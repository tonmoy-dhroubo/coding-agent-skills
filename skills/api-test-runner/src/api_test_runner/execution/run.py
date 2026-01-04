import subprocess
from typing import List


RUNTIME_COMMANDS = {
    "python": ["python3"],
    "node": ["node"],
    "bash": ["bash"],
}


def run_runner(runtime: str, script_path: str) -> int:
    cmd: List[str] = RUNTIME_COMMANDS.get(runtime, ["python3"])
    cmd = cmd + [script_path]
    result = subprocess.run(cmd, check=False)
    return result.returncode
