FROM python:3.12-slim

# Install necessary packages using pip3
RUN pip3 install --no-cache-dir virtualenv

# Set the working directory
WORKDIR /app

# Copy the project files into the container
COPY . /app

# Create a virtual environment and activate it
RUN python3 -m venv /app/venv

# Install the required Python packages in the virtual environment
RUN /app/venv/bin/pip install --no-cache-dir web3 py-solc-x 

# Set environment variables
ENV RPC_URL=$RPC_URL
ENV DEPLOYER_PRIVATE_KEY=$DEPLOYER_PRIVATE_KEY

# Ensure the virtual environment is activated when running the Python script
CMD ["/app/venv/bin/python", "deploy_contract.py"]

