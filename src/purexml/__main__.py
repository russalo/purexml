"""CLI: ``python -m purexml`` — report this runtime's XML-security posture.

Read-only introspection over `purexml.security_report()`. **Informs by default
(exit 0)**; ``--check`` is the *caller* opting into a CI gate (the inform-by-default
version-assertion stance). This module is the package's one **I/O boundary** — it
prints, and imports ``argparse``/``json``/``sys`` on top of purexml — but nothing
that reaches the network / filesystem / subprocess. `tests/test_no_io` enforces both
halves: the parse surface stays strict stdlib-`xml`, and this file may add only those
CLI-output modules, never a forbidden one.
"""
import argparse
import json
import sys

from . import __version__, security_report
from . import _expat_security as _es


def _ver(t):
    return ".".join(map(str, t))


def _build_parser():
    p = argparse.ArgumentParser(
        prog="python -m purexml",
        description="Report this runtime's XML-security posture (purexml).")
    p.add_argument("--json", action="store_true",
                   help="emit the posture as JSON (machine-readable; PROVISIONAL shape)")
    p.add_argument("--check", action="store_true",
                   help="exit non-zero if libexpat is below the floor (opt-in CI gate)")
    p.add_argument("--min-expat", metavar="X.Y.Z", default=None,
                   help="floor for --check (default: the recommended-latest floor)")
    p.add_argument("--version", action="store_true",
                   help="print purexml and libexpat versions, then exit")
    return p


def main(argv=None):
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.version:
        print("purexml %s (libexpat %s)" % (__version__, _ver(_es.EXPAT_VERSION)))
        return 0

    report = security_report()
    if args.json:
        print(json.dumps({"purexml_version": __version__, **report.as_dict()}))
    else:
        print(report)

    if args.check:
        if args.min_expat is not None:
            try:
                floor = _es._as_version_tuple(args.min_expat)
            except (ValueError, TypeError):
                parser.error("--min-expat must be a version like 2.8.1, got %r"
                             % args.min_expat)
        else:
            floor = _es.RECOMMENDED_EXPAT_VERSION
        if _es.EXPAT_VERSION < floor:
            print("FAIL: libexpat %s is below the required floor %s"
                  % (_ver(_es.EXPAT_VERSION), _ver(floor)), file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
