import logging
from src.deployer import EthereumDeployer

logger = logging.getLogger(__name__)

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
