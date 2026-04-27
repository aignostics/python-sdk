# Supply-Chain Vulnerabilities

This document describes how aignostics handles vulnerabilities in its Python
dependency supply chain.

Aignostics is consumed both as an application (`uvx aignostics`, or the
Launchpad) and as a library that users add to their own project with
`uv add aignostics`, `pip install aignostics`, or any other resolver. In
both cases the user's tooling picks dependency versions against the
dependency metadata we publish with the aignostics package — our own
lockfile and any development-only constraints we apply locally are
invisible to consumers. The only way to keep a consumer from resolving a
known-vulnerable version of a dependency is therefore to set an
appropriate lower bound on the dependency metadata we publish, including
on transitive dependencies.

This document covers:

- **How we protect consumers** — our default response when a scanner
  reports an advisory, and the fallback path when no upstream fix is
  available yet.
- **Active acceptances** — the (short) list of advisories we have
  consciously accepted because no upstream fix exists or the
  vulnerability is not exploitable in how aignostics uses the package.
  This is where **the actual residual risk lives**: each row records
  severity, scope, downstream-exposure assessment, rationale, and the
  condition under which the acceptance expires.
- **Enforced lower bounds for CVE protection** — the complete catalog of
  lower bounds we currently set specifically to shield consumers from
  advisories that already have an upstream fix.

See [SECURITY.md](SECURITY.md) for the scanners that feed this process
(`pip-audit`, Dependabot, Renovate, trivy, ox.security).

## How we protect consumers

This is sharper than the default practice in the Python ecosystem, where
many libraries constrain only their direct dependencies or rely on their
own lockfile for protection. We deliberately maintain explicit lower
bounds on direct *and* transitive dependencies, annotated with the
relevant CVE / GHSA id, so both `uvx aignostics` and `uv add aignostics`
give consumers a dependency tree free of the advisories we are aware of.

Our policy per finding:

- **Upstream fix available** — raise the lower bound of the affected
  package with an inline CVE / GHSA comment and refresh our lockfile.
  The bound goes on the existing line for direct dependencies, and in
  the transitive-overrides block of the same section for transitive
  ones. If the package is only reachable through an optional extra the
  bound goes in that extra; if the package is genuinely dev-only it goes
  in the dev-group constraints.
- **No upstream fix yet, or not exploitable in our use** — add the
  advisory to the "Active acceptances" table below (with severity,
  downstream-exposure assessment, rationale, and a removal condition)
  and suppress it in `pip-audit` so it does not block CI. We never
  silently ignore a finding.

## Active acceptances

This is where the actual residual risk lives. Each row is an advisory for
which no upstream fix has been released yet — or for which the
vulnerability is not exploitable in how aignostics uses the package —
together with severity, exposure assessment, rationale, and the condition
under which the acceptance expires.

- **Applies to** says when the vulnerable package reaches a consumer's
  tree: *always* (every install), *with the `<X>` extra* (only consumers
  who install that extra), or *dev only* (never reaches consumers;
  affects our tooling only).
- **Downstream exposure** says whether accepting the advisory leaves
  consumers at risk: *None* (e.g. the package is dev-only for us),
  *Partial* (only if a specific extra is installed), or *Full* (every
  consumer install inherits the vulnerable version).

