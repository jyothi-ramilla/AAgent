# Autonomous Ethereum Agents with ERC20 Integration

## Overview

This project involves an ERC-20 token smart contract and a Python-based autonomous agent that interacts with it. The smart contract allows for token transfers, approvals, and balance tracking, while the agent handles various messages and performs token transactions.

## Design Flow

1. Web3 and Environment Setup - Connects to Ethereum using web3_instance and loads sensitive data (private keys, RPC URL) securely from a .env file.
2. Message Exchange - Agents communicate using Inbox and Outbox classes to send and receive messages seamlessly. 
3. Nonce Management - The NonceManager ensures proper transaction ordering by managing the nonce and avoiding race conditions.
4. ERC-20 Token Interaction - The ERC20Handler fetches token balances and handles secure token transfers with proper gas and nonce management.
5. Autonomous Agents - Agents, running as threads, process messages (process_messages()), generate random messages, and periodically check token balances independently and concurrently.
6. Execution Flow - Two agents are created, register message handlers (e.g., "hello" for logging, "crypto" for token transfer), and continuously run in separate threads to achieve autonomy.

### Threads
Using threads, the agents can:

1. Operate independently without blocking each other.
2. Perform multiple tasks concurrently, such as:
3. Processing incoming messages.
4. Generating and sending random messages.
5. Checking token balances periodically.

So I have used Threads.

## Clone from Github
```
1. git clone -b main https://github.com/jyothi-ramilla/AAgent.git
2. cd AAgent/agent
```
## 1.Folder Structure
```
agent/
│
├── src/
│   ├── agents/
│   │   ├── autonomous_agent.py    # Handles agent logic and messaging
│   │   ├── inbox.py               # Inbox for storing received messages
│   │   ├── outbox.py              # Outbox for sending messages
│   └── erc20/
│       ├── erc20_handler.py       # ERC20 token interactions
│       ├── nonce_manager.py       # Nonce management for transactions
│   ├── utils/
│   │   ├── logging_utils.py       # Logging setup
│   │   ├── env_loader.py          # Environment variable loader
│   └── main.py                    # Entry point for running agents
│
├── docker/
│   ├── Dockerfile.dev             # Dockerfile for development environment
│   ├── Dockerfile.test            # Dockerfile for running tests
│   ├── run_dev.sh                 # Bash script to build and run the development Docker container
│   ├── run_tests.sh               # Bash script to build and run tests in Docker
│
├── tests/                         # Contains test files for each module
│   ├── integrationtest_agent.py   # integration tests for the agent
|   ├── unittest_agent.py          # Unit tests for the agent
│
├── token_contract                 # Codebase for deploying ERC20 Token Contract. This is optional if you already have the ERC20 contract. Use it in case needed
│
├── .env                           # Environment variables file
├── requirements.txt               # Python dependencies
└── README.md                      # Project documentation
```

## 2.Prerequisites

1. Docker and Docker Compose

2. Bash for shell scripting

3. Python dependencies file (see requirements.txt).List all python libraries required to run the code. In this code base we used Web3 and Standard libraries

4. Environment variables

## 3.Guide to configuring Environment Variables

### 1. Generate Source and Target Addresses
To perform transactions, you'll need source and target addresses. You can create two testing addresses using the script below.

#### Script for creating Accounts and Private keys
This script demonstrates how to create Ethereum accounts and generate private keys using Web3.

