import os

def is_local():
    """
    Checks if the application is running in a local environment.
    Defaults to True if the ENVIRONMENT variable is not set.
    """
    return os.getenv("ENVIRONMENT", "local") == "local"
