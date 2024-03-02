import os

ENVIRONMENT = 'local'
# Define base directory paths
PRODUCTION_BASE_DIR = "/var/www/html/"
LOCAL_BASE_DIR = "./"

def get_base_dir():
    """Return the appropriate base directory path based on the environment."""
    if ENVIRONMENT == "production":
        return PRODUCTION_BASE_DIR
    else:
        return LOCAL_BASE_DIR