```python
import os
from web3 import Web3

# Function to load environment variables from a .env file
def load_env_variables(env_file):
    with open(env_file) as file:
        for line in file:
            # Ignore lines starting with '#' or empty lines
            if line.strip() and not line.startswith("#"):
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()

# Load environment variables from the .env file
load_env_variables(".env")

# Fetch the environment variables
ETH_RPC_URL = os.getenv("ETH_RPC_URL")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")

# Ensure the values are loaded
if not ETH_RPC_URL or not CONTRACT_ADDRESS:
    raise ValueError("ETH_RPC_URL or CONTRACT_ADDRESS not found in the environment variables")

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

### 2. Set Up an Ethereum Node Provider using Tenderly

1. Use an Ethereum node provider like Tenderly and obtain an RPC URL.
2. Fund the source and target addresses using a Faucet to cover the gas fees required for each transaction.

### 3.Deploy an ERC20 Contract 

1. Option 1: If you already have an ERC20 smart contract, deploy it and save the contract address. Use this address for all transactions.

2. Option 2: Use the token_contract folder (available in this repository) to deploy the ERC20 contract.

If you are in the agent folder, navigate to the token_contract folder using:

```bash
cd token_contract
```
Deploy the contract once and reuse the contract address for all subsequent transactions.

### 4. Ensure Sufficient ERC20 Tokens

1. After deployment, ensure that the source and target addresses hold sufficient balances of the deployed ERC20 tokens.
2. These tokens are required for transactions like transfers and balance tracking.

### 5. Create a .env file in the project root with the following variables:

```
ETH_RPC_URL=<Your Ethereum RPC URL>
SOURCE_ADDRESS=<Source Ethereum Address>
TARGET_ADDRESS=<Target Ethereum Address>
ERC20_CONTRACT_ADDRESS=<Deployed ERC20 Contract Address>
SOURCE_PRIVATE_KEY=<Private Key for Source Address>
TARGET_PRIVATE_KEY=<Private Key for Target Address>
```

## 4.How to run the Project

### Docker Setup

- **docker/Dockerfile.dev:** Docker image for the Python environment setup for development.
- **docker/Dockerfile.test:** Docker image for the Python environment setup for testing.
- **docker/run_dev.sh:** Bash script to run the development docker image
- **docker/run_tests.sh:** Bash script to run the testing docker image 
---

### Permissions for Scripts

To ensure that the scripts are executable, run:
```bash
chmod +x ./docker/run_dev.sh ./docker/run_tests.sh
```

### Development Setup

To run the development environment, use:
```bash
./docker/run_dev.sh
```
This script will build the Docker image and run the agent code continuously until interrupted.

### Testing Setup

To set up the test environment and run unit/integration tests, use:
```bash
./docker/run_tests.sh
```
This will build the Docker image for testing and execute the test cases.

---

## 5.Agent Code - src/main.py

The agent is designed to interact with the deployed smart contract by processing messages, checking balances, and performing transactions.

### Key Classes:

- **Inbox:** Stores and retrieves messages for the agent.
- **Outbox:** Sends messages from one agent to another.
- **NonceManager:** Ensures correct transaction order on Ethereum.
- **ERC20Handler:** Handles ERC20 token interactions.
- **AutonomousAgent:** Manages the agent's tasks and interactions.

### Key Functions:

- `register_message_handler()`: Registers a handler for specific message types.
- `process_messages()`: Processes messages from the agent's inbox.
- `generate_random_messages()`: Generates random messages periodically.
- `check_balance_periodically()`: Checks and logs the balance at regular intervals.
---

## 6.Test Cases  

### Unit Tests - tests/unittest_agent.py:

- **test_generate_random_messages:** Tests the generation of random messages.
- **test_handle_hello_messages:** Tests handling of 'hello' messages.
- **test_handle_crypto_messages:** Tests handling of 'crypto' messages and token transfer.
- **test_check_balance_periodically:** Tests periodic balance checking.

### Integration Tests - tests/integrationtest_agent.py:

- **test_balance_check_and_transfer:** Tests balance checking and transfer functionality.
- **test_resilience_to_invalid_messages:** Tests how the agent handles invalid messages.
- **test_concurrent_threads:** Tests the agent’s multi-threading functionality.
- **test_handle_web3_interaction_failure:** Tests the agent’s response to Web3 interaction failures.
- **test_balance_retrieval_failure:** Tests the agent's behavior when balance retrieval fails.

---

