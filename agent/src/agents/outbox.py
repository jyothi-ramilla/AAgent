class Outbox:
    def __init__(self, inbox):
        self.inbox = inbox

    def send_message(self, message):
        """Send a message to the given inbox."""
        self.inbox.add_message(message)
