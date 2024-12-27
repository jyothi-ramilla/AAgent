import os
import logging
from src.manager import DeploymentManager

# Configure logging settings
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main function to handle the smart contract deployment process."""
    try:
        # Fetch environment variables
        rpc_url = os.environ.get("ETH_RPC_URL")
        deployer_private_key = os.environ.get("DEPLOYER_PRIVATE_KEY")

        if not rpc_url or not deployer_private_key:
            logger.error("RPC_URL or DEPLOYER_PRIVATE_KEY is missing in environment variables.")
            raise EnvironmentError("Missing RPC_URL or DEPLOYER_PRIVATE_KEY.")

        # Define the contract path
        contract_path = os.path.join("contracts", "AgentToken.sol")

        # Instantiate DeploymentManager to handle contract deployment
        deployment_manager = DeploymentManager(contract_path, rpc_url, deployer_private_key)

        # Execute the deployment process
        contract_address = deployment_manager.execute_deployment()

        logger.info(f"Smart contract successfully deployed at: {contract_address}")

    except Exception as e:
        logger.error(f"Deployment failed: {e}")

if __name__ == "__main__":
    main()
