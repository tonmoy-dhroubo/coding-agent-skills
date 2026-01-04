import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from api_test_runner.reporting.report import format_markdown_report


class TestReporting(unittest.TestCase):
    def test_format_markdown_report(self):
        output = format_markdown_report(
            [
                {
                    "method": "GET",
                    "path": "/health",
                    "status": 200,
                    "latency_ms": 10,
                    "notes": "ok",
                }
            ]
        )
        self.assertIn("| GET | /health | 200 | 10 | ok |", output)


if __name__ == "__main__":
    unittest.main()
