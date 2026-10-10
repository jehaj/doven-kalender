import os
import tempfile
import unittest
from pathlib import Path

from environment import get_value, load_dotenv


class GeneralTests(unittest.TestCase):
    def test_env_keys_exist_in_example(self):
        """Test that all keys in .env exist in .env.example, if .env exists."""
        if not os.path.exists(".env"):
            self.skipTest(".env file not present")

        env_keys = set()
        example_keys = set()

        with open(".env", encoding="utf-8") as env_file, open(".env.example", encoding="utf-8") as example_file:
            for line in env_file:
                if "=" in line and not line.startswith("#"):
                    env_keys.add(line.split("=")[0].strip())

            for line in example_file:
                if "=" in line and not line.startswith("#"):
                    example_keys.add(line.split("=")[0].strip())

        missing_keys = env_keys - example_keys

        self.assertEqual(
            missing_keys,
            set(),
            f"Keys in .env missing from .env.example: {missing_keys}",
        )


class EnvironmentTests(unittest.TestCase):
    def test_load_dotenv_from_file(self):
        """Test that environment variables are loaded correctly from file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_env = Path(temp_dir) / ".env"
            temp_env.write_text("TEST_KEY=test_val\n", encoding="utf-8")

            load_dotenv(temp_env)

            self.assertEqual(get_value("TEST_KEY"), "test_val")

    def test_load_dotenv_missing_file_does_not_raise(self):
        """Test that load_dotenv handles missing files without error."""
        load_dotenv("/path/that/does/not/exist/.env")

    def test_get_value(self):
        """Test that get_value retrieves the correct environment variable."""
        os.environ["MOCK_KEY"] = "mock_val"
        self.assertEqual(get_value("MOCK_KEY"), "mock_val")

    def test_non_value(self):
        """Test that get_value fails for non-existing environment variable."""
        os.environ.pop("FAKE_API_KEY", None)
        with self.assertRaises(ValueError):
            get_value("FAKE_API_KEY")

    def test_setting_value(self):
        """Test that get_value retrieves the updated environment variable after setting it."""
        os.environ["GOOGLE_API_KEY"] = "TEST_VALUE"
        self.assertEqual(get_value("GOOGLE_API_KEY"), "TEST_VALUE")


if __name__ == "__main__":
    unittest.main()
