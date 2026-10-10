"""Environment variables for the application.
This module retrieves environment variables from the environment
or the .env file if it exists,
and provides default values for configuration settings
if none have been set."""

from __future__ import annotations

import os
from pathlib import Path


def load_dotenv(env_path: str | Path = ".env") -> None:
    """Load environment variables from .env file."""
    path = Path(env_path)
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].lstrip()

        key, separator, value = line.partition("=")
        if not separator:
            continue

        key = key.strip()
        value = value.strip()
        if not key:
            continue

        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            value = value[1:-1]

        # According to the documentation os.environ should be
        # used instead of os.putenv
        # https://devdocs.io/python~3.13/library/os#os.putenv
        os.environ[key] = value


def get_value(key: str) -> str:
    """Get the value for the key. If the key is not set,
    raise a ValueError."""
    variable = os.getenv(key)
    if variable is None:
        raise ValueError(f"Environment variable '{key}' is not set.")
    return variable
