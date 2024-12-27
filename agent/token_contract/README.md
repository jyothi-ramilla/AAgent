#### Note: Use this code if you dont have the ERC20 contract address to run the agent code. 

# AgentToken Smart Contract

## Overview

The `AgentToken` is an ERC-20 token smart contract with the following features. It is designed to create a token on the Ethereum blockchain and provide basic functionalities such as transferring tokens, approving spenders, and tracking balances.

## WorkFlow

### 1.Set up environment variables:

1. ETH_RPC_URL: Ethereum node RPC URL of Tenderly
2. DEPLOYER_PRIVATE_KEY: Private key of the deployer account.

### 2.Compile and Deploy the Contract:

The contract file (AgentToken.sol) is compiled using the compile_contract method, saving the ABI and bytecode to artifacts/.

The smart contract is deployed to the Ethereum network with an initial supply, using the deploy_contract method.

### 3.Deployment Results:
The deployed contract’s address is returned, and the deployment process is logged.

## Clone the Repository
1. git clone -b main https://github.com/jyothi-ramilla/AAgent.git
2. cd AAgent/agent/token_contract

## 1.Folder Structure
```
token_contract
├── contracts
│   ├── AgentToken.sol            # Solidity source code
│   └── artifacts                  
│       ├── AgentToken_abi.json  # ABI file
│       └── AgentToken_bytecode.json  # Bytecode file
├── deploy.sh                    # Shell script for deployment
├── Dockerfile                   # Docker image build instructions
├── env-local                    # Local environment variables 
├── main.py                      # Entry point for the deployment process
├── README.md                    # Project documentation
├── requirements.txt             # Python dependencies
├── src
│   ├── deployer.py              # Contains contract deployment logic
│   └── manager.py               # Contains contract management logic (optional additional logic)
```
## 2.Prerequisites

1. Docker and Docker Compose

2. Bash for shell scripting

3. Python dependencies file (see requirements.txt).List all python libraries required to run the code.

4. Environment variables 

5. ERC20 SmartContract

## 3.Configure the environment variables
```
ETH_RPC_URL=<Tenderly Ethereum Node RPC URL>
DEPLOYER_PRIVATE_KEY=<privatekey of the Deployer>
```
## 4.Smart Contract Details

### ERC-20 Standard:

This contract adheres to the ERC-20 standard, which is widely used for managing tokens on the Ethereum blockchain.

### Token Details:
- **Name:** Agent Token
- **Symbol:** AIT
- **Decimals:** 18 (standard token precision)
- **Total Supply:** The initial supply is set by the contract creator and assigned to their address.

### Key Functions:
- `transfer()`: Allows users to send tokens to other addresses.
- `approve()`: Allows users to grant permission to other addresses to spend tokens on their behalf.
- `transferFrom()`: Lets an approved spender transfer tokens from an owner's account.

### Events:
- `Transfer`: Logs token transfers between addresses.
- `Approval`: Logs when an owner allows a spender to transfer tokens.

## 5.To Run the Codebase

The Dockerfile is used to set up the Python environment and deploy the smart contract using the specified tools and scripts.

1. Make the deploy script executable:
   ```bash
   chmod +x ./deploy.sh
   ```

2. Run the deploy script:
   ```bash
   ./deploy.sh
   ```
   This command will create the Docker image and deploy the smart contract. Once completed, you will receive the smart contract address.


### CONTRACT ADDRESS

Once the smart contract is deployed, the contract address will be generated and its artifacts are stored in contracts/artifacts folder

**Smart Contract Address:** 

This address represents the deployed token contract address on the Ethereum Node of Tenderly.


## 6. Key Classes and their Functions 

### 1. EthereumDeployer - src/deployer.py
This class is responsible for handling the deployment of an Ethereum smart contract. It connects to the Ethereum network, compiles the Solidity contract, and deploys it using the provided private key.

#### Key Functions:
1. connect_to_network(): Establishes a connection to the Ethereum network using the provided RPC URL.
2. compile_contract(contract_path): Compiles the provided Solidity smart contract file and saves the ABI and bytecode to the artifacts folder.
3. prepare_account(): Prepares the Ethereum account from the private key for signing and sending transactions.
4. deploy_contract(initial_supply): Deploys the compiled contract to the Ethereum network with an initial supply (for ERC-20 token contracts).
5. get_contract_address(): Returns the deployed contract address.

### 2. DeploymentManager - src/manager.py
This class manages the overall deployment process. It uses the EthereumDeployer class to compile and deploy a contract, ensuring the entire process is executed in order.

#### Key Functions:
1. __init__(contract_path, rpc_url, private_key): Initializes the deployment manager with the  contract path, RPC URL, and private key.
2. execute_deployment(): Executes the full contract deployment process: connects to the network, compiles the contract, prepares the account, and deploys the contract. Returns the deployed contract address.

### 3. Main Script (main() function) - main.py
 The main function coordinates the execution of the deployment process by fetching necessary environment variables and invoking the DeploymentManager to deploy the contract.
