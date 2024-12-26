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
# Integration Test Cases
# -------------------------------------------

class TestAgentIntegration(unittest.TestCase):

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

        self.agent = AutonomousAgent("IntegrationTestAgent", self.inbox, self.outbox, self.erc20_handler, self.logger)

        # Register message handlers
        self.agent.register_message_handler("hello", lambda msg: self.logger.info(f"Responding to 'hello' in message: {msg}"))
        self.agent.register_message_handler("crypto", lambda msg: self.erc20_handler.execute_transfer(1))
        # Define WORDS list for testing
        self.agent.WORDS = ["hello", "sun", "world", "space", "moon", "crypto", "sky", "ocean", "universe", "human"]
        self.logger = setup_logger() 

    def tearDown(self):
        """Called after every test"""
        self.logger.info(f"{self._testMethodName}: Test completed")

    def test_balance_check_and_transfer(self):
        """Test if balance is checked periodically and transfer happens"""
        try:
            self.agent.running = True
            balance_thread = self._start_thread(self.agent.check_balance_periodically)

            # Simulate balance fetching and transfer
            self.erc20_handler.fetch_balance.return_value = 100  # Mock balance
            self.agent.process_messages()
            self.erc20_handler.execute_transfer(50)

            time.sleep(3)  # Allow periodic tasks to execute

            # Ensure balance was fetched and transfer occurred
            self.erc20_handler.fetch_balance.assert_called()
            self.erc20_handler.execute_transfer.assert_called_with(50)

            self.logger.info(f"{self._testMethodName}: Passed")
        except AssertionError as e:
            self.logger.error(f"{self._testMethodName}: Failed - {e}")
            raise
        finally:
            self.agent.running = False
            balance_thread.join()

    def test_resilience_to_invalid_messages(self):
        """Test agent handling invalid messages without crashing"""
        try:
            # Simulate invalid messages
            self.inbox.add_message("unknown command")
            self.inbox.add_message("hellohello")

            with self.assertLogs(self.logger, level='INFO') as log:
                self.agent.process_messages()
                self.assertFalse(any("Unhandled message type" in message for message in log.output))

            self.logger.info(f"{self._testMethodName}: Passed")
        except AssertionError as e:
            self.logger.error(f"{self._testMethodName}: Failed - {e}")
            raise


    def test_concurrent_threads(self):
        """Test if multiple threads can run concurrently without issues"""
        try:
            # Start multiple threads for balance checking and random message generation
            self.agent.running = True
            balance_thread = self._start_thread(self.agent.check_balance_periodically)
            message_thread = self._start_thread(self.agent.generate_random_messages, self.agent.WORDS)        
            time.sleep(3)  # Allow threads to run concurrently

            self.agent.running = False
            balance_thread.join()
            message_thread.join()

            # Ensure no race conditions or deadlocks occurred
            self.assertTrue(self.inbox.get_messages())
            self.logger.info(f"{self._testMethodName}: Passed")
        except AssertionError as e:
            self.logger.error(f"{self._testMethodName}: Failed - {e}")
            raise

    def test_handle_web3_interaction_failure(self):
        """Test handling Web3 interaction failure, like network issues"""
        try:
            # Simulate Web3 failure by making fetch_balance raise an exception
            self.erc20_handler.fetch_balance.side_effect = Exception("Web3 network error")

            with self.assertRaises(Exception) as context:
                self.erc20_handler.fetch_balance()
            
            self.assertTrue("Web3 network error" in str(context.exception))
            self.logger.info(f"{self._testMethodName}: Passed")
        except AssertionError as e:
            self.logger.error(f"{self._testMethodName}: Failed - {e}")
            raise

    def test_balance_retrieval_failure(self):
        """Test the agent's behavior when balance retrieval fails"""
        try:
            # Simulate failure in balance fetching
            self.erc20_handler.fetch_balance.side_effect = Exception("Balance retrieval failed")

            with self.assertRaises(Exception) as context:
                self.erc20_handler.fetch_balance()
            
            self.assertTrue("Balance retrieval failed" in str(context.exception))
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

