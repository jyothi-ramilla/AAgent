
# AIAgentToken Smart Contract & Agent Development

## Overview

This project involves an ERC-20 token smart contract and a Python-based autonomous agent that interacts with it. The smart contract allows for token transfers, approvals, and balance tracking, while the agent handles various messages and performs token transactions.

---

---

### 1. Running the Project

#### Permissions for Scripts

To ensure that the scripts are executable, run:
```bash
chmod +x run_development.sh run_tests.sh
```

#### Development Setup

To run the development environment, use:
```bash
./run_development.sh
```
This script will build the Docker image and run the agent code continuously until interrupted.

#### Testing Setup

To set up the test environment and run unit/integration tests, use:
```bash
./run_tests.sh
```
This will build the Docker image for testing and execute the test cases.

---

### 2. Agent Code - agent.py

The agent is designed to interact with the `AgentToken` smart contract by processing messages, checking balances, and performing transactions.

#### Key Classes:

- **Inbox:** Stores and retrieves messages for the agent.
- **Outbox:** Sends messages from one agent to another.
- **NonceManager:** Ensures correct transaction order on Ethereum.
- **ERC20Handler:** Handles ERC20 token interactions.
- **AutonomousAgent:** Manages the agent's tasks and interactions.

#### Functions:

- `register_message_handler()`: Registers a handler for specific message types.
- `process_messages()`: Processes messages from the agent's inbox.
- `generate_random_messages()`: Generates random messages periodically.
- `check_balance_periodically()`: Checks and logs the balance at regular intervals.
---


### 3. Docker Setup

- **Dockerfile.dev:** Docker image for the Python environment setup for development.
- **Dockerfile.test:** Docker image for the Python environment setup for testing.

---

### 4. Test Cases  test_agents.py

#### Unit Tests:

- **test_generate_random_messages:** Tests the generation of random messages.
- **test_handle_hello_messages:** Tests handling of 'hello' messages.
- **test_handle_crypto_messages:** Tests handling of 'crypto' messages and token transfer.
- **test_check_balance_periodically:** Tests periodic balance checking.

#### Integration Tests:

- **test_balance_check_and_transfer:** Tests balance checking and transfer functionality.
- **test_resilience_to_invalid_messages:** Tests how the agent handles invalid messages.
- **test_concurrent_threads:** Tests the agent’s multi-threading functionality.
- **test_handle_web3_interaction_failure:** Tests the agent’s response to Web3 interaction failures.
- **test_balance_retrieval_failure:** Tests the agent's behavior when balance retrieval fails.

---

### 5. Environment Variables

Create a `.env` file with the following variables:

```
ETH_RPC_URL=<tenderlyurl>
SOURCE_PRIVATE_KEY=<privatekeyofsource>
TARGET_PRIVATE_KEY=<privatekey>
SOURCE_ADDRESS=<sourceaccount>
TARGET_ADDRESS=<targetaddress>
ERC20_CONTRACT_ADDRESS=<contractaddress>
```

Ensure that you replace the placeholders with appropriate values.

---


### 6. Script for creating Accounts and Private keys

This script demonstrates how to create Ethereum accounts and generate private keys using Web3.

```python
import os
from web3 import Web3
from dotenv import load_dotenv

Create accounts using web3 and ETH_RPC_URL

# Ensure the values are loaded
if not ETH_RPC_URL or not CONTRACT_ADDRESS:
    raise ValueError("ETH_RPC_URL or CONTRACT_ADDRESS not found in the .env file")

# Initialize Web3 connection
w3 = Web3(Web3.HTTPProvider(ETH_RPC_URL))

# Check if connected to the network
if not w3.is_connected():
    raise ValueError("Failed to connect to Ethereum network")

def generate_account():
    """Function to generate a new Ethereum account"""
    account = w3.eth.account.create()
    return account.address, account.key.hex()

# Generate source and target addresses and private keys
source_address, source_private_key = generate_account()
target_address, target_private_key = generate_account()

# Output the generated values
print(f"Source Address: {source_address}")
print(f"Source Private Key: {source_private_key}")
print(f"Target Address: {target_address}")
print(f"Target Private Key: {target_private_key}")
```
