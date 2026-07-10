# Contributing to purexml

Thanks for your interest. purexml is a **security control** — a zero-dependency,
standard-library-only drop-in for `defusedxml` — so contributions are held to the bar a
security library needs. This page is the short version of what that means in practice.

> **Reporting a vulnerability?** Do **not** open a public issue. A parse that should have
> been blocked, an unexpected fetch/read, or any divergence from `defusedxml`'s blocking is a
> security report — see [`SECURITY.md`](SECURITY.md).

> **Status: 1.0, MIT-licensed, on PyPI** (`pip install purexml`). The public API is **frozen
> and binding** — the `defusedxml`-mirror surface is stable to 2.0 (see
> [`PUBLIC_CONTRACT.md`](PUBLIC_CONTRACT.md)); the opt-in defense-in-depth (`Limits`,
> `security_report()`) stays provisional. For anything beyond a small fix, **open an issue to
> discuss first** — especially anything touching the frozen surface.

## The prime directive

purexml's contract is **behavioral equivalence to `defusedxml` at its defaults** — *matching
the oracle's allow behavior is as much the contract as matching its block behavior.* Two rules
follow that almost every change has to respect:

1. **Never change default parse behavior.** With default arguments, purexml must stay
   C14N-equivalent-or-both-raise vs the `defusedxml` oracle. Any new strictness ships
   **opt-in, default-off** (the way `Limits` and `forbid_dtd=True` do). Over-blocking is a bug.
2. **Stay zero-dependency, stdlib-only.** No third-party runtime dependency, ever. Nothing
   under `src/` may import a network / filesystem / subprocess module — a CI-gated test
   (`tests/test_no_io.py`) enforces this structurally. `defusedxml` is a **dev/test oracle
   only**, never shipped.

If a change can't hold both, it probably belongs in a different project.

## Development setup

```sh
pip install -e ".[dev]"          # editable install + pytest, defusedxml (oracle), ruff, mypy
python -m pytest tests/ -q
```

## The bar (what CI enforces — run it locally before you push)

```sh
python -m pytest tests/ -q                       # all green, CPython 3.10–3.13
python -m pytest --cov=purexml --cov-fail-under=90
ruff check src tests fuzz tools examples         # clean (CI lints all of these)
mypy                                             # --strict, clean
```

A change also has to keep:

- **The differential-fuzz equivalence gate** (`tests/test_fuzz_equivalence.py`) at **0
  divergences** vs the oracle, across every covered surface (ElementTree, minidom, sax, xmlrpc).
- **The no-I/O import guard** (`tests/test_no_io.py`) passing — no new network/fs/exec import
  reachable from `src/`.
- **The consumer-contract gate** (`tests/test_fo_contract.py`) — the anchor consumer's contract
  as named tests (bytes/str parity, the `.common` exception mirror, determinism, the `>=3.10`
  floor, `__version__`). A change that breaks a downstream guarantee fails CI as a *labeled
  regression*, so touch the mirror deliberately.
- **The examples stay runnable** — `tests/test_examples.py` runs each `examples/*.py` as a
  smoke test (exit 0); an example that no longer runs, or an attack it stops blocking, fails CI.
  New/edited examples must run on stdlib + purexml only.
- **Exception shape:** malformed input → stdlib `xml.etree.ElementTree.ParseError`; a blocked
  attack → a `*Forbidden` / `LimitExceeded` exception, all subclassing `ValueError`.

New behavior needs a **falsify-first test** — show the failing input, then the fix. Bug reports
and PRs are most useful with a minimal reproducing XML document.

## How changes are reviewed

Substantive changes go through a four-leg decorrelated review (in-house multi-agent swarm,
a cross-model pass, an empirical corpus/fuzz sweep, and a PR bot — CodeRabbit auto-reviews on
open) and — for new surfaces or parse-behavior changes — an RFC + a compliance report. Every
cross-model/bot finding is **grounded against the real code** before it's acted on (models
overstate severity and critique code they were never shown). You don't have to run all of that
yourself; opening the PR kicks off CI + the CodeRabbit review.

## Commits & PRs

- Keep PRs focused; describe *what changed and why*, and what you ran.
- Reference the issue you discussed (for non-trivial changes).
- Update the docs that drift with your change (README / CHANGELOG / COMPATIBILITY / LIMITATIONS
  / MIGRATING / `examples/` as applicable) in the same PR — sweep the affected docs together,
  not piecemeal.

Thanks again — careful, well-tested contributions to a security control are genuinely valued.
