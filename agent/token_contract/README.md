#### Note: Use this code if you dont have the ERC20 contract for running the agent code. 

# AIAgentToken Smart Contract

## Overview

The `AIAgentToken` is an ERC-20 token smart contract with the following features. It is designed to create a token on the Ethereum blockchain and provide basic functionalities such as transferring tokens, approving spenders, and tracking balances.

## Clone the Repository
1. git clone -b main https://github.com/jyothi-ramilla/AAgent.git
2. cd AAgent/agent/token_contract

## 1.Folder Structure

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
