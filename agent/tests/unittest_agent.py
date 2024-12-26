import unittest
from threading import Thread
import time
from unittest.mock import patch, MagicMock
from src.agents.autonomous_agent import AutonomousAgent
from src.agents.inbox import Inbox
from src.agents.outbox import Outbox
from src.erc20.erc20_handler import ERC20Handler
from src.erc20.nonce_manager import NonceManager
from src.utils.logging_utils import setup_logger
from src.utils.env_loader import load_env
import os

# Load environment variables from .env file
load_env()

# Get the RPC URL and contract address from environment variables
ETH_RPC_URL = os.getenv("ETH_RPC_URL")
CONTRACT_ADDRESS = os.getenv("ERC20_CONTRACT_ADDRESS")
SOURCE_PRIVATE_KEY = os.getenv("SOURCE_PRIVATE_KEY")
TARGET_PRIVATE_KEY = os.getenv("TARGET_PRIVATE_KEY")
SOURCE_ADDRESS = os.getenv("SOURCE_ADDRESS")
TARGET_ADDRESS = os.getenv("TARGET_ADDRESS")

# -------------------------------------------
# UnitTest Test Cases
# -------------------------------------------

class TestAgent(unittest.TestCase):

    @patch('web3.Web3')
    def setUp(self, mock_web3):
        # Mock Web3 instance
        mock_web3.is_connected.return_value = True
        mock_web3.eth.get_transaction_count.return_value = 0
        mock_web3.eth.gas_price = 1
        mock_web3.eth.estimate_gas.return_value = 21000
        mock_web3.eth.send_raw_transaction.return_value = b"mock_tx_hash"

        # Set up inbox, outbox, and ERC20Handler mock
        self.inbox = Inbox()
        self.outbox = Outbox(self.inbox)

        # Mock NonceManager and ERC20Handler
        self.nonce_manager = NonceManager(SOURCE_ADDRESS, mock_web3)
        self.erc20_handler = ERC20Handler(
            contract_address=CONTRACT_ADDRESS,
            private_key=SOURCE_PRIVATE_KEY,
            source_address=SOURCE_ADDRESS,
            target_address=TARGET_ADDRESS,
            nonce_manager=self.nonce_manager,
            web3_instance=mock_web3,
            chain_id=int(os.getenv("CHAIN_ID", 123456))
        )
        self.erc20_handler.fetch_balance = MagicMock(return_value=100)
        self.erc20_handler.execute_transfer = MagicMock()

        self.logger = setup_logger() 

        self.agent = AutonomousAgent("TestAgent", self.inbox, self.outbox, self.erc20_handler, self.logger)

        # Register message handlers
        self.agent.register_message_handler("hello", lambda msg: self.logger.info(f"Responding to 'hello' in message: {msg}"))
        self.agent.register_message_handler("crypto", lambda msg: self.erc20_handler.execute_transfer(1))

        # Define WORDS list for testing
        self.agent.WORDS = ["hello", "sun", "world", "space", "moon", "crypto", "sky", "ocean", "universe", "human"]



    def tearDown(self):
        """Called after every test"""
        self.logger.info(f"{self._testMethodName}: Test completed")

    def test_generate_random_messages(self):
        """Test random message generation"""
        try:
            self.agent.running = True
            thread = self._start_thread(self.agent.generate_random_messages, self.agent.WORDS)
            #thread = self._start_thread(self.agent.generate_random_messages, args=(self.agent.WORDS,))

            time.sleep(3)  # Allow messages to generate
            self.agent.running = False
            thread.join()

            self.assertTrue(len(self.inbox.get_messages()) > 0)
            for message in self.inbox.messages:
                words = message.split()
                self.assertEqual(len(words), 2)
                for word in words:
                    self.assertIn(word, self.agent.WORDS)

            self.logger.info(f"{self._testMethodName}: Passed")
        except AssertionError as e:
            self.logger.error(f"{self._testMethodName}: Failed - {e}")
            raise


    def test_handle_hello_messages(self):
        """Test handling of 'hello' messages"""
        try:
            self.inbox.add_message("hello world")

            with self.assertLogs(self.logger, level='INFO') as log:
                self.agent.process_messages()

            self.assertTrue(any("Responding to 'hello'" in message for message in log.output))
            self.logger.info(f"{self._testMethodName}: Passed")
        except AssertionError as e:
            self.logger.error(f"{self._testMethodName}: Failed - {e}")
            raise

    def test_handle_crypto_messages(self):
        """Test handling of 'crypto' messages and token transfer"""
        try:
            self.inbox.add_message("crypto moon")
            self.agent.process_messages()

            self.erc20_handler.execute_transfer.assert_called_once_with(1)
            self.logger.info(f"{self._testMethodName}: Passed")
        except AssertionError as e:
            self.logger.error(f"{self._testMethodName}: Failed - {e}")
            raise

    def test_check_balance_periodically(self):
        """Test periodic balance checking"""
        try:
            self.agent.running = True
            thread = self._start_thread(self.agent.check_balance_periodically)

            time.sleep(3)  # Allow balance checks to occur
            self.agent.running = False
            thread.join()

            self.erc20_handler.fetch_balance.assert_called()
            self.logger.info(f"{self._testMethodName}: Passed")
        except AssertionError as e:
            self.logger.error(f"{self._testMethodName}: Failed - {e}")
            raise

    def _start_thread(self, target, *args):
        thread = Thread(target=target, args=args)
        thread.start()
        return thread

if __name__ == "__main__":
    unittest.main()
