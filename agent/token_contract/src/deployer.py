import os
import logging
from web3 import Web3
import solcx
from web3.exceptions import ContractLogicError

logger = logging.getLogger(__name__)

class EthereumDeployer:
    """Class to handle Ethereum contract deployment using Web3."""

    def __init__(self, rpc_url, private_key):
        self.rpc_url = rpc_url
        self.private_key = private_key
        self.web3_instance = None
        self.account = None
        self.contract_abi = None
        self.contract_bytecode = None
        self.contract_address = None

    def connect_to_network(self):
        """Establish a connection to the Ethereum network."""
        self.web3_instance = Web3(Web3.HTTPProvider(self.rpc_url))
        if not self.web3_instance.is_connected():
            logger.error("Failed to connect to the Ethereum network.")
            raise ConnectionError("Could not establish a connection to the Ethereum network.")
        logger.info("Successfully connected to Ethereum network.")

    def install_solidity_compiler(self):
        """Install the latest version of the Solidity compiler (solc)."""
        try:
            solcx.install_solc('latest')
            logger.info("Solidity compiler (solc) installed successfully.")
        except Exception as e:
            logger.error(f"Failed to install Solidity compiler: {e}")
            raise e

    def compile_contract(self, contract_path):
        """Compile the Solidity smart contract and save ABI and bytecode to artifacts folder."""
        try:
            with open(contract_path, 'r') as file:
                contract_source_code = file.read()

            self.install_solidity_compiler()

            # Extract contract name dynamically from the Solidity file name
            contract_name = os.path.splitext(os.path.basename(contract_path))[0]

            compiled_contract = solcx.compile_standard({
                "language": "Solidity",
                "sources": {
                    contract_name + ".sol": {
                        "content": contract_source_code
                    }
                },
                "settings": {
                    "outputSelection": {
                        "*": {
                            "*": ["abi", "evm.bytecode"]
                        }
                    }
                }
            })

            # Get ABI and Bytecode dynamically based on the contract name
            self.contract_abi = compiled_contract['contracts'][contract_name + ".sol"][contract_name]['abi']
            self.contract_bytecode = compiled_contract['contracts'][contract_name + ".sol"][contract_name]['evm']['bytecode']['object']
            logger.info("Contract compiled successfully.")

            # Save ABI and Bytecode in the artifacts folder
            artifacts_folder = os.path.join(os.path.dirname(contract_path), 'artifacts')
            os.makedirs(artifacts_folder, exist_ok=True)

            abi_path = os.path.join(artifacts_folder, f'{contract_name}_abi.json')
            bytecode_path = os.path.join(artifacts_folder, f'{contract_name}_bytecode.json')

            with open(abi_path, 'w') as abi_file:
                abi_file.write(Web3.to_json(self.contract_abi))
            with open(bytecode_path, 'w') as bytecode_file:
                bytecode_file.write(Web3.to_json({"bytecode": self.contract_bytecode}))

            logger.info(f"ABI and bytecode saved to {artifacts_folder}.")
        except Exception as e:
            logger.error(f"Error during contract compilation: {e}")
            raise e

    def prepare_account(self):
        """Prepare account object from private key."""
        if not self.private_key.startswith('0x'):
            logger.info("Private key does not start with '0x'. Adding it.")
            self.private_key = '0x' + self.private_key

        self.account = self.web3_instance.eth.account.from_key(self.private_key)
        logger.info(f"Account address: {self.account.address}")

    def deploy_contract(self, initial_supply):
        """Deploy the compiled smart contract to the Ethereum network."""
        try:
            nonce = self.web3_instance.eth.get_transaction_count(self.account.address)

            # Build the contract deployment transaction
            contract = self.web3_instance.eth.contract(abi=self.contract_abi, bytecode=self.contract_bytecode)
            transaction = contract.constructor(initial_supply).build_transaction({
                'gas': 2000000,
                'gasPrice': self.web3_instance.to_wei('10', 'gwei'),
                'nonce': nonce,
            })

            # Sign the transaction with the private key
            signed_transaction = self.web3_instance.eth.account.sign_transaction(transaction, self.private_key)

            # Send the signed transaction to the network
            tx_hash = self.web3_instance.eth.send_raw_transaction(signed_transaction.raw_transaction)
            logger.info(f"Transaction sent. Hash: {tx_hash.hex()}")

            # Wait for the transaction receipt and get the contract address
            tx_receipt = self.web3_instance.eth.wait_for_transaction_receipt(tx_hash)
            self.contract_address = tx_receipt['contractAddress']
            logger.info(f"Smart contract deployed at address: {self.contract_address}")
        except ContractLogicError as e:
            logger.error(f"Contract deployment failed due to a logic error: {e}")
            raise e
        except Exception as e:
            logger.error(f"Error during contract deployment: {e}")
            raise e

    def get_contract_address(self):
        """Return the deployed contract address."""
        return self.contract_address
