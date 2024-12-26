import random
import time
import threading

class AutonomousAgent(threading.Thread):
    def __init__(self, name, inbox, outbox, erc20_handler,logger):
        super().__init__()
        self.name = name
        self.inbox = inbox
        self.outbox = outbox
        self.erc20_handler = erc20_handler
        self.logger = logger
        self.message_handlers = {}
        self.running = True

    def run(self):
        """Start the agent and process messages continuously."""
        self.logger.info(f"[{self.name}] Agent started.")
        while self.running:
            self.process_messages()
            time.sleep(1)

    def stop(self):
        """Stop the agent from processing messages."""
        self.logger.info(f"[{self.name}] Agent stopping.")
        self.running = False

    def register_message_handler(self, message_type, handler):
        """Registers a handler function for a given message type."""
        self.message_handlers[message_type] = handler

    def process_messages(self):
        """Process and handle messages from the inbox."""
        for message in self.inbox.get_messages():
            for message_type, handler in self.message_handlers.items():
                if message_type in message:
                    self.logger.info(f"[{self.name}] Handling message with {message_type}: {message}")
                    handler(message)

    def generate_random_messages(self, words):
        """Generate and send random messages periodically."""
        while self.running:
            word1, word2 = random.choices(words, k=2)
            self.outbox.send_message(f"{word1} {word2}")
            self.logger.info(f"[{self.name}] Sent random message: {word1} {word2}")
            time.sleep(2)

    def check_balance_periodically(self):
        """Check and log balance periodically."""
        while self.running:
            balance = self.erc20_handler.fetch_balance()
            self.logger.info(f"[{self.name}] Current ERC20 balance: {balance}")
            time.sleep(10)
