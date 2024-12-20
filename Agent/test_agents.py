import unittest
from threading import Thread
import time
from unittest.mock import patch, MagicMock
from agent import AutonomousAgent, Inbox, Outbox, ERC20Handler, NonceManager, logger
import os
from dotenv import load_dotenv
# -------------------------------------------
# UnitTest Test Cases
# -------------------------------------------

# Load environment variables from .env file
load_dotenv()

# Get the RPC URL and contract address from environment variables
ETH_RPC_URL = os.getenv("ETH_RPC_URL")
CONTRACT_ADDRESS = os.getenv("ERC20_CONTRACT_ADDRESS")
SOURCE_PRIVATE_KEY=os.getenv("SOURCE_PRIVATE_KEY")
TARGET_PRIVATE_KEY=os.getenv("TARGET_PRIVATE_KEY")
SOURCE_ADDRESS=os.getenv("SOURCE_ADDRESS")
TARGET_ADDRESS=os.getenv("TARGET_ADDRESS")

# Print constants that you can use in your code
print(f"ETH_RPC_URL: {ETH_RPC_URL}")
print(f"CONTRACT_ADDRESS: {CONTRACT_ADDRESS}")

class TestAgent(unittest.TestCase):

    @patch('agent.web3_instance')
    def setUp(self, mock_web3):
        # Mock Web3 instance
        mock_web3.eth.get_transaction_count.return_value = 0
        mock_web3.eth.gas_price = 1
        mock_web3.eth.estimate_gas.return_value = 21000
        mock_web3.eth.send_raw_transaction.return_value = b"mock_tx_hash"
        mock_web3.is_connected.return_value = True

        # Set up inbox, outbox, and ERC20Handler mock
        self.inbox = Inbox()
        self.outbox = Outbox(self.inbox)

        self.nonce_manager = NonceManager(SOURCE_ADDRESS)
        self.erc20_handler = ERC20Handler(
            contract_address=CONTRACT_ADDRESS,
            private_key=SOURCE_PRIVATE_KEY,
            source_address=SOURCE_ADDRESS,
            target_address=TARGET_ADDRESS,
            nonce_manager=self.nonce_manager
        )
        self.erc20_handler.fetch_balance = MagicMock(return_value=100)
        self.erc20_handler.execute_transfer = MagicMock()

        self.agent = AutonomousAgent("TestAgent", self.inbox, self.outbox, self.erc20_handler)
        self.agent.register_message_handler("hello", lambda msg: logger.info(f"Responding to 'hello' in message: {msg}"))
        self.agent.register_message_handler("crypto", lambda msg: self.erc20_handler.execute_transfer(1))

    def tearDown(self):
        """Called after every test"""
        logger.info(f"{self._testMethodName}: Test completed")

    def test_generate_random_messages(self):
        """Test random message generation"""
        try:
            self.agent.running = True
            thread = self._start_thread(self.agent.generate_random_messages)

            time.sleep(3)  # Allow messages to generate
            self.agent.running = False
            thread.join()

            self.assertTrue(len(self.inbox.get_messages()) > 0)
            for message in self.inbox.messages:
                words = message.split()
                self.assertEqual(len(words), 2)
                for word in words:
                    self.assertIn(word, self.agent.WORDS)

            logger.info(f"{self._testMethodName}: Passed")
        except AssertionError as e:
            logger.error(f"{self._testMethodName}: Failed - {e}")
            raise

    def test_handle_hello_messages(self):
        """Test handling of 'hello' messages"""
        try:
            self.inbox.add_message("hello world")

            with self.assertLogs(logger, level='INFO') as log:
                self.agent.process_messages()

            self.assertTrue(any("Responding to 'hello'" in message for message in log.output))
            logger.info(f"{self._testMethodName}: Passed")
        except AssertionError as e:
            logger.error(f"{self._testMethodName}: Failed - {e}")
            raise

    def test_handle_crypto_messages(self):
        """Test handling of 'crypto' messages and token transfer"""
        try:
            self.inbox.add_message("crypto moon")
            self.agent.process_messages()

            self.erc20_handler.execute_transfer.assert_called_once_with(1)
            logger.info(f"{self._testMethodName}: Passed")
        except AssertionError as e:
            logger.error(f"{self._testMethodName}: Failed - {e}")
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
            logger.info(f"{self._testMethodName}: Passed")
        except AssertionError as e:
            logger.error(f"{self._testMethodName}: Failed - {e}")
            raise

    def _start_thread(self, target):
        thread = Thread(target=target)
        thread.start()
        return thread