| Advisory | Package (affected) | Severity | Applies to | Downstream exposure | Published | Accepted | Revisit by | Fix status | Rationale | Removal condition | Accepted via |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [GHSA-58qw-9mgm-455v](https://github.com/advisories/GHSA-58qw-9mgm-455v) / [CVE-2026-3219](https://nvd.nist.gov/vuln/detail/CVE-2026-3219) — pip archive type confusion (tar+ZIP concatenation) | `pip` ≤ 26.0.1 | CVSS 4.6 Moderate (CWE-434) | dev only | **None** — `pip` is not shipped as a dependency of `aignostics`; consumers use their own pip. | 2026-04-20 | 2026-04-24 | 2026-05-24 | Fix merged in [pypa/pip#13870](https://github.com/pypa/pip/pull/13870) for milestone `26.1`; not yet released | Exploitation requires `pip install` on an attacker-crafted dual-format archive; aignostics installs only from PyPI and signed GitHub release artifacts. | pip `26.1` (or later) is released on PyPI. Raise the dev-only `pip>=25.3` lower bound to `pip>=26.1` with a `# CVE-2026-3219` comment and remove the ignore. | [PYSDK-93](https://aignx.atlassian.net/browse/PYSDK-93) |

"Revisit by" is a soft deadline: when it passes, we re-check whether the
upstream fix landed or whether a newer advisory superseded this one. For
dev-only entries we revisit quarterly; for runtime entries with a known
upcoming fix, monthly.

## Enforced lower bounds for CVE protection

Every lower bound below is set with an inline CVE / GHSA comment so it is
visible to anyone reading the project metadata. These are the constraints
that prevent downstream consumers from resolving a known-vulnerable
version.

- **Applies to** tells you when the constraint reaches a consumer's
  dependency tree: *always* (affects every `uvx aignostics` and
  `uv add aignostics`), *with the `<X>` extra* (affects only consumers
  who install that extra), or *dev only* (never reaches a consumer;
  applies to our own tooling).
- **Severity** is the highest CVSS rating among the advisories protected
  against, as reported by NVD.
- **Since** is the calendar date on which the lower bound was introduced
  into `main`.

| Package | Constraint | Protects against | Severity | Applies to | Since |
| --- | --- | --- | --- | --- | --- |
| `nicegui[native]` | `>=3.11.0,<4` | [CVE-2026-21871](https://nvd.nist.gov/vuln/detail/CVE-2026-21871), [CVE-2026-21873](https://nvd.nist.gov/vuln/detail/CVE-2026-21873), [CVE-2026-21874](https://nvd.nist.gov/vuln/detail/CVE-2026-21874) (≥3.5.0); [CVE-2026-25516](https://nvd.nist.gov/vuln/detail/CVE-2026-25516) (≥3.7.0); [CVE-2026-27156](https://nvd.nist.gov/vuln/detail/CVE-2026-27156) (≥3.8.0); [CVE-2026-33332](https://nvd.nist.gov/vuln/detail/CVE-2026-33332) (≥3.9.0); [CVE-2026-39844](https://nvd.nist.gov/vuln/detail/CVE-2026-39844) (≥3.10.0) | Medium | always | 2026-01-09 (≥3.5.0); 2026-04-24 raised to ≥3.9.0; 2026-04-26 raised to ≥3.11.0 (#531) |
| `pyjwt[crypto]` | `>=2.12.0,<3` | [CVE-2026-32597](https://nvd.nist.gov/vuln/detail/CVE-2026-32597) | High | always | 2026-04-24 |
| `requests` | `>=2.33.0,<3` | [CVE-2026-25645](https://nvd.nist.gov/vuln/detail/CVE-2026-25645) | Medium | always | 2026-03-26 |
| `urllib3` | `>=2.6.3,<3` | [CVE-2026-21441](https://nvd.nist.gov/vuln/detail/CVE-2026-21441) | Medium | always | 2026-01-08 |
| `h11` | `>=0.16.0` | [CVE-2025-43859](https://nvd.nist.gov/vuln/detail/CVE-2025-43859) | Critical | always | 2025-12-10 |
| `tornado` | `>=6.5.5` | [CVE-2025-47287](https://nvd.nist.gov/vuln/detail/CVE-2025-47287) (≥6.5.0); [GHSA-78cv-mqj4-43f7](https://github.com/advisories/GHSA-78cv-mqj4-43f7) (≥6.5.5) | High | always | 2025-12-10 (≥6.5.0); 2026-04-24 raised to ≥6.5.5 |
| `urllib3` | `>=2.5.0` | [CVE-2025-50181](https://nvd.nist.gov/vuln/detail/CVE-2025-50181), [CVE-2025-50182](https://nvd.nist.gov/vuln/detail/CVE-2025-50182) | Medium | always | 2025-12-10 |
| `pillow` | `>=12.2.0` | [CVE-2025-48379](https://nvd.nist.gov/vuln/detail/CVE-2025-48379) (≥11.3.0); [CVE-2026-25990](https://nvd.nist.gov/vuln/detail/CVE-2026-25990) (≥12.1.1); [CVE-2026-40192](https://nvd.nist.gov/vuln/detail/CVE-2026-40192) (≥12.2.0) | High | always | 2025-12-10 (≥11.3.0); 2026-04-24 raised to ≥12.2.0 |
| `aiohttp` | `>=3.13.4` | [CVE-2025-53643](https://nvd.nist.gov/vuln/detail/CVE-2025-53643), CVE-2025-69223..69230 (≥3.13.3); [CVE-2026-22815](https://nvd.nist.gov/vuln/detail/CVE-2026-22815) (≥3.13.4) | High | always | 2026-01-06 (≥3.13.3); 2026-04-24 raised to ≥3.13.4 |
| `starlette` | `>=0.49.1` | [CVE-2025-54121](https://nvd.nist.gov/vuln/detail/CVE-2025-54121) (≥0.47.2); [GHSA-7f5h-v6xp-fcq8](https://github.com/advisories/GHSA-7f5h-v6xp-fcq8) (≥0.49.1) | Medium | always | 2025-12-10 |
| `lxml` | `>=6.1.0` | [CVE-2026-41066](https://nvd.nist.gov/vuln/detail/CVE-2026-41066) | High | always | 2025-12-10 (≥6.0.2); 2026-04-24 raised to ≥6.1.0 |
| `filelock` | `>=3.20.3` | [CVE-2025-68146](https://nvd.nist.gov/vuln/detail/CVE-2025-68146) (≥3.20.1); [CVE-2026-22701](https://nvd.nist.gov/vuln/detail/CVE-2026-22701) (≥3.20.3) | Medium | always | 2025-12-17 (≥3.20.1); 2026-04-24 raised to ≥3.20.3 |
| `marshmallow` | `>=3.26.2` | [CVE-2025-68480](https://nvd.nist.gov/vuln/detail/CVE-2025-68480) | Medium | always | 2025-12-23 |
| `pygments` | `>=2.20.0` | [CVE-2026-4539](https://nvd.nist.gov/vuln/detail/CVE-2026-4539) | Medium | always | 2026-04-24 |
| `cryptography` | `>=46.0.7` | [CVE-2026-39892](https://nvd.nist.gov/vuln/detail/CVE-2026-39892) | Medium | always | 2026-04-24 |
| `pydicom` | `>=3.0.2` | [CVE-2026-32711](https://nvd.nist.gov/vuln/detail/CVE-2026-32711) | High | always | 2026-04-24 |
| `pyasn1` | `>=0.6.3` | [CVE-2026-30922](https://nvd.nist.gov/vuln/detail/CVE-2026-30922) | High | always | 2026-04-24 |
| `lxml-html-clean` | `>=0.4.4` | [CVE-2026-28348](https://nvd.nist.gov/vuln/detail/CVE-2026-28348), [CVE-2026-28350](https://nvd.nist.gov/vuln/detail/CVE-2026-28350) | Medium | always | 2026-04-24 |
| `python-multipart` | `>=0.0.26` | [CVE-2026-24486](https://nvd.nist.gov/vuln/detail/CVE-2026-24486) (≥0.0.22); [CVE-2026-40347](https://nvd.nist.gov/vuln/detail/CVE-2026-40347) (≥0.0.26) | High | always | 2026-04-24 |
| `protobuf` | `>=6.33.5` | [CVE-2026-0994](https://nvd.nist.gov/vuln/detail/CVE-2026-0994) | High | always | 2026-04-24 |
| `nbconvert` | `>=7.17.1` | [CVE-2025-53000](https://nvd.nist.gov/vuln/detail/CVE-2025-53000) (≥7.17.0); [CVE-2026-39377](https://nvd.nist.gov/vuln/detail/CVE-2026-39377), [CVE-2026-39378](https://nvd.nist.gov/vuln/detail/CVE-2026-39378) (≥7.17.1) | High | with the `jupyter` extra | 2026-04-24 (≥7.17.1) |
| `jupyter-core` | `>=5.8.1` | [CVE-2025-30167](https://nvd.nist.gov/vuln/detail/CVE-2025-30167) | High | with the `jupyter` extra | 2025-12-10 |
| `jupyterlab` | `>=4.4.9` | [CVE-2025-59842](https://nvd.nist.gov/vuln/detail/CVE-2025-59842) | Low | with the `jupyter` extra | 2025-12-10 |
| `marimo` | `>=0.23.0,<1` | [GHSA-2679-6mx9-h9xc](https://github.com/advisories/GHSA-2679-6mx9-h9xc) | Medium | with the `marimo` extra | 2026-04-24 |
| `pip` | `>=25.3` | [CVE-2025-8869](https://nvd.nist.gov/vuln/detail/CVE-2025-8869) | Medium | dev only | 2026-04-01 (>=5.3 — ineffective); 2026-04-24 raised to ≥25.3 |
| `uv` | `>=0.11.6` | [CVE-2025-54368](https://nvd.nist.gov/vuln/detail/CVE-2025-54368), [GHSA-w476-p2h3-79g9](https://github.com/advisories/GHSA-w476-p2h3-79g9), [GHSA-pqhf-p39g-3x64](https://github.com/advisories/GHSA-pqhf-p39g-3x64) (≥0.9.7); [GHSA-pjjw-68hj-v9mw](https://github.com/advisories/GHSA-pjjw-68hj-v9mw) (≥0.11.6) | Medium | dev only | 2025-12-10 (≥0.9.7); 2026-04-24 raised to ≥0.11.6 |
| `pytest` | `>=9.0.3,<10` | [CVE-2025-71176](https://nvd.nist.gov/vuln/detail/CVE-2025-71176) | Medium | dev only | 2026-04-24 |
| `virtualenv` | `>=20.36.1` | [pypa/virtualenv#3013](https://github.com/pypa/virtualenv/pull/3013) TOCTOU fix; bundles filelock ≥3.20.1 for [CVE-2025-68146](https://nvd.nist.gov/vuln/detail/CVE-2025-68146) | Medium | dev only | 2026-04-24 |
| `fonttools` | `>=4.60.2` | [CVE-2025-66034](https://nvd.nist.gov/vuln/detail/CVE-2025-66034) / [GHSA-768j-98cg-p3fv](https://github.com/advisories/GHSA-768j-98cg-p3fv) | Medium | dev only | 2025-12-10 |
