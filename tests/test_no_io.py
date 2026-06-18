"""Structural no-I/O guard (v0.3.1).

A safe XML parser must never reach the network or filesystem. The attack battery
proves this *behaviorally* (the no-fetch/no-read trip-wire); this test proves it
*structurally* — `src/purexml/` imports only the stdlib `xml` package, and none of
the network / process-exec / OS modules. So purexml literally cannot open a socket,
run a subprocess, or touch the filesystem (beyond what the caller hands `parse`).
"""
import ast
import pathlib

import purexml

#: The top-level (non-relative) imports the runtime is permitted — all pure, no I/O:
#:   xml         — the stdlib XML parser (the whole point)
#:   collections — `namedtuple` (Limits/SecurityReport)
#:   types       — `MappingProxyType` (read-only mitigations view)
#:   typing      — type annotations (v0.8 typed surface); pure, evaluated lazily
#:   __future__  — `annotations` (PEP 563 lazy annotations)
#: Adding anything here must be a conscious decision (a pure parser's import surface
#: is part of its security guarantee — each entry is justified inline).
ALLOWED_TOPLEVEL = {"xml", "collections", "types", "typing", "__future__"}

#: The CLI entry point (`__main__.py`, v0.7) is the package's ONE explicit I/O
#: boundary — it prints the posture report, so it may import the CLI-output stdlib on
#: top of the library surface. None of these reach the network/filesystem/subprocess
#: (they stay subject to FORBIDDEN below); the parse surface keeps the strict allowlist.
CLI_EXTRA = {"argparse", "json", "sys"}
CLI_FILE = "__main__.py"

#: Explicitly forbidden — network, process-exec, OS, and low-level memory modules,
#: plus common third-party HTTP clients. None belong in a stdlib-only safe parser.
FORBIDDEN = {
    "socket", "ssl", "urllib", "http", "ftplib", "smtplib", "poplib", "imaplib",
    "telnetlib", "subprocess", "multiprocessing", "asyncio", "ctypes", "mmap",
    "os", "shutil", "pathlib", "requests", "httpx", "aiohttp", "pycurl",
}

_SRC = pathlib.Path(purexml.__file__).resolve().parent


def _toplevel_imports(path):
    """Top-level module names imported non-relatively by *path* (relative imports
    — the package's own modules — are excluded)."""
    mods = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            for alias in node.names:
                mods.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:  # level>0 == relative, skip
                mods.add(node.module.split(".")[0])
    return mods


def test_src_imports_only_stdlib_xml():
    """Strong form: the entire runtime import surface is the stdlib `xml` package —
    except the CLI entry point, which may add CLI-output stdlib (see CLI_EXTRA)."""
    for py in _SRC.rglob("*.py"):
        allowed = ALLOWED_TOPLEVEL | CLI_EXTRA if py.name == CLI_FILE else ALLOWED_TOPLEVEL
        extra = _toplevel_imports(py) - allowed
        assert not extra, (
            "%s imports outside the allowed surface %s: %s "
            "(adding a stdlib import is a conscious security decision — update "
            "ALLOWED_TOPLEVEL with justification)" % (py.name, allowed, extra)
        )


def test_src_imports_no_io_or_exec_modules():
    """Explicit form: no network / process-exec / filesystem module is imported."""
    for py in _SRC.rglob("*.py"):
        bad = _toplevel_imports(py) & FORBIDDEN
        assert not bad, "%s imports forbidden I/O/exec module(s): %s" % (py.name, bad)
