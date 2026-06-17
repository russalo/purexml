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

#: The only top-level (non-relative) import the runtime needs: the stdlib XML
#: parser. Adding anything here must be a conscious decision (a pure parser's
#: import surface is part of its security guarantee).
ALLOWED_TOPLEVEL = {"xml"}

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
    for node in ast.walk(ast.parse(path.read_text())):
        if isinstance(node, ast.Import):
            for alias in node.names:
                mods.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:  # level>0 == relative, skip
                mods.add(node.module.split(".")[0])
    return mods


def test_src_imports_only_stdlib_xml():
    """Strong form: the entire runtime import surface is the stdlib `xml` package."""
    for py in _SRC.rglob("*.py"):
        extra = _toplevel_imports(py) - ALLOWED_TOPLEVEL
        assert not extra, (
            "%s imports outside the allowed surface %s: %s "
            "(adding a stdlib import is a conscious security decision — update "
            "ALLOWED_TOPLEVEL with justification)" % (py.name, ALLOWED_TOPLEVEL, extra)
        )


def test_src_imports_no_io_or_exec_modules():
    """Explicit form: no network / process-exec / filesystem module is imported."""
    for py in _SRC.rglob("*.py"):
        bad = _toplevel_imports(py) & FORBIDDEN
        assert not bad, "%s imports forbidden I/O/exec module(s): %s" % (py.name, bad)
