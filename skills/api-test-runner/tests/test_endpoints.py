import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from api_test_runner.discovery.endpoints import discover_endpoints


class TestEndpointDiscovery(unittest.TestCase):
    def test_discover_openapi(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            spec = {
                "openapi": "3.0.0",
                "paths": {"/health": {"get": {}}, "/users": {"post": {}}},
            }
            path = os.path.join(tmpdir, "openapi.json")
            with open(path, "w", encoding="utf-8") as handle:
                json.dump(spec, handle)
            endpoints = discover_endpoints(tmpdir)
            methods = {(e["method"], e["path"]) for e in endpoints}
            self.assertIn(("GET", "/health"), methods)
            self.assertIn(("POST", "/users"), methods)


if __name__ == "__main__":
    unittest.main()
