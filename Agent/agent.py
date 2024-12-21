import time
import random
import logging
from threading import Thread, Lock
from web3 import Web3
import os

# Configure logging for the script
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create a console handler to print logs to stdout
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Define the log message format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Add the console handler to the logger
logger.addHandler(console_handler)

# Function to load .env file into os.environ
def load_env(file_path=".env"):
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            for line in file:
                # Ignore comments and blank lines
                line = line.strip()
                if line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()

# Load environment variables from .env file
load_env()

# Constants from environment variables
ETH_RPC_URL = os.getenv("ETH_RPC_URL")
SOURCE_ADDRESS = os.getenv("SOURCE_ADDRESS")
TARGET_ADDRESS = os.getenv("TARGET_ADDRESS")
ERC20_CONTRACT_ADDRESS = os.getenv("ERC20_CONTRACT_ADDRESS")
WORDS = ["hello", "sun", "world", "space", "moon", "crypto", "sky", "ocean", "universe", "human"]
CHAIN_ID = int(os.getenv("CHAIN_ID", 123456))

# Load private keys (ensure these are set in environment variables)
SOURCE_PRIVATE_KEY = os.getenv("SOURCE_PRIVATE_KEY")
TARGET_PRIVATE_KEY = os.getenv("TARGET_PRIVATE_KEY")

# Raise an error if private keys are not set
if not SOURCE_PRIVATE_KEY or not TARGET_PRIVATE_KEY:
    raise ValueError("SOURCE_PRIVATE_KEY and TARGET_PRIVATE_KEY environment variables must be set.")

# Web3 Setup: Establish a connection to the Ethereum network
web3_instance = Web3(Web3.HTTPProvider(ETH_RPC_URL))
if not web3_instance.is_connected():
    logger.error("Web3 failed to connect to the Ethereum RPC URL.")
    raise ConnectionError("Web3 connection failed.")

logger.info("Web3 is successfully connected to the Ethereum network.")

# Inbox class for storing and retrieving messages
class Inbox:
    def __init__(self):
        self.messages = []

    def add_message(self, message):
        """Add a message to the inbox."""
        self.messages.append(message)

    def get_messages(self):
        """Retrieve and clear all messages in the inbox."""
        messages = self.messages[:]
        self.messages.clear()
        return messages

# Outbox class for sending messages to another agent's inbox
class Outbox:
    def __init__(self, inbox):
        self.inbox = inbox

    def send_message(self, message):
        """Send a message to the given inbox."""
        self.inbox.add_message(message)

# NonceManager class to handle Ethereum transaction order and nonce management
class NonceManager:
    def __init__(self, address):
        self.address = Web3.to_checksum_address(address)
        self.lock = Lock()

    def get_nonce(self):
        """Retrieve the current transaction count (nonce) for the address."""
        with self.lock:
            nonce = web3_instance.eth.get_transaction_count(self.address)
            return nonce

