
# AIAgentToken Smart Contract

## Overview

The `AIAgentToken` is an ERC-20 token smart contract with the following features. It is designed to create a token on the Ethereum blockchain and provide basic functionalities such as transferring tokens, approving spenders, and tracking balances.

## To Run the Codebase

1. Make the deploy script executable:
   ```bash
   chmod +x deploy.sh
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

**Smart Contract Address:** 0x284d63E2979bB01F89e71bc651b2e23b2503a16A

This address represents the deployed token contract on the Ethereum network of Test node.

## env file 

Consist of ETH_RPC_URL, DEPLOYER_PRIVATE_KEY