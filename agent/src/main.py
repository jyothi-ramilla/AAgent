import os
import time
from threading import Thread
from utils.env_loader import load_env
from erc20.nonce_manager import NonceManager
from erc20.erc20_handler import ERC20Handler
from agents.inbox import Inbox
from agents.outbox import Outbox
from agents.autonomous_agent import AutonomousAgent
from utils.logging_utils import setup_logger
from web3 import Web3

# Set up logging
logger = setup_logger()

# Load environment variables
load_env()

def create_web3_instance():
    """Create and return a Web3 instance connected to the Ethereum network."""
    eth_rpc_url = os.getenv("ETH_RPC_URL")
    web3_instance = Web3(Web3.HTTPProvider(eth_rpc_url))
    if not web3_instance.is_connected():
        raise ConnectionError("Web3 connection failed.")
    return web3_instance

def create_erc20_handler(contract_address, private_key, source_address, target_address, nonce_manager, web3_instance, chain_id):
    """Create and return an ERC20Handler instance."""
    return ERC20Handler(
        contract_address, private_key, source_address, target_address, 
        nonce_manager, web3_instance, chain_id
    )

def create_nonce_manager(address, web3_instance):
    """Create and return a NonceManager instance."""
    return NonceManager(address, web3_instance)

def create_agent(name, inbox, outbox, erc20_handler,logger):
    """Create and return an AutonomousAgent instance."""
    return AutonomousAgent(name, inbox, outbox, erc20_handler,logger)

def main():
    
    # Define WORDS list
    WORDS = ["hello", "sun", "world", "space", "moon", "crypto", "sky", "ocean", "universe", "human"]

    # Initialize Web3 and set up variables
    web3_instance = create_web3_instance()
    chain_id = int(os.getenv("CHAIN_ID", 123456))
    
    # Nonce managers for both agents
    nonce_manager1 = create_nonce_manager(os.getenv("SOURCE_ADDRESS"), web3_instance)
    nonce_manager2 = create_nonce_manager(os.getenv("TARGET_ADDRESS"), web3_instance)

    # ERC20 handlers for both agents
    erc20_handler1 = create_erc20_handler(
        os.getenv("ERC20_CONTRACT_ADDRESS"), os.getenv("SOURCE_PRIVATE_KEY"),
        os.getenv("SOURCE_ADDRESS"), os.getenv("TARGET_ADDRESS"),
        nonce_manager1, web3_instance, chain_id
    )
    erc20_handler2 = create_erc20_handler(
        os.getenv("ERC20_CONTRACT_ADDRESS"), os.getenv("TARGET_PRIVATE_KEY"),
        os.getenv("TARGET_ADDRESS"), os.getenv("SOURCE_ADDRESS"),
        nonce_manager2, web3_instance, chain_id
    )

    # Create inbox and outbox for both agents
    inbox1, inbox2 = Inbox(), Inbox()
    outbox1, outbox2 = Outbox(inbox2), Outbox(inbox1)

    # Create agents
    agent1 = create_agent("Agent1", inbox1, outbox1, erc20_handler1,logger)
    agent2 = create_agent("Agent2", inbox2, outbox2, erc20_handler2,logger)

    # Register message handlers
    agent1.register_message_handler("hello", lambda message: logger.info(f"[Agent1] Received hello message: {message}"))
    agent2.register_message_handler("crypto", lambda message: logger.info(f"[Agent2] Received crypto message: {message}"))

    # Start agents
    agent1.start()
    agent2.start()

    # Run background tasks for agents
    Thread(target=agent1.generate_random_messages, args=(WORDS,)).start()
    Thread(target=agent2.generate_random_messages, args=(WORDS,)).start()
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

if __name__ == "__main__":
    main()
