"""Standing libexpat-currency check — the maintained-successor promise as mechanism.

purexml's reason to exist beyond file-observer is *tracking the moving libexpat
target*. This makes that check one command instead of a thing someone remembers to
do: it compares the latest upstream libexpat release against the pinned
`RECOMMENDED_EXPAT_VERSION` and reports drift.

Lives in `tools/` (a TRACKED location, NOT `src/`): it must be runnable from a clean
clone — a gate the contract requires can't depend on gitignored scratch (PR#14 Codex)
— yet it uses the network (`gh` API), so it must stay outside the no-I/O import-guarded
package (`test_no_io` only scans `src/purexml/`). Zero new deps: the already-auth'd
`gh` CLI + stdlib. Run from anywhere:

    python tools/check_expat_currency.py

Exit 0 = in sync; exit 1 = DRIFT (newer libexpat exists). On drift, run the
floor-currency review (see the printed checklist): bump RECOMMENDED to latest-stable
(a PATCH — report data, not parse behavior), and for each new release assess whether
its fix reaches purexml's parse paths → if so, add it to the security_report() map
gated on its own fix version (a MINOR / RFC, as v0.6 did). Ground each CVE before
mapping (grounding rule), and surface to Russell — never auto-PR/merge unattended.
"""
import json
import pathlib
import re
import subprocess
import sys

# Resolve the package from the repo layout relative to THIS file, so the check works
# regardless of the caller's cwd (tools/ -> repo root -> src/).
_REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO / "src"))
from purexml import RECOMMENDED_EXPAT_VERSION  # noqa: E402

_TAG = re.compile(r"^R_(\d+)_(\d+)_(\d+)$")


def _tag_to_tuple(tag):
    m = _TAG.match(tag)
    return tuple(int(g) for g in m.groups()) if m else None


def _gh(args):
    return subprocess.run(["gh", *args], capture_output=True, text=True, check=True).stdout


def main():
    latest_tag = _gh(["api", "repos/libexpat/libexpat/releases/latest",
                       "--jq", ".tag_name"]).strip()
    latest = _tag_to_tuple(latest_tag)
    if latest is None:
        print("could not parse latest libexpat tag: %r" % latest_tag)
        return 2

    cur = ".".join(map(str, RECOMMENDED_EXPAT_VERSION))
    new = ".".join(map(str, latest))
    print("RECOMMENDED_EXPAT_VERSION = %s   latest libexpat = %s (%s)"
          % (cur, new, latest_tag))

    if latest <= RECOMMENDED_EXPAT_VERSION:
        print("IN SYNC — no libexpat currency action needed.")
        return 0

    # Drift: list the releases newer than our floor for the review.
    rels = json.loads(_gh(["api", "repos/libexpat/libexpat/releases",
                           "--jq", "[.[] | .tag_name]"]))
    newer = [t for t in rels if (_tag_to_tuple(t) or (0, 0, 0)) > RECOMMENDED_EXPAT_VERSION]
    print("\n*** DRIFT *** libexpat %s is newer than RECOMMENDED %s." % (new, cur))
    print("Releases to review: %s" % ", ".join(reversed(newer)))
    print(
        "\nFloor-currency review (per CLAUDE.md maintenance gate + Known decisions):\n"
        "  1. For each release, read its Changes/CVEs; ground reachability vs purexml's\n"
        "     BLOCKED handlers + parse paths (grounding rule — don't map a guess).\n"
        "  2. Bump RECOMMENDED_EXPAT_VERSION to latest-stable — a PATCH (report data only).\n"
        "  3. For any new class that REACHES purexml's parse paths, add it to\n"
        "     security_report().mitigations gated on its own fix version — a MINOR (RFC),\n"
        "     as v0.6 did. Classes purexml can't reach stay unmapped (recorded).\n"
        "  4. Surface to Russell (draft relay) — do NOT auto-PR/merge unattended.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
