"""08 — Know your runtime's posture: security_report() + the CLI.

purexml's protection is partly libexpat-version-dependent (its own Python-layer
handlers block entity bombs / XXE / external DTDs on every runtime; parser-level DoS
mitigations depend on your libexpat). `security_report()` tells you what each attack
class is protected by ON THIS runtime. Read-only — it does not parse, fetch, or fail.

Run:  python examples/08_security_posture.py     (also try:  python -m purexml)
"""
import purexml


def main() -> None:
    report = purexml.security_report()
    print(report)  # human-readable posture summary

    print("\nlibexpat on this runtime:", ".".join(map(str, purexml.EXPAT_VERSION)))

    # Machine-readable form — e.g. to assert posture in CI.
    data = report.as_dict()
    print("attack classes mapped:", len(data["mitigations"]))
    print("expat meets recommended floor:", data["expat_meets_recommended"])

    print("\nTip: `python -m purexml --check --min-expat 2.8.2` is an opt-in CI gate")
    print("     (exit code non-zero if the runtime's libexpat is below your floor).")


if __name__ == "__main__":
    main()
