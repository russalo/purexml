# Changelog

All notable changes to purexml, newest first. Format follows
[Keep a Changelog](https://keepachangelog.com/); versions are
[SemVer](https://semver.org/). This is the **public-facing** changelog; the deeper
per-release record (RFCs, compliance, internal axes) lives in
[`HISTORY.md`](HISTORY.md).

> **v1.0.0:** the public API is **frozen and binding** — see
> [`PUBLIC_CONTRACT.md`](PUBLIC_CONTRACT.md). Install with `pip install purexml`.

## [1.0.1] — 2026-07-08
### Fixed
- **PyPI project description.** 1.0.0 was published with the pre-publish README (which still
  read "not yet published to PyPI / depend on it via git"), and an uploaded release's
  `long_description` is immutable. 1.0.1 re-uploads with the corrected README — the accurate
  `pip install purexml` front door + PyPI badges + the russalo byline. **No code change**;
  parse behavior byte-identical to 1.0.0; the frozen contract is unchanged.

## [1.0.0] — 2026-07-08
### Changed
- **Public contract frozen + binding.** The `defusedxml`-mirror surface — module
  namespaces, function signatures + defaults, the complete exception hierarchy, the
  `>=3.10` floor, and `__version__` — is now **Stable to 2.0**. The opt-in
  defense-in-depth (`Limits`, `security_report()`, the version-assertion surface) is
  **Provisional** by design (freezing it would block hardening against new expat CVE
  classes without a 2.0). Guarded by `tests/test_public_contract.py`. Ratified by the
  file-observer steward. See
  [`docs/v1.0.0_RFC_Specification.md`](docs/v1.0.0_RFC_Specification.md) +
  [`PUBLIC_CONTRACT.md`](PUBLIC_CONTRACT.md).
- **No parse-or-block behavior change** — 1.0 is a governance/contract freeze, not a
  feature release. Default parse output stays byte-equivalent to `defusedxml`.

## [0.14.1] — 2026-06-28
### Added
- **License: MIT** — purexml is now MIT-licensed (`LICENSE`; `license`/classifier set in
  packaging metadata). Pure open source, zero strings. (PyPI publishing remains a separate,
  deliberate step.)

## [0.14.0] — 2026-06-27
### Added
- Opt-in `Limits` structural-DoS caps (`max_depth`/`max_attributes`/`max_bytes`) now
  apply to **`purexml.minidom`** and **`purexml.sax`** too, via a keyword-only
  `limits=` argument. Default-off — with `limits=None` these surfaces stay byte-identical
  to defusedxml. (xmlrpc is bounded by its own anti-decompression-bomb cap instead.)

## [0.13.0] — 2026-06-26
### Added
- **`purexml.xmlrpc`** — a drop-in for `defusedxml.xmlrpc`: `monkey_patch()` /
  `unmonkey_patch()` install/restore a defused parser plus a bounded (anti-bomb) gzip
  decode on the stdlib `xmlrpc`. Network-capable imports stay lazy — `import purexml`
  never pulls the transport.

## [0.12.0] — 2026-06-26
### Added
- **`purexml.sax`** + **`purexml.expatreader`** — drop-ins for `defusedxml.sax` /
  `.expatreader`: `make_parser` / `parse` / `parseString` driving a caller's
  `ContentHandler`.

## [0.11.0] — 2026-06-26
### Changed
- `security_report()` maps the reachable libexpat 2.8.2 integer-overflow batch
  (`integer_overflow_dos_expat_2_8_2`), gated on expat ≥ 2.8.2.

## [0.10.0] — 2026-06-19
### Added
- **`purexml.minidom`** — a drop-in for `defusedxml.minidom` (`parse` / `parseString`
  returning a stdlib `Document`), plus **`purexml.common`** (aliases
  `DefusedXmlException = PureXMLError`, so `except DefusedXmlException` survives
  `s/defusedxml/purexml/`).

## [0.9.0] — 2026-06-19
### Changed
- `security_report()` maps the SipHash hash-flooding class (`hash_flooding_cve_2026_41080`).

## [0.8.0] — 2026-06-18
### Added
- **Type annotations + `py.typed`** (PEP 561): the public API is annotated and the
  package ships its types, so your type-checker uses purexml's types instead of `Any`.
  `mypy`-clean, enforced by a CI typecheck job.

## [0.7.0] — 2026-06-17
### Added
- `python -m purexml` posture CLI over `security_report()`: default human report
  (informs, exit 0), `--json` (machine-readable), `--check [--min-expat X.Y.Z]`
  (opt-in CI gate, exit code), `--version`.
- `SecurityReport.as_dict()` — JSON-safe serialization.

## [0.6.0] — 2026-06-17
### Added
- `security_report()` now reports the newer libexpat DoS classes
  (`content_token_overflow_cve_2026_25210`, `attribute_collision_dos_cve_2026_45186`),
  each gated on its own libexpat fix version.

## [0.5.1] — 2026-06-17
### Changed
- Refreshed the recommended libexpat floor to **2.8.1** after the 2026 libexpat DoS
  release train; decoupled per-class mitigation reporting from the moving floor.
### Added
- Adversarial soak: a red-team vector module (incl. encoding-vector attacks) backed by
  a 60k-comparison differential soak vs the `defusedxml` oracle.

## [0.5.0] — 2026-06-17
### Added
- **Trust surface:** read-only `security_report()` — runtime libexpat version +
  per-attack-class mitigation map + recommended limits.
- Committed per-release equivalence report ([`docs/EQUIVALENCE.md`](docs/EQUIVALENCE.md));
  optional coverage-guided fuzzing via the `[fuzz]` extra.

## [0.4.0] — 2026-06-16
### Added
- Opt-in structural-DoS caps — `Limits` (`max_depth`/`max_attributes`/`max_bytes`),
  default-off — raising `LimitExceeded`. First opt-in step beyond defusedxml.

## [0.3.0] — 2026-06-16
### Added
- Hardened `iterparse` — **completes the `defusedxml.ElementTree` family**
  (`fromstring`, `parse`, `iterparse`, `fromstringlist`, `XML`, `XMLParser`,
  `tostring`, `ParseError`, the `forbid_*` knobs).

## [0.2.0] — 2026-06-16
### Added
- Non-streaming ElementTree surface (`parse`, `fromstringlist`, `XML`/`tostring`,
  exposed `XMLParser`) + the `forbid_*` knobs (incl. `forbid_dtd` strict mode).

## [0.1.0] — 2026-06-16
### Added
- First release: hardened `fromstring`, behaviorally equivalent to `defusedxml` at its
  defaults, standard-library-only. (0.1.1 lowered the floor to Python 3.10; 0.1.2 added
  differential fuzzing + libexpat version awareness.)