# ERC20Handler class for interacting with ERC20 tokens (balance, transfer)
class ERC20Handler:
    def __init__(self, contract_address, private_key, source_address, target_address, nonce_manager):
        self.contract_address = Web3.to_checksum_address(contract_address)
        self.private_key = private_key
        self.account = web3_instance.eth.account.from_key(private_key)
        self.address = self.account.address
        self.source_address = Web3.to_checksum_address(source_address)
        self.target_address = Web3.to_checksum_address(target_address)
        self.nonce_manager = nonce_manager
        self.contract = web3_instance.eth.contract(
            address=self.contract_address, abi=self._get_standard_erc20_abi()
        )

    @staticmethod
    def _get_standard_erc20_abi():
        """Returns a basic ERC20 token ABI for interacting with transfer and balance functions."""
        return [
            {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "type": "function"},
            {"constant": True, "inputs": [{"name": "_owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "balance", "type": "uint256"}], "type": "function"},
            {"constant": False, "inputs": [{"name": "_to", "type": "address"}, {"name": "_value", "type": "uint256"}], "name": "transfer", "outputs": [{"name": "", "type": "bool"}], "type": "function"}
        ]

    def fetch_balance(self):
        """Fetch and log the balance of ERC20 tokens for the source address."""
        balance = self.contract.functions.balanceOf(self.source_address).call()
        logger.info(f"Balance fetched for {self.address}: {balance} tokens")
        return balance

    def execute_transfer(self, amount):
        """Execute an ERC20 token transfer from source to target address."""
        try:
            nonce = self.nonce_manager.get_nonce()
            time.sleep(0.1)  # Small delay to avoid nonce issues

            # Build the transaction for transfer
            transfer_function = self.contract.functions.transfer(self.target_address, amount)
            tx = transfer_function.build_transaction({
                'from': self.address,
                'nonce': nonce,
                'gasPrice': web3_instance.eth.gas_price,
                'chainId': CHAIN_ID
            })

            # Estimate gas and set it
            gas = web3_instance.eth.estimate_gas(tx)
            tx['gas'] = int(gas * 1.2)  # Add 20% buffer

            # Sign and send the transaction
            signed_tx = self.account.sign_transaction(tx)
            tx_hash = web3_instance.eth.send_raw_transaction(signed_tx.raw_transaction)
            logger.info(f"Transfer from {self.address} successful, transaction hash: {tx_hash.hex()}")
            return tx_hash.hex()
        except Exception as e:
            logger.error(f"Error during token transfer from {self.address}: {e}")
            if "nonce too low" in str(e):
                logger.warning("Nonce too low, retrying...")
                return self.execute_transfer(amount)
            raise

# AutonomousAgent class that handles message processing and interacting with other agents
class AutonomousAgent(Thread):
    def __init__(self, name, inbox, outbox, erc20_handler):
        super().__init__()
        self.name = name
        self.inbox = inbox
        self.outbox = outbox
        self.erc20_handler = erc20_handler
        self.message_handlers = {}
        self.running = True

    def run(self):
        """Start the agent and process messages continuously."""
        logger.info(f"[{self.name}] Agent started.")
        while self.running:
            self.process_messages()
            time.sleep(1)

    def stop(self):
        """Stop the agent from processing messages."""
        logger.info(f"[{self.name}] Agent stopping.")
        self.running = False

    def register_message_handler(self, message_type, handler):
        """Registers a handler function for a given message type."""
        self.message_handlers[message_type] = handler

    def process_messages(self):
        """Process and handle messages from the inbox."""
        for message in self.inbox.get_messages():
            for message_type, handler in self.message_handlers.items():
                if message_type in message:
                    logger.info(f"[{self.name}] Handling message with {message_type}: {message}")
                    handler(message)

    def generate_random_messages(self):
        """Generate and send random messages periodically."""
        while self.running:
            word1, word2 = random.choices(WORDS, k=2)
            self.outbox.send_message(f"{word1} {word2}")
            logger.info(f"[{self.name}] Sent random message: {word1} {word2}")
            time.sleep(2)

    def check_balance_periodically(self):
        """Check and log balance periodically."""
        while self.running:
            balance = self.erc20_handler.fetch_balance()
            logger.info(f"[{self.name}] Current ERC20 balance: {balance}")
            time.sleep(10)

if __name__ == "__main__":
    # Ensure environment variables are loaded
    source_private_key = os.getenv("SOURCE_PRIVATE_KEY")
    target_private_key = os.getenv("TARGET_PRIVATE_KEY")

    # Raise an error if private keys are missing
    if not source_private_key or not target_private_key:
        raise ValueError("SOURCE_PRIVATE_KEY and TARGET_PRIVATE_KEY environment variables must be set.")

    # Create inbox and outbox for both agents
    inbox1, inbox2 = Inbox(), Inbox()
    outbox1, outbox2 = Outbox(inbox2), Outbox(inbox1)

    # Nonce managers for both agents
    nonce_manager1 = NonceManager(SOURCE_ADDRESS)
    nonce_manager2 = NonceManager(TARGET_ADDRESS)

    # ERC20 handlers for both agents
    erc20_handler1 = ERC20Handler(ERC20_CONTRACT_ADDRESS, source_private_key, SOURCE_ADDRESS, TARGET_ADDRESS, nonce_manager1)
    erc20_handler2 = ERC20Handler(ERC20_CONTRACT_ADDRESS, target_private_key, TARGET_ADDRESS, SOURCE_ADDRESS, nonce_manager2)

    # Create agents
    agent1 = AutonomousAgent("Agent1", inbox1, outbox1, erc20_handler1)
    agent2 = AutonomousAgent("Agent2", inbox2, outbox2, erc20_handler2)

    # Register message handlers
    agent1.register_message_handler("hello", lambda message: logger.info(f"[Agent1] Received hello message: {message}"))
    agent2.register_message_handler("crypto", lambda message: logger.info(f"[Agent2] Received crypto message: {message}"))

    # Start agents
    agent1.start()
    agent2.start()

    # Run background tasks for agents
    Thread(target=agent1.generate_random_messages).start()
    Thread(target=agent2.generate_random_messages).start()
    Thread(target=agent1.check_balance_periodically).start()
    Thread(target=agent2.check_balance_periodically).start()

    # Let the script run indefinitely
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down agents.")
        agent1.stop()
        agent2.stop()
