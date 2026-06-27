# Contributing to purexml

Thanks for your interest. purexml is a **security control** — a zero-dependency,
standard-library-only drop-in for `defusedxml` — so contributions are held to the bar a
security library needs. This page is the short version of what that means in practice.

> **Reporting a vulnerability?** Do **not** open a public issue. A parse that should have
> been blocked, an unexpected fetch/read, or any divergence from `defusedxml`'s blocking is a
> security report — see [`SECURITY.md`](SECURITY.md).

> **Status: pre-1.0, license pending.** The public API isn't frozen yet and the license is an
> open decision (see the README). For anything beyond a small fix, **open an issue to discuss
> first** — it saves you from building against a moving target.

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
ruff check src tests                             # clean
mypy src                                         # --strict, clean
```

A change also has to keep:

- **The differential-fuzz equivalence gate** (`tests/test_fuzz_equivalence.py`) at **0
  divergences** vs the oracle, across every covered surface (ElementTree, minidom, sax, xmlrpc).
- **The no-I/O import guard** (`tests/test_no_io.py`) passing — no new network/fs/exec import
  reachable from `src/`.
- **Exception shape:** malformed input → stdlib `xml.etree.ElementTree.ParseError`; a blocked
  attack → a `*Forbidden` / `LimitExceeded` exception, all subclassing `ValueError`.

New behavior needs a **falsify-first test** — show the failing input, then the fix. Bug reports
and PRs are most useful with a minimal reproducing XML document.

## How changes are reviewed

Substantive changes go through a four-leg decorrelated review (in-house multi-agent swarm,
a cross-model pass, an empirical corpus/fuzz sweep, and PR bots) and — for new surfaces or
parse-behavior changes — an RFC + a compliance report. Every cross-model/bot finding is
**grounded against the real code** before it's acted on. You don't have to run all of that
yourself; opening the PR kicks off the parts that run on PR open.

## Commits & PRs

- Keep PRs focused; describe *what changed and why*, and what you ran.
- Reference the issue you discussed (for non-trivial changes).
- Update the docs that drift with your change (README / CHANGELOG / COMPATIBILITY / LIMITATIONS
  as applicable) in the same PR.

Thanks again — careful, well-tested contributions to a security control are genuinely valued.
