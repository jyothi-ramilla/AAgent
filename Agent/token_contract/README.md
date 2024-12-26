This is optional.Use it only when needed.

# AIAgentToken Smart Contract


## Overview

The `AIAgentToken` is an ERC-20 token smart contract with the following features. It is designed to create a token on the Ethereum blockchain and provide basic functionalities such as transferring tokens, approving spenders, and tracking balances.

## Clone the Repository
1. git clone -b main https://github.com/jyothi-ramilla/AAgent.git
2. cd Agent
3. cd token_contract

## Folder Structure
├── AgentToken.abi
├── AgentToken.sol
├── deploy_contract.py
├── deploy.sh
├── Dockerfile
├── env-local
├── README.md
└── requirements.txt

## To Run the Codebase

1. Make the deploy script executable:
   ```bash
   chmod +x ./deploy.sh
   ```

2. Run the deploy script:
   ```bash
   ./deploy.sh
   ```
   This command will create the Docker image and deploy the smart contract. Once completed, you will receive the smart contract address.

## Dockerfile

The Dockerfile is used to set up the Python environment and deploy the smart contract using the specified tools and scripts.

## Smart Contract Details

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

## ERC-20 Standard:

This contract adheres to the ERC-20 standard, which is widely used for managing tokens on the Ethereum blockchain.

## CONTRACT ADDRESS

Once the smart contract is deployed, the following contract address will be generated:

**Smart Contract Address:** 

This address represents the deployed token contract address on the Ethereum Node of Tenderly.

## env file 

Consist of ETH_RPC_URL(Tenderly Ethereum Node), DEPLOYER_PRIVATE_KEY