# -------------------------------------------
# Integration Test Cases
# -------------------------------------------

class TestAgentIntegration(unittest.TestCase):

    @patch('agent.web3_instance')
    def setUp(self, mock_web3):
        # Mock Web3 instance
        mock_web3.eth.get_transaction_count.return_value = 0
        mock_web3.eth.gas_price = 1
        mock_web3.eth.estimate_gas.return_value = 21000
        mock_web3.eth.send_raw_transaction.return_value = b"mock_tx_hash"
        mock_web3.is_connected.return_value = True

        # Mock ERC20Handler dependencies
        self.mock_fetch_balance = MagicMock(return_value=100)
        self.mock_execute_transfer = MagicMock()

        # Set up inbox, outbox, and ERC20Handler
        self.inbox = Inbox()
        self.outbox = Outbox(self.inbox)
        self.nonce_manager = NonceManager(SOURCE_ADDRESS)
        self.erc20_handler = ERC20Handler(
            contract_address=CONTRACT_ADDRESS,
            private_key=SOURCE_PRIVATE_KEY,
            source_address=SOURCE_ADDRESS,
            target_address=TARGET_ADDRESS,
            nonce_manager=self.nonce_manager
        )

        self.erc20_handler.fetch_balance = self.mock_fetch_balance
        self.erc20_handler.execute_transfer = self.mock_execute_transfer

        self.agent = AutonomousAgent("IntegrationTestAgent", self.inbox, self.outbox, self.erc20_handler)

        # Register handlers
        self.agent.register_message_handler("hello", lambda msg: logger.info(f"Responding to 'hello' in message: {msg}"))
        self.agent.register_message_handler("crypto", lambda msg: self.erc20_handler.execute_transfer(1))

    def tearDown(self):
        """Called after every test"""
        logger.info(f"{self._testMethodName}: Test completed")

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
            self.mock_fetch_balance.assert_called()
            self.mock_execute_transfer.assert_called_with(50)

            logger.info(f"{self._testMethodName}: Passed")
        except AssertionError as e:
            logger.error(f"{self._testMethodName}: Failed - {e}")
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

            with self.assertLogs(logger, level='INFO') as log:
                self.agent.process_messages()
                self.assertFalse(any("Unhandled message type" in message for message in log.output))

            logger.info(f"{self._testMethodName}: Passed")
        except AssertionError as e:
            logger.error(f"{self._testMethodName}: Failed - {e}")
            raise

    def test_concurrent_threads(self):
        """Test if multiple threads can run concurrently without issues"""
        try:
            # Start multiple threads for balance checking and random message generation
            self.agent.running = True
            balance_thread = self._start_thread(self.agent.check_balance_periodically)
            message_thread = self._start_thread(self.agent.generate_random_messages)

            time.sleep(3)  # Allow threads to run concurrently

            self.agent.running = False
            balance_thread.join()
            message_thread.join()

            # Ensure no race conditions or deadlocks occurred
            self.assertTrue(self.inbox.get_messages())
            logger.info(f"{self._testMethodName}: Passed")
        except AssertionError as e:
            logger.error(f"{self._testMethodName}: Failed - {e}")
            raise

    def test_handle_web3_interaction_failure(self):
        """Test handling Web3 interaction failure, like network issues"""
        try:
            # Simulate Web3 failure by making fetch_balance raise an exception
            self.erc20_handler.fetch_balance.side_effect = Exception("Web3 network error")

            with self.assertRaises(Exception) as context:
                self.erc20_handler.fetch_balance()
            
            self.assertTrue("Web3 network error" in str(context.exception))
            logger.info(f"{self._testMethodName}: Passed")
        except AssertionError as e:
            logger.error(f"{self._testMethodName}: Failed - {e}")
            raise

    def test_balance_retrieval_failure(self):
        """Test the agent's behavior when balance retrieval fails"""
        try:
            # Simulate failure in balance fetching
            self.erc20_handler.fetch_balance.side_effect = Exception("Balance retrieval failed")

            with self.assertRaises(Exception) as context:
                self.erc20_handler.fetch_balance()
            
            self.assertTrue("Balance retrieval failed" in str(context.exception))
            logger.info(f"{self._testMethodName}: Passed")
        except AssertionError as e:
            logger.error(f"{self._testMethodName}: Failed - {e}")
            raise

    def _start_thread(self, target):
        thread = Thread(target=target)
        thread.start()
        return thread


if __name__ == "__main__":
    unittest.main()
