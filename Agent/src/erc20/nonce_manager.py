from threading import Lock
from web3 import Web3

class NonceManager:
    """Manages transaction nonces for an Ethereum address."""
    def __init__(self, address, web3_instance):
        self.address = Web3.to_checksum_address(address)
        self.lock = Lock()
        self.web3_instance = web3_instance

    def get_nonce(self):
        """Safely fetches the current nonce."""
        with self.lock:
            return self.web3_instance.eth.get_transaction_count(self.address)

