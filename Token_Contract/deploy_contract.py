import os
import logging
from web3 import Web3
from dotenv import load_dotenv
import solcx
from web3.exceptions import ContractLogicError

# Configure logging settings
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

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

    def _fetch_env_variable(self, variable_name):
        """Fetch environment variables with error handling."""
        value = os.getenv(variable_name)
        if not value:
            logger.error(f"Environment variable '{variable_name}' is missing.")
            raise EnvironmentError(f"{variable_name} not set in environment variables.")
        return value

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
        """Compile the Solidity smart contract and return ABI and bytecode."""
        try:
            with open(contract_path, 'r') as file:
                contract_source_code = file.read()

            self.install_solidity_compiler()

            compiled_contract = solcx.compile_standard({
                "language": "Solidity",
                "sources": {
                    "AgentToken.sol": {
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

            self.contract_abi = compiled_contract['contracts']['AgentToken.sol']['AgentToken']['abi']
            self.contract_bytecode = compiled_contract['contracts']['AgentToken.sol']['AgentToken']['evm']['bytecode']['object']
            logger.info("Contract compiled successfully.")
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

class DeploymentManager:
    """Class to manage the deployment of a contract."""
    
    def __init__(self, contract_path, rpc_url, private_key):
        self.contract_path = contract_path
        self.rpc_url = rpc_url
        self.private_key = private_key
        self.deploy = EthereumDeployer(self.rpc_url, self.private_key)

    def execute_deployment(self):
        """Execute the full contract deployment process."""
        try:
            # Connect to the Ethereum network
            self.deploy.connect_to_network()

            # Compile the smart contract
            self.deploy.compile_contract(self.contract_path)

            # Prepare the account for deployment
            self.deploy.prepare_account()

            # Deploy the smart contract
            initial_supply = 1000000  # Example initial supply for ERC-20 tokens
            self.deploy.deploy_contract(initial_supply)

            # Return the deployed contract address
            return self.deploy.get_contract_address()

        except Exception as e:
            logger.error(f"Deployment process failed: {e}")
            raise e

def main():
    """Main function to handle the smart contract deployment process."""
    try:
        # Fetch environment variables
        rpc_url = os.getenv("ETH_RPC_URL")
        deployer_private_key = os.getenv("DEPLOYER_PRIVATE_KEY")

        if not rpc_url or not deployer_private_key:
            logger.error("RPC_URL or DEPLOYER_PRIVATE_KEY is missing in environment variables.")
            raise EnvironmentError("Missing RPC_URL or DEPLOYER_PRIVATE_KEY.")

        # Instantiate DeploymentManager to handle contract deployment
        deployment_manager = DeploymentManager("AgentToken.sol", rpc_url, deployer_private_key)

        # Execute the deployment process
        contract_address = deployment_manager.execute_deployment()

        logger.info(f"Smart contract successfully deployed at: {contract_address}")

    except Exception as e:
        logger.error(f"Deployment failed: {e}")

if __name__ == "__main__":
    main()
