import os

def load_env(file_path=".env"):
    """Loads environment variables from a `.env` file into `os.environ`."""
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()

