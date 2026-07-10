# purexml vs `defusedxml` — why switch

purexml is a **behavioral mirror** of `defusedxml` built on the Python standard library
alone. If `defusedxml` works for you today, purexml does the *same parses* and blocks the
*same attacks* — validated oracle-gated against `defusedxml` itself, every release. So the
honest question isn't "is purexml better at blocking XML attacks" (it's deliberately
*equivalent*) — it's **"what do I gain by switching?"** Two things `defusedxml` can no
longer offer:

1. **Zero dependencies** — drop a third-party package with no loss of protection.
2. **Active maintenance** — a security control that tracks the moving parser-level threat
   landscape, and can tell you what your runtime is actually protected against.

If neither matters to you, staying on `defusedxml` is fine — it still blocks what it always
blocked. This page is for the reader deciding whether the switch is worth it.

---

## 1. The maintenance gap (the main reason)

`defusedxml` is what the [OWASP XXE Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/XML_External_Entity_Prevention_Cheat_Sheet.html)
still points Python developers to — and it earned that. But its last stable release is
**0.7.1 (2021)**; the `0.8.0` line has sat in pre-release (`rc`) and never shipped. The
library is effectively frozen.

The XML threat surface did not freeze with it. Much of Python's XML-DoS resistance lives in
**libexpat** (the C parser under `pyexpat` / `xml.etree`), which has shipped a train of
integer-overflow and denial-of-service fixes — through the 2.7.4 → 2.8.2 releases — that a
frozen wrapper knows nothing about. `defusedxml` blocks the classic *declaration-time*
attacks (entity bombs, XXE) version-independently, and purexml mirrors that exactly — but
neither wrapper can retro-fix libexpat. The difference is that purexml **tracks** it:

- **A currency gate** (`tools/check_expat_currency.py`) checks the latest libexpat against
  the recommended floor before every release, and whenever the security code changes.
- **A posture report** — `security_report()` / `python -m purexml` — tells you, per attack
  class, whether you're protected by purexml's own handlers, by your libexpat version, or by
  an opt-in cap (and flags a stale runtime).
- **A standing external attack battery** soaks every release across every drop-in surface,
  judged on raw evidence (timed-out / memory-exceeded / escaped).

That is the whole reason purexml exists beyond a one-time mirror: it is **maintained where
the incumbent stopped.**

## 2. The dependency case

`defusedxml` is a third-party package in your dependency tree — one more thing to install,
audit, pin, and trust. purexml is **stdlib-only, zero runtime dependencies**, and that claim
is enforced *structurally*: a CI-gated test asserts `src/` imports only the standard `xml`
package — no `socket`, `urllib`, `http`, `subprocess`, or `os` — so purexml cannot reach the
network or filesystem at all, and adds no third-party parser/native code to your import path.

For a security-sensitive dependency, "one fewer thing in the supply chain, with no loss of
protection" is often reason enough on its own.

## 3. What's identical (so switching is safe)

Switching is a literal find-and-replace — `s/defusedxml/purexml/` — because purexml keeps:

- the **same API and defaults** (`forbid_dtd=False`, `forbid_entities=True`,
  `forbid_external=True`);
- the **same exception types and their `ValueError` base**, so your `except` clauses transfer
  unchanged (`purexml.common.DefusedXmlException` aliases the base for catch-all sites);
- the **same standard return objects** (`xml.etree` `Element`, `xml.dom.minidom.Document`,
  SAX events) — your downstream `.find()` / `.iter()` / handler code doesn't change;
- **behavioral equivalence proven every release** — C14N same-parse + event-stream equivalence
  against the `defusedxml` oracle over a real corpus, an adversarial attack battery, and
  differential fuzzing (see [`EQUIVALENCE.md`](EQUIVALENCE.md)).

See [`MIGRATING.md`](MIGRATING.md) for the module-by-module walk-through and
[`../examples/`](../examples/) for runnable versions.

## 4. Side by side

| | `defusedxml` | purexml |
|---|---|---|
| **Runtime dependencies** | third-party package | **zero** (stdlib only, structurally enforced) |
| **Maintenance** | last stable 0.7.1 (2021); 0.8.0 stalled in `rc` | actively maintained |
| **libexpat threat tracking** | none | currency gate + per-class posture report |
| **Structural-DoS caps** (deep nesting / attribute floods / giant docs) | — | opt-in (`max_depth` / `max_attributes` / `max_bytes`), default-off |
| **Posture introspection** | — | `security_report()` + `python -m purexml` |
| **Type hints** | partial | full public surface + PEP 561 `py.typed` |
| **Public-contract guarantee** | — | frozen + binding to 2.0 ([`../PUBLIC_CONTRACT.md`](../PUBLIC_CONTRACT.md)) |
| **Migration** | — | drop-in: `s/defusedxml/purexml/` |

Covered surfaces: `ElementTree`, `minidom`, `sax` / `expatreader`, `xmlrpc`, `common` —
the modules the ecosystem actually imports.

## 5. When *not* to switch (honest boundaries)

purexml's zero-dependency identity draws real lines:

- **You use `defusedxml.lxml`.** purexml **excludes** it by design — `lxml` is a third-party
  C library, and wrapping it would break the zero-dependency contract. There is no drop-in
  for that module.
- **You use `defusedxml.pulldom`.** Deferred (measured-negligible usage) — [open an issue](../CONTRIBUTING.md)
  if you need it.
- **You run on a non-CPython, non-`pyexpat` runtime** (IronPython / Jython). purexml's
  hardening assumes CPython's stdlib expat; those runtimes are out of scope.
- **`defusedxml` isn't broken for you and you don't mind the dependency.** It still blocks
  what it always did. This is a maintenance-and-dependency decision, not a "your parser is
  unsafe" alarm.

---

**In one line:** purexml is the maintained, zero-dependency way to keep exactly the
`defusedxml` protection you already rely on — same parses, same blocks, one fewer dependency,
and a posture that moves with the threat instead of freezing in 2021.
