"""Environment variables for the application.
This module retrieves environment variables from the environment
or the .env file if it exists,
and provides default values for configuration settings
if none have been set."""



def load_dotenv() -> None:
    """Load environment variables from .env file."""
    with open(".env", "r") as file:
        import os

        for line in file:
            if line.strip() and not line.startswith("#"):
                key, value = line.strip().split("=", 1)
                key = key.strip()
                value = value.strip()
                if key and value:
                    # According to the documentation os.environ should
                    # used instead of os.putenv
                    # https://devdocs.io/python~3.13/library/os#os.putenv
                    os.environ[key] = value

def get_value(key: str) -> str:
    """Get the value for the key. If the key is not set,
    raise a ValueError."""
    import os

    variable = os.getenv(key)
    if variable is None:
        raise ValueError(f"Environment variable '{key}' is not set.")
    return variable
