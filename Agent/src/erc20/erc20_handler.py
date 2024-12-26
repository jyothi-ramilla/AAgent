import time
from web3 import Web3

class ERC20Handler:
    def __init__(self, contract_address, private_key, source_address, target_address, nonce_manager, web3_instance, chain_id):
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
        self.web3_instance = web3_instance
        self.chain_id = chain_id

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
                'gasPrice': self.web3_instance.eth.gas_price,
                'chainId': self.chain_id
            })

            # Estimate gas and set it
            gas = self.web3_instance.eth.estimate_gas(tx)
            tx['gas'] = int(gas * 1.2)  # Add 20% buffer

            # Sign and send the transaction
            signed_tx = self.account.sign_transaction(tx)
            tx_hash = self.web3_instance.eth.send_raw_transaction(signed_tx.raw_transaction)
            return tx_hash.hex()
        except Exception as e:
            if "nonce too low" in str(e):
                return self.execute_transfer(amount)
            raise

