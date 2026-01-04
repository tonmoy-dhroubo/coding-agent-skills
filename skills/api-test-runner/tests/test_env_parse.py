import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from api_test_runner.discovery.env import extract_base_url, parse_env_text


class TestEnvParsing(unittest.TestCase):
    def test_parse_env_text(self):
        data = parse_env_text("PORT=3000\nDB_HOST=localhost\n")
        self.assertEqual(data["PORT"], "3000")
        self.assertEqual(data["DB_HOST"], "localhost")

    def test_extract_base_url(self):
        base = extract_base_url({"HOST": "127.0.0.1", "PORT": "4000"})
        self.assertEqual(base, "http://127.0.0.1:4000")


if __name__ == "__main__":
    unittest.main()
