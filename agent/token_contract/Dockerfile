# Base Image
FROM python:3.12-slim

# Set environment variables for non-interactive installs
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file first to install dependencies
COPY requirements.txt /app/

# Install virtualenv globally
RUN pip install --no-cache-dir virtualenv setuptools

# Create a virtual environment
RUN virtualenv venv

# Activate the virtual environment and upgrade pip, setuptools, and wheel
RUN . venv/bin/activate && pip install --upgrade pip setuptools wheel

# Install dependencies into the virtual environment
RUN . venv/bin/activate && pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . /app

# Create the artifacts directory for storing compiled contract data
RUN mkdir -p /app/contracts/artifacts

# Ensure the artifacts directory has write permissions
RUN chmod -R 777 /app/contracts/artifacts

# Set environment variables for RPC URL and deployer private key
ENV RPC_URL=$RPC_URL
ENV DEPLOYER_PRIVATE_KEY=$DEPLOYER_PRIVATE_KEY

# Use the virtual environment to run the entry point script
CMD ["/app/venv/bin/python", "main.py"]
