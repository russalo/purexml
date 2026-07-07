"""Smoke-test the shipped examples: each must run to completion (exit 0).

The `examples/` scripts are public, copy-run-able documentation. A shipped example
that no longer runs is worse than none — so this gate runs each one as a subprocess
against the current package and fails CI if any exits non-zero. It keeps the examples
honest to the API the same way `test_fo_contract.py` keeps the FO contract honest.
"""
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_DIR = REPO_ROOT / "examples"
SCRIPTS = sorted(EXAMPLES_DIR.glob("[0-9]*.py"))


def test_examples_present():
    """Guard against the glob silently matching nothing (a moved dir would make
    every parametrized test vanish and look green)."""
    assert SCRIPTS, f"no example scripts found under {EXAMPLES_DIR}"


@pytest.mark.parametrize("script", SCRIPTS, ids=lambda p: p.name)
def test_example_runs(script):
    """Each example runs to completion with exit 0 (stdlib + purexml only)."""
    # pytest's `pythonpath = ["src"]` does NOT propagate to spawned subprocesses, so
    # put src on PYTHONPATH explicitly — the examples then import purexml whether or
    # not the package is editable-installed (CI installs it; a bare `pytest` may not).
    env = os.environ.copy()
    src = str(REPO_ROOT / "src")
    env["PYTHONPATH"] = os.pathsep.join(p for p in (src, env.get("PYTHONPATH", "")) if p)
    result = subprocess.run(
        [sys.executable, str(script)],
        capture_output=True,
        text=True,
        timeout=60,
        env=env,
    )
    assert result.returncode == 0, (
        f"{script.name} exited {result.returncode}\n"
        f"--- stdout ---\n{result.stdout}\n--- stderr ---\n{result.stderr}"
    )
