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
