# Changelog

All notable changes to purexml, newest first. Format follows
[Keep a Changelog](https://keepachangelog.com/); versions are
[SemVer](https://semver.org/). This is the **public-facing** changelog; the deeper
per-release record (RFCs, compliance, internal axes) lives in
[`HISTORY.md`](HISTORY.md).

> **Pre-1.0:** the public API is not yet frozen — minor releases may refine it. The
> contract binds at **1.0** (see [`PUBLIC_CONTRACT.md`](PUBLIC_CONTRACT.md)). Not yet
> published to PyPI.

## [Unreleased]
- Publish-prep: public README, this changelog, packaging metadata.

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
