[🔬 Aignostics Python SDK](https://aignostics.readthedocs.io/en/latest/)

# [0.2.118](https://github.com/aignostics/python-sdk/compare/v0.2.117..0.2.118) - 2025-08-10

### ⚙️ Miscellaneous Tasks

- *(notebook)* Adapt to refactoring - ([d2502e5](https://github.com/aignostics/python-sdk/commit/d2502e5f8d44b9751a6214a946d47f943b5c9b6f))


# [v0.2.117](https://github.com/aignostics/python-sdk/compare/v0.2.116..v0.2.117) - 2025-08-10

### 🐛 Bug Fixes

- *(notebook)* Navigation to marimo - ([8d3d117](https://github.com/aignostics/python-sdk/commit/8d3d117bfba1381576c722c5bafc8213945d0599))

### ⚙️ Miscellaneous Tasks

- *(notebook)* Adapt test - ([8813de6](https://github.com/aignostics/python-sdk/commit/8813de6e3beadf5108c203be25059511c7eda05a))


# [v0.2.116](https://github.com/aignostics/python-sdk/compare/v0.2.115..v0.2.116) - 2025-08-09

### 🚜 Refactor

- *(notebook)* Simplify open marimo button - ([4bc3184](https://github.com/aignostics/python-sdk/commit/4bc318415c12abda1758290dde1764e9c36cc6e5))

### ⚙️ Miscellaneous Tasks

- *(bucket)* Better logging for flaky test - ([4bc3184](https://github.com/aignostics/python-sdk/commit/4bc318415c12abda1758290dde1764e9c36cc6e5))


# [v0.2.115](https://github.com/aignostics/python-sdk/compare/v0.2.114..v0.2.115) - 2025-08-09

### ⚙️ Miscellaneous Tasks

- *(bucket)* More time for download test - ([a9d036c](https://github.com/aignostics/python-sdk/commit/a9d036c308cbc0a798fe8cf5f7d32c9e0ece2093))


# [v0.2.114](https://github.com/aignostics/python-sdk/compare/v0.2.113..v0.2.114) - 2025-08-09

### ⚙️ Miscellaneous Tasks

- *(notebook)* Cannot in parallel test multiple marimo servers on same host with no isolation - ([bb27f4c](https://github.com/aignostics/python-sdk/commit/bb27f4caf417e400c0978f73799a25cb75f88288))


# [v0.2.113](https://github.com/aignostics/python-sdk/compare/v0.2.112..v0.2.113) - 2025-08-09

### 🐛 Bug Fixes

- *(bucket)* In GUI use static version of download operation offered by service - ([66499ae](https://github.com/aignostics/python-sdk/commit/66499ae082dcec8230adb2b1e140e6ccdba8d232))

### ⚙️ Miscellaneous Tasks

- *(audit)* Audit reports part of release artifacts - ([66499ae](https://github.com/aignostics/python-sdk/commit/66499ae082dcec8230adb2b1e140e6ccdba8d232))
- *(deps)* Bump - ([66499ae](https://github.com/aignostics/python-sdk/commit/66499ae082dcec8230adb2b1e140e6ccdba8d232))
- *(pytest)* Show recent notifications if asserted one not found - ([66499ae](https://github.com/aignostics/python-sdk/commit/66499ae082dcec8230adb2b1e140e6ccdba8d232))
- *(release)* Announce release on internal Slack (experimental) - ([66499ae](https://github.com/aignostics/python-sdk/commit/66499ae082dcec8230adb2b1e140e6ccdba8d232))
- *(test)* Don't provide log as job artifact - ([66499ae](https://github.com/aignostics/python-sdk/commit/66499ae082dcec8230adb2b1e140e6ccdba8d232))

### 🛡️ Security

- *(uv)* Use uv > 0.8.6 in pre-commit hook - ([66499ae](https://github.com/aignostics/python-sdk/commit/66499ae082dcec8230adb2b1e140e6ccdba8d232))


# [v0.2.112](https://github.com/aignostics/python-sdk/compare/v0.2.111..v0.2.112) - 2025-08-08

### ⚙️ Miscellaneous Tasks

- *(heta)* Adapt tests - ([2d315d0](https://github.com/aignostics/python-sdk/commit/2d315d0fd84cb62520b08dda845d2fef2c6c9636))


# [v0.2.111](https://github.com/aignostics/python-sdk/compare/v0.2.110..v0.2.111) - 2025-08-08

### 🚜 Refactor

- *(uv)* Define required uv version in pyproject.toml, for use across GHA - ([c7b7db2](https://github.com/aignostics/python-sdk/commit/c7b7db275d6924aecc5f8ee657e69577ebdd8e1a))

### ⚙️ Miscellaneous Tasks

- *(deps)* Bump - ([a62e9c7](https://github.com/aignostics/python-sdk/commit/a62e9c7974db39dc5e64e64a7ddc22572a9bef9b))
- *(deps)* Bump various github actions versions - ([c7b7db2](https://github.com/aignostics/python-sdk/commit/c7b7db275d6924aecc5f8ee657e69577ebdd8e1a))
- *(heta)* Further adaptation to changed output file sizes - ([a62e9c7](https://github.com/aignostics/python-sdk/commit/a62e9c7974db39dc5e64e64a7ddc22572a9bef9b))

### 🛡️ Security

- *(dep)* Ensure all uses of uv are >= 0.8.6 (CVE-2025-54368) - ([c7b7db2](https://github.com/aignostics/python-sdk/commit/c7b7db275d6924aecc5f8ee657e69577ebdd8e1a))


# [v0.2.110](https://github.com/aignostics/python-sdk/compare/v0.2.109..v0.2.110) - 2025-08-08

### 🚜 Refactor

- *(tests)* Central place for app id and version - ([fef1174](https://github.com/aignostics/python-sdk/commit/fef1174a9168baa1042ad569adf1212a31875678))
- *(tests)* Central constants for app and app version id to simplify adapting to new apps - ([4156d33](https://github.com/aignostics/python-sdk/commit/4156d33da999018ae933005739aca69001bd4df9))

### ⚙️ Miscellaneous Tasks

- *(tests)* Adapt to heta.5 - ([47cffb7](https://github.com/aignostics/python-sdk/commit/47cffb7ec05d8b417c6dd24d368a20a1e9f0ba94))

### 🛡️ Security

- *(dep)* Force UV >0.8.6 given CVE-2025-54368 - ([e8ff6c1](https://github.com/aignostics/python-sdk/commit/e8ff6c167727e5f00d06fa40da4a6de10ab2a9ab))


# [v0.2.109](https://github.com/aignostics/python-sdk/compare/v0.2.108..v0.2.109) - 2025-08-07


# [v0.2.108](https://github.com/aignostics/python-sdk/compare/v0.2.107..v0.2.108) - 2025-08-07

### ⚙️ Miscellaneous Tasks

- *(test)* Adapt remaining test config to beta.5 of heta - ([6d98300](https://github.com/aignostics/python-sdk/commit/6d983007b11604f1a1b3aab4f5fdb00956070707))


# [v0.2.107](https://github.com/aignostics/python-sdk/compare/v0.2.106..v0.2.107) - 2025-08-07

### ⛰️  Features

- *(codegen, platform)* Support me endpoint ([#81](https://github.com/orhun/git-cliff/issues/81)) - ([9666c56](https://github.com/aignostics/python-sdk/commit/9666c563e9fd2404e7ad27c15605e3237b7f0bfa))
- Allow to boot with zero config, i.e. no .env file required in default case - ([9666c56](https://github.com/aignostics/python-sdk/commit/9666c563e9fd2404e7ad27c15605e3237b7f0bfa))

### 🐛 Bug Fixes

- *(codegen)* Don't rely on redirects from /v1 to /api/v1 - ([9666c56](https://github.com/aignostics/python-sdk/commit/9666c563e9fd2404e7ad27c15605e3237b7f0bfa))
- *(platform)* Allow to dial into dev environment - ([9666c56](https://github.com/aignostics/python-sdk/commit/9666c563e9fd2404e7ad27c15605e3237b7f0bfa))
- Fix typos in readme.md - ([1b6a652](https://github.com/aignostics/python-sdk/commit/1b6a65253ca524a76c41506d5c00de5bfbd16be6))

### ⚙️ Miscellaneous Tasks

- *(deps)* Bump nicegui - ([e190094](https://github.com/aignostics/python-sdk/commit/e1900941f155f1382fd7d767aed2d4b5e6fe1e4d))
- *(deps)* Bump - ([9666c56](https://github.com/aignostics/python-sdk/commit/9666c563e9fd2404e7ad27c15605e3237b7f0bfa))
- *(heta)* Adapt tests to 1.0.0-beta.5 of HETA - ([9666c56](https://github.com/aignostics/python-sdk/commit/9666c563e9fd2404e7ad27c15605e3237b7f0bfa))



* @omid-aignostics made their first contribution in [#70](https://github.com/aignostics/python-sdk/pull/70)

# [v0.2.106](https://github.com/aignostics/python-sdk/compare/v0.2.105..v0.2.106) - 2025-07-22

### ⚙️ Miscellaneous Tasks

- *(audit)* Allow for heartbeat url specific for audit - ([475eac1](https://github.com/aignostics/python-sdk/commit/475eac159816f3e63b1724b66b71c79fbe6912be))
- *(publish)* Adapt to recent changes - ([524f8d1](https://github.com/aignostics/python-sdk/commit/524f8d130011df71b2a9841149a5611e673dd1b0))


# [v0.2.105](https://github.com/aignostics/python-sdk/compare/v0.2.104..v0.2.105) - 2025-07-22

### ⚙️ Miscellaneous Tasks

- *(gha)* Add metadata to BetterStack when posting heartbeats ([#61](https://github.com/orhun/git-cliff/issues/61)) - ([bd74063](https://github.com/aignostics/python-sdk/commit/bd740634dcf8749e479c020556602d621d54cf7c))

### 🛡️ Security

- *(dep)* Ensure starlette >= 0.47.2 given GHSA-2c2j-9gv5-cj73 - ([98ebe61](https://github.com/aignostics/python-sdk/commit/98ebe612eccdd17175bfa49e6a683b426117c55d))



* @idelsink made their first contribution in [#61](https://github.com/aignostics/python-sdk/pull/61)

# [v0.2.104](https://github.com/aignostics/python-sdk/compare/v0.2.103..v0.2.104) - 2025-07-15

### 📚 Documentation

- Update URLs in openapi spec and downstream docs - ([083e992](https://github.com/aignostics/python-sdk/commit/083e9923f71b28c670457354ab90f84088e715ed))


# [v0.2.103](https://github.com/aignostics/python-sdk/compare/v0.2.102..v0.2.103) - 2025-07-15

### ⚙️ Miscellaneous Tasks

- *(gha)* Monitor scheduled audit in betterstack - ([e9f22f8](https://github.com/aignostics/python-sdk/commit/e9f22f8fd2fbab6219f77759be604c3879424af6))


# [v0.2.102](https://github.com/aignostics/python-sdk/compare/v0.2.101..v0.2.102) - 2025-07-15

### ⚙️ Miscellaneous Tasks

- *(gha)* Separate scheduled audit in separate workflow - ([0feb976](https://github.com/aignostics/python-sdk/commit/0feb976c7c1020fa551cc4750ef1b82fe431c486))


# [v0.2.101](https://github.com/aignostics/python-sdk/compare/v0.2.99..v0.2.101) - 2025-07-15

### ⚙️ Miscellaneous Tasks

- *(deps)* Update ghcr.io/astral-sh/uv docker tag to v0.7.20 ([#59](https://github.com/orhun/git-cliff/issues/59)) - ([987828d](https://github.com/aignostics/python-sdk/commit/987828d3b2b25acfc74938c50f3b8c55e3b7805c))
- *(deps)* Update ghcr.io/astral-sh/uv docker tag to v0.7.15 ([#54](https://github.com/orhun/git-cliff/issues/54)) - ([65a9b24](https://github.com/aignostics/python-sdk/commit/65a9b247f9fa1821a12d2f95685d70a0e7ae2be1))
- *(deps)* Bump astral-sh/setup-uv from 6.3.0 to 6.3.1 ([#55](https://github.com/orhun/git-cliff/issues/55)) - ([1ee922e](https://github.com/aignostics/python-sdk/commit/1ee922ee3aefb89256f42652416fc326d9bef383))
- Renovate[bot] <29139614+renovate[bot]@users.noreply.github.com> - ([987828d](https://github.com/aignostics/python-sdk/commit/987828d3b2b25acfc74938c50f3b8c55e3b7805c))
- Helmut Hoffer von Ankershoffen né Oertel <helmut@aignostics.com> - ([65a9b24](https://github.com/aignostics/python-sdk/commit/65a9b247f9fa1821a12d2f95685d70a0e7ae2be1))
- Dependabot[bot] <support@github.com> - ([1ee922e](https://github.com/aignostics/python-sdk/commit/1ee922ee3aefb89256f42652416fc326d9bef383))
- Dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com> - ([1ee922e](https://github.com/aignostics/python-sdk/commit/1ee922ee3aefb89256f42652416fc326d9bef383))

### 🛡️ Security

- *(dep)* Override aiohttp to 3.12.14 given vulnerability GHSA-9548-qrrj-x5pj - ([c9cefae](https://github.com/aignostics/python-sdk/commit/c9cefae37c255b05c1453a0a795695f55b7d3c44))



* @renovate[bot] made their first contribution in [#59](https://github.com/aignostics/python-sdk/pull/59)
* @dependabot[bot] made their first contribution in [#55](https://github.com/aignostics/python-sdk/pull/55)

# [v0.2.99](https://github.com/aignostics/python-sdk/compare/v0.2.98..v0.2.99) - 2025-07-10

### 🚜 Refactor

- *(boot)* Reduce boot time - ([e8b3250](https://github.com/aignostics/python-sdk/commit/e8b32504fb053fbdb9454e42be6160fb8317da6a))

### 📚 Documentation

- Minor tweaks - ([e8b3250](https://github.com/aignostics/python-sdk/commit/e8b32504fb053fbdb9454e42be6160fb8317da6a))

### ⚙️ Miscellaneous Tasks

- *(deps)* Update deps - ([e8b3250](https://github.com/aignostics/python-sdk/commit/e8b32504fb053fbdb9454e42be6160fb8317da6a))
- *(platform)* Update to latest openapi spec - ([e8b3250](https://github.com/aignostics/python-sdk/commit/e8b32504fb053fbdb9454e42be6160fb8317da6a))


# [v0.2.98](https://github.com/aignostics/python-sdk/compare/v0.2.97..v0.2.98) - 2025-07-01

### ⚙️ Miscellaneous Tasks

- *(application)* Mark test as long running - ([e5a3d9f](https://github.com/aignostics/python-sdk/commit/e5a3d9fe270c37a8ff5812f30909d76fa764fec5))


# [v0.2.97](https://github.com/aignostics/python-sdk/compare/v0.2.96..v0.2.97) - 2025-07-01

### 🛡️ Security

- *(deps)* Pillow 11.3.0 given CVE-2025-48379 - ([a2c1387](https://github.com/aignostics/python-sdk/commit/a2c1387c71bb6186e41a740e5f5053db18dd0988))


# [v0.2.96](https://github.com/aignostics/python-sdk/compare/v0.2.95..v0.2.96) - 2025-07-01

### 🐛 Bug Fixes

- *(platform)* Allow for rapid re-auth - ([b299932](https://github.com/aignostics/python-sdk/commit/b2999322c70e0e7026b2ce185dbfa3e0d129f7af))


# [v0.2.95](https://github.com/aignostics/python-sdk/compare/v0.2.94..v0.2.95) - 2025-07-01

### 🐛 Bug Fixes

- *(application)* Allow next post excluding slides if remaining slides with valid metadata - ([ee6945b](https://github.com/aignostics/python-sdk/commit/ee6945b8f8013d6ff9779bf9459ade368560256b))


# [v0.2.94](https://github.com/aignostics/python-sdk/compare/v0.2.93..v0.2.94) - 2025-07-01

### ⚙️ Miscellaneous Tasks

- *(platform)* Even more time for test app - ([852c3f0](https://github.com/aignostics/python-sdk/commit/852c3f039dc452e8e5a6c6b581224aa7397ac94d))


# [v0.2.93](https://github.com/aignostics/python-sdk/compare/v0.2.92..v0.2.93) - 2025-06-29

### ⚙️ Miscellaneous Tasks

- *(platform)* Even more time for test app - ([c46bd12](https://github.com/aignostics/python-sdk/commit/c46bd1297ef2ded50d6db54a3f1d5ca4542f8fc4))


# [v0.2.92](https://github.com/aignostics/python-sdk/compare/v0.2.91..v0.2.92) - 2025-06-29

### ⚙️ Miscellaneous Tasks

- *(application)* Adapt test - ([7fde8d5](https://github.com/aignostics/python-sdk/commit/7fde8d5d78157d324309e4135573ea23d480d36e))


# [v0.2.91](https://github.com/aignostics/python-sdk/compare/v0.2.90..v0.2.91) - 2025-06-29

### 🚜 Refactor

- *(application)* Consistent exception logging and raising - ([2f2acfb](https://github.com/aignostics/python-sdk/commit/2f2acfba3e9aaf95b6037661b44ba1ecec5c0609))


# [v0.2.90](https://github.com/aignostics/python-sdk/compare/v0.2.89..v0.2.90) - 2025-06-29

### ⚙️ Miscellaneous Tasks

- Run hooks - ([e343303](https://github.com/aignostics/python-sdk/commit/e343303179bb14d46e3b243f9c5f59b141407439))


# [v0.2.89](https://github.com/aignostics/python-sdk/compare/v0.2.88..v0.2.89) - 2025-06-29

### ⚙️ Miscellaneous Tasks

- Run hooks - ([3c888ad](https://github.com/aignostics/python-sdk/commit/3c888ad07b9add48d0df0610bd4426feb51e8574))


# [v0.2.88](https://github.com/aignostics/python-sdk/compare/v0.2.87..v0.2.88) - 2025-06-29

### ⚙️ Miscellaneous Tasks

- *(native)* Only distribute aignostics.app bundle for MacOS - ([82a085b](https://github.com/aignostics/python-sdk/commit/82a085bd0cc32ef4afe372f28589bb9974da11fe))
- *(native)* 7z, to preserve attributes - ([82a085b](https://github.com/aignostics/python-sdk/commit/82a085bd0cc32ef4afe372f28589bb9974da11fe))


# [v0.2.87](https://github.com/aignostics/python-sdk/compare/v0.2.86..v0.2.87) - 2025-06-28

### 🐛 Bug Fixes

- *(dataset)* Missing dependency, while still smaller then pyarrow - ([ff41393](https://github.com/aignostics/python-sdk/commit/ff413933c0c90a98222f731331df8c5e054222ea))


# [v0.2.86](https://github.com/aignostics/python-sdk/compare/v0.2.85..v0.2.86) - 2025-06-28

### 🚜 Refactor

- *(logging)* Revert to cwd for logfile - ([e5c235c](https://github.com/aignostics/python-sdk/commit/e5c235c01456067a14ad03046d40b940e32058ce))


# [v0.2.85](https://github.com/aignostics/python-sdk/compare/v0.2.84..v0.2.85) - 2025-06-28

### 🚜 Refactor

- *(logging)* Use app dir as default for log file - ([e8a8a75](https://github.com/aignostics/python-sdk/commit/e8a8a750d46021fab4affd9c118fdd460a10659b))
- *(native)* Significantly reduce size and bootup time - ([e8a8a75](https://github.com/aignostics/python-sdk/commit/e8a8a750d46021fab4affd9c118fdd460a10659b))


# [v0.2.84](https://github.com/aignostics/python-sdk/compare/v0.2.83..v0.2.84) - 2025-06-28

### ⚙️ Miscellaneous Tasks

- *(platform)* Give test application more time in tests - ([5a03f74](https://github.com/aignostics/python-sdk/commit/5a03f742479a9ec703be048c25a527e0ee43ade3))


# [v0.2.83](https://github.com/aignostics/python-sdk/compare/v0.2.82..v0.2.83) - 2025-06-28

### 📚 Documentation

- *(platform)* Description - ([38af243](https://github.com/aignostics/python-sdk/commit/38af24326fe7f50823b286113bd392ce3343c337))


# [v0.2.82](https://github.com/aignostics/python-sdk/compare/v0.2.81..v0.2.82) - 2025-06-28

### 📚 Documentation

- *(platform)* Description - ([d353ff3](https://github.com/aignostics/python-sdk/commit/d353ff3851984e2870579de95421c344c621aba7))


# [v0.2.81](https://github.com/aignostics/python-sdk/compare/v0.2.80..v0.2.81) - 2025-06-28

### 📚 Documentation

- *(platform)* Description - ([a772bed](https://github.com/aignostics/python-sdk/commit/a772bed258cfc3a106e6a6e9ebb397a5ba48439b))


# [v0.2.80](https://github.com/aignostics/python-sdk/compare/v0.2.79..v0.2.80) - 2025-06-28

### 🚜 Refactor

- *(platform)* Test timeout/expires - ([a2fffab](https://github.com/aignostics/python-sdk/commit/a2fffab8e4d2ad3c1f070f3ee10afd0a74257487))


# [v0.2.79](https://github.com/aignostics/python-sdk/compare/v0.2.78..v0.2.79) - 2025-06-28

### 🚜 Refactor

- *(platform)* Test timeout/expires - ([7ab1e75](https://github.com/aignostics/python-sdk/commit/7ab1e75237ec3195a5fc82c40e5ea4439a2722ac))


# [v0.2.78](https://github.com/aignostics/python-sdk/compare/v0.2.77..v0.2.78) - 2025-06-28

### ⚙️ Miscellaneous Tasks

- *(platform)* Adapt test to app versions - ([e203cf9](https://github.com/aignostics/python-sdk/commit/e203cf94bbc8d80b76687322a62cda77cfb00cb2))


# [v0.2.77](https://github.com/aignostics/python-sdk/compare/v0.2.76..v0.2.77) - 2025-06-28

### ⚙️ Miscellaneous Tasks

- *(platform)* Adapt test to app versions - ([873640e](https://github.com/aignostics/python-sdk/commit/873640eb4d2cd026f9438a3cdc90afdc6aa1f231))


# [v0.2.76](https://github.com/aignostics/python-sdk/compare/v0.2.75..v0.2.76) - 2025-06-27

### ⚙️ Miscellaneous Tasks

- *(platform)* Move from dummy to test app in test - ([c2e7bde](https://github.com/aignostics/python-sdk/commit/c2e7bded7f51eaa283938d672308c3f5980b68a3))


# [v0.2.75](https://github.com/aignostics/python-sdk/compare/v0.2.74..v0.2.75) - 2025-06-27

### ⚙️ Miscellaneous Tasks

- *(platform)* Allow long running tests for 4h, bump of signed url expire accordingly - ([9808e97](https://github.com/aignostics/python-sdk/commit/9808e97c14e01af23d2ebde1cba93686d90f8881))


# [v0.2.74](https://github.com/aignostics/python-sdk/compare/v0.2.73..v0.2.74) - 2025-06-27

### ⚙️ Miscellaneous Tasks

- *(application,platform)* Test with v1.0.0-beta.4 of HETA - ([e112b0c](https://github.com/aignostics/python-sdk/commit/e112b0c8de692d17f916cc5219a5024343e56a73))


# [v0.2.73](https://github.com/aignostics/python-sdk/compare/v0.2.72..v0.2.73) - 2025-06-27

### 🐛 Bug Fixes

- ⚡️ Use SemVer to check for application ids in launchpad ([#56](https://github.com/orhun/git-cliff/issues/56)) - ([1ee2f76](https://github.com/aignostics/python-sdk/commit/1ee2f768a1985082882c2d8c77c4bb32ed621d7f))

### 🚜 Refactor

- *(application)* Introduce service tests - ([b41f8e8](https://github.com/aignostics/python-sdk/commit/b41f8e8fb387e8de5f69765b0c2cecd6711cb3e8))



* @ari-nz made their first contribution in [#56](https://github.com/aignostics/python-sdk/pull/56)

# [v0.2.72](https://github.com/aignostics/python-sdk/compare/v0.2.71..v0.2.72) - 2025-06-25

### ⚙️ Miscellaneous Tasks

- *(platform)* Adapt tests to breaking change - ([d9c2f2a](https://github.com/aignostics/python-sdk/commit/d9c2f2a6c7efe1b9bdc4960a9716f228a0d6c9c8))


# [v0.2.71](https://github.com/aignostics/python-sdk/compare/v0.2.70..v0.2.71) - 2025-06-25

### 🐛 Bug Fixes

- *(platform)* Adapt to breaking change in API - ([e869268](https://github.com/aignostics/python-sdk/commit/e8692686bb5d4ed41ee803bc5bf959e24cffc232))

### ⚙️ Miscellaneous Tasks

- *(deps)* Gha setup-uv dep - ([d600f2a](https://github.com/aignostics/python-sdk/commit/d600f2a73a2c5f48ec506f073e306502197f52d0))
- Try new api spec without further change - ([da97c97](https://github.com/aignostics/python-sdk/commit/da97c97006c7a2abdb09643590141aaf38fed40f))


# [v0.2.70](https://github.com/aignostics/python-sdk/compare/v0.2.69..v0.2.70) - 2025-06-24

### 📚 Documentation

- Enhance structure and layout of Changelog - ([6ba9998](https://github.com/aignostics/python-sdk/commit/6ba9998eb1178f0530604852df28b04d11e49852))

### ⚙️ Miscellaneous Tasks

- *(bucket)* Grant more time for bucket gui workflow in test - ([6ba9998](https://github.com/aignostics/python-sdk/commit/6ba9998eb1178f0530604852df28b04d11e49852))
- *(deps)* Update dependencies for GitHub actions - ([6ba9998](https://github.com/aignostics/python-sdk/commit/6ba9998eb1178f0530604852df28b04d11e49852))


# [v0.2.69](https://github.com/aignostics/python-sdk/compare/v0.2.68..v0.2.69) - 2025-06-23

### 🐛 Bug Fixes

- *(platform/user)* Reload on reauth - ([e3af366](https://github.com/aignostics/python-sdk/commit/e3af3668c667e9c585b3d07345e0d7908fafe7a0))

### ⚙️ Miscellaneous Tasks

- *(win32)* Username - ([a746dd0](https://github.com/aignostics/python-sdk/commit/a746dd023487cd989d0f5f2b37119d2221d1eae0))


# [v0.2.68](https://github.com/aignostics/python-sdk/compare/v0.2.67..v0.2.68) - 2025-06-19

### ⚙️ Miscellaneous Tasks

- *(di)* Adapt to typer workaround - ([a5a50bc](https://github.com/aignostics/python-sdk/commit/a5a50bc3c38ff7de3b7fedd6ddeb8664b7fde17b))


# [v0.2.67](https://github.com/aignostics/python-sdk/compare/v0.2.66..v0.2.67) - 2025-06-19

### ⚙️ Miscellaneous Tasks

- *(cli)* Adapt tests - ([69a3803](https://github.com/aignostics/python-sdk/commit/69a38030b2a413f09e981844d4c67c21fc3ec1a4))


# [v0.2.66](https://github.com/aignostics/python-sdk/compare/v0.2.64..v0.2.66) - 2025-06-19

### 🐛 Bug Fixes

- *(typer)* Workaround https://github.com/fastapi/typer/pull/1240 - ([321d502](https://github.com/aignostics/python-sdk/commit/321d502ae1ddf951cfd4b2f13b3591ed819be699))

### 🚜 Refactor

- *(performance)* Faster boot - ([321d502](https://github.com/aignostics/python-sdk/commit/321d502ae1ddf951cfd4b2f13b3591ed819be699))

### 🎨 Styling

- *(bucket)* Button layout - ([321d502](https://github.com/aignostics/python-sdk/commit/321d502ae1ddf951cfd4b2f13b3591ed819be699))

### 🛡️ Security

- *(security)* Update deps given CVE-2025-50181, CVE-2025-50182 - ([321d502](https://github.com/aignostics/python-sdk/commit/321d502ae1ddf951cfd4b2f13b3591ed819be699))


# [v0.2.64](https://github.com/aignostics/python-sdk/compare/v0.2.63..v0.2.64) - 2025-06-18

### ⛰️  Features

- *(bucket)* Allow to select destination in bucket download gui - ([44a6611](https://github.com/aignostics/python-sdk/commit/44a66119bdab63d389f7b4d489e8b0e2a4222977))

### 🚜 Refactor

- *(application)* Shrink images - ([011039a](https://github.com/aignostics/python-sdk/commit/011039ac4aab480db45af6798f69c40183af5d5f))

### ⚙️ Miscellaneous Tasks

- *(bucket)* Bump test duration - ([011039a](https://github.com/aignostics/python-sdk/commit/011039ac4aab480db45af6798f69c40183af5d5f))


# [v0.2.63](https://github.com/aignostics/python-sdk/compare/v0.2.62..v0.2.63) - 2025-06-17

### ⛰️  Features

- *(bucket)* Proper download including support for patterns, keys, gui, cli - ([b0ea8ab](https://github.com/aignostics/python-sdk/commit/b0ea8ab719a6dcb1cace62db9385a5a514422784))
- *(bucket)* Purge - ([b0ea8ab](https://github.com/aignostics/python-sdk/commit/b0ea8ab719a6dcb1cace62db9385a5a514422784))

### 🚜 Refactor

- *(bucket)* Removed ls, refactored find - ([b0ea8ab](https://github.com/aignostics/python-sdk/commit/b0ea8ab719a6dcb1cace62db9385a5a514422784))


# [v0.2.62](https://github.com/aignostics/python-sdk/compare/v0.2.61..v0.2.62) - 2025-06-16

### 🎨 Styling

- Lint - ([6408db4](https://github.com/aignostics/python-sdk/commit/6408db45e3308fc0a996bbf5ded88b73e461acaf))

### ⚙️ Miscellaneous Tasks

- *(QuPath)* Run test on linux - ([8e0c81e](https://github.com/aignostics/python-sdk/commit/8e0c81e1eae380c62b35c3048f10065910ebc819))
- Download from bucket cli - ([ecb7f23](https://github.com/aignostics/python-sdk/commit/ecb7f23cafd0a48e18ee3e9aea707cb7e91620bf))


# [v0.2.61](https://github.com/aignostics/python-sdk/compare/v0.2.60..v0.2.61) - 2025-06-15

### 🚜 Refactor

- *(user)* Rename from platform to user in cli - ([4df6942](https://github.com/aignostics/python-sdk/commit/4df6942850a11704376e4fcc4a0ff90a9d7175aa))


# [v0.2.60](https://github.com/aignostics/python-sdk/compare/v0.2.59..v0.2.60) - 2025-06-15

### ⛰️  Features

- *(userinfo)* Allow to edit profile - ([06604c2](https://github.com/aignostics/python-sdk/commit/06604c2253f3e9c66c7af9c2b14c45a635976c0c))


# [v0.2.59](https://github.com/aignostics/python-sdk/compare/v0.2.58..v0.2.59) - 2025-06-15

### 🎨 Styling

- *(gui)* Polish user info - ([25d607c](https://github.com/aignostics/python-sdk/commit/25d607c5df6d82a311e5a4b21adce5f67ce0b103))


# [v0.2.58](https://github.com/aignostics/python-sdk/compare/v0.2.57..v0.2.58) - 2025-06-15

### 🎨 Styling

- *(gui)* Polish user info - ([e5eca02](https://github.com/aignostics/python-sdk/commit/e5eca02b084860c4957f28d13580962e83af1758))


# [v0.2.57](https://github.com/aignostics/python-sdk/compare/v0.2.56..v0.2.57) - 2025-06-15

### ⚙️ Miscellaneous Tasks

- *(platform)* Lazyload srvice in cli - ([28f1819](https://github.com/aignostics/python-sdk/commit/28f18195c06c2d69a569b4a44b9dcc2e1b07421b))


# [v0.2.56](https://github.com/aignostics/python-sdk/compare/v0.2.55..v0.2.56) - 2025-06-15

### ⛰️  Features

- *(platform,gui)* Org name - ([ca075d9](https://github.com/aignostics/python-sdk/commit/ca075d9bc803722c5faae5af2e8f21a8b558e03a))


# [v0.2.55](https://github.com/aignostics/python-sdk/compare/v0.2.54..v0.2.55) - 2025-06-15

### 🎨 Styling

- Welcome user by name in launchpad - ([ac666f9](https://github.com/aignostics/python-sdk/commit/ac666f932f53531770dd3a852b37a80d3b453dd6))


# [v0.2.54](https://github.com/aignostics/python-sdk/compare/v0.2.53..v0.2.54) - 2025-06-15

### ⛰️  Features

- *(platform,gui,diagnostics)* Whoami - ([bc025b1](https://github.com/aignostics/python-sdk/commit/bc025b191d284293e756cb15c7cc68acc0ba368c))

### 🐛 Bug Fixes

- *(platform)* Graceful fail on user info not accessible - ([f8bb5a8](https://github.com/aignostics/python-sdk/commit/f8bb5a8194c8970d6420d4f748e33b4fd570ef88))

### 🚜 Refactor

- *(platform)* Refactor user profile - ([e2d4f51](https://github.com/aignostics/python-sdk/commit/e2d4f51a19f08320e4f66b5d284546a501f4fda3))

### 🎨 Styling

- Nicer start page graphics - ([bc025b1](https://github.com/aignostics/python-sdk/commit/bc025b191d284293e756cb15c7cc68acc0ba368c))

### ⚙️ Miscellaneous Tasks

- *(deps)* Bump - ([f802e41](https://github.com/aignostics/python-sdk/commit/f802e41fb0f87a91b8cd67e85f70d24c8c37787a))


# [v0.2.53](https://github.com/aignostics/python-sdk/compare/v0.2.52..v0.2.53) - 2025-06-12

### ⛰️  Features

- QuPath enabled by default - ([dc0f876](https://github.com/aignostics/python-sdk/commit/dc0f876f2d414aed8a72b8d40923aa187c866df1))

### 🚜 Refactor

- Don't support QuPath on Linux/arm - ([dc0f876](https://github.com/aignostics/python-sdk/commit/dc0f876f2d414aed8a72b8d40923aa187c866df1))

### 📚 Documentation

- Generate - ([bebf86e](https://github.com/aignostics/python-sdk/commit/bebf86e6286e1780ae350673ba6bf5ca057381f7))


# [v0.2.52](https://github.com/aignostics/python-sdk/compare/v0.2.51..v0.2.52) - 2025-06-12

### 🐛 Bug Fixes

- *(unmask)* Unmask secrets on request in all services - ([8c3e6e6](https://github.com/aignostics/python-sdk/commit/8c3e6e6a9f7b1dde8515458c0304387cf831fe61))

### ⚙️ Miscellaneous Tasks

- *(Makefile)* Typo - ([3b1ac6b](https://github.com/aignostics/python-sdk/commit/3b1ac6b9c6be8e60a63ad16253dd45041193afdb))


# [v0.2.51](https://github.com/aignostics/python-sdk/compare/v0.2.50..v0.2.51) - 2025-06-11

### ⚙️ Miscellaneous Tasks

- Move to long running for install to inspect test - ([a61fe3f](https://github.com/aignostics/python-sdk/commit/a61fe3f12c8483c994606822ebab1072d6d70a1a))


# [v0.2.50](https://github.com/aignostics/python-sdk/compare/v0.2.49..v0.2.50) - 2025-06-11

### 🚜 Refactor

- *(QuPath)* Proper handling of script max execution time - ([0fa1fe0](https://github.com/aignostics/python-sdk/commit/0fa1fe0e586dbf4eadacf49ba24282655cd84743))

### ⚙️ Miscellaneous Tasks

- Timeout - ([26b39fe](https://github.com/aignostics/python-sdk/commit/26b39fe87d6589ffe71155a6e0d1c35e2b9a017d))


# [v0.2.49](https://github.com/aignostics/python-sdk/compare/v0.2.48..v0.2.49) - 2025-06-10

### ⛰️  Features

- *(application)* Dump zip with application schemata - ([8989c03](https://github.com/aignostics/python-sdk/commit/8989c03b5ab561defa3eb8154a00591c44afb876))


# [v0.2.48](https://github.com/aignostics/python-sdk/compare/v0.2.47..v0.2.48) - 2025-06-10

### 📚 Documentation

- Fix api docs generation - ([f3ea12d](https://github.com/aignostics/python-sdk/commit/f3ea12d87c4e629f40af4df08fc61bc64e460353))


# [v0.2.47](https://github.com/aignostics/python-sdk/compare/v0.2.46..v0.2.47) - 2025-06-10

### ⚙️ Miscellaneous Tasks

- *(test)* No warn on kill; output qupath inspect results - ([adbf0b4](https://github.com/aignostics/python-sdk/commit/adbf0b4ebee9ef17bb9a6478c70a988d87571097))


# [v0.2.46](https://github.com/aignostics/python-sdk/compare/v0.2.45..v0.2.46) - 2025-06-09

### ⚙️ Miscellaneous Tasks

- Zip on release - ([638f993](https://github.com/aignostics/python-sdk/commit/638f993d2e95e539203bca7da22ed2cb9d6ba2ae))


# [v0.2.45](https://github.com/aignostics/python-sdk/compare/v0.2.44..v0.2.45) - 2025-06-09

### ⚙️ Miscellaneous Tasks

- *(deps)* Bump actions in gha and duckdb - ([c731c68](https://github.com/aignostics/python-sdk/commit/c731c68ac789e9e1a015b7223b8edd88e7876c6e))


# [v0.2.44](https://github.com/aignostics/python-sdk/compare/v0.2.43..v0.2.44) - 2025-06-09

### ⚙️ Miscellaneous Tasks

- Encoding for win32 on package publish - ([dce9f28](https://github.com/aignostics/python-sdk/commit/dce9f28094b9315b395ef81d39f29fa4a303bb68))


# [v0.2.43](https://github.com/aignostics/python-sdk/compare/v0.2.42..v0.2.43) - 2025-06-09

### ⚙️ Miscellaneous Tasks

- *(QuPath)* Check QuPath is launched in install to inspect test - ([526417c](https://github.com/aignostics/python-sdk/commit/526417cad780449ba80f894ac55889fe43491114))
- *(QuPath)* E2E test from install via run to inspect - ([f35a89d](https://github.com/aignostics/python-sdk/commit/f35a89d26e9a2408e43c67d638866500b3a2c2c2))


# [v0.2.42](https://github.com/aignostics/python-sdk/compare/v0.2.41..v0.2.42) - 2025-06-09

### ⚙️ Miscellaneous Tasks

- Release workflow - ([ccaef74](https://github.com/aignostics/python-sdk/commit/ccaef740ed807288ebb9b705af0cd160635949cb))


# [v0.2.41](https://github.com/aignostics/python-sdk/compare/v0.2.40..v0.2.41) - 2025-06-09


# [v0.2.40](https://github.com/aignostics/python-sdk/compare/v0.2.39..v0.2.40) - 2025-06-09

### ⛰️  Features

- *(native)* Spike for native (compiled) apps - ([289ae77](https://github.com/aignostics/python-sdk/commit/289ae77b90526adb7ec4bd7511a9c271e72c8e54))
- *(system)* Allow to unmask secrets - ([289ae77](https://github.com/aignostics/python-sdk/commit/289ae77b90526adb7ec4bd7511a9c271e72c8e54))

### 🚜 Refactor

- *(gui)* Consistent use of spinners and awaiting - ([9ef72b2](https://github.com/aignostics/python-sdk/commit/9ef72b2aa367660c5a5a140ea162eb32f0f5271e))
- *(qupath)* Using groovy, not paquo; GPL removed from allow-list when license auditing - ([289ae77](https://github.com/aignostics/python-sdk/commit/289ae77b90526adb7ec4bd7511a9c271e72c8e54))
- *(qupath)* Using groovy, not paquo - ([9ef72b2](https://github.com/aignostics/python-sdk/commit/9ef72b2aa367660c5a5a140ea162eb32f0f5271e))
- *(various)* Consistent use of spinners and awaiting; sentry and logfire can now be removed as dependencies - ([289ae77](https://github.com/aignostics/python-sdk/commit/289ae77b90526adb7ec4bd7511a9c271e72c8e54))

### ⚙️ Miscellaneous Tasks

- *(cross-platform)* Now matrix testing on win-amd64, win-arm64, linux-amd64, linux-arm64, mac-arm64; related fixes - ([289ae77](https://github.com/aignostics/python-sdk/commit/289ae77b90526adb7ec4bd7511a9c271e72c8e54))
- *(native)* Include version in macOS bundle - ([7155bbb](https://github.com/aignostics/python-sdk/commit/7155bbb34ebd6656ce68b0231616a21dbcc4eb6c))


# [v0.2.39](https://github.com/aignostics/python-sdk/compare/v0.2.38..v0.2.39) - 2025-06-06

### 🐛 Bug Fixes

- *(platform)* Refresh token repl - ([0ab8f66](https://github.com/aignostics/python-sdk/commit/0ab8f66b2b26cca7de13112ef1753267ec6f845d))


# [v0.2.38](https://github.com/aignostics/python-sdk/compare/v0.2.37..v0.2.38) - 2025-06-06

### 🚜 Refactor

- *(general)* Central place for defining supported WSI extensions - ([b7a886a](https://github.com/aignostics/python-sdk/commit/b7a886a0bc09d51a6090c113e5cbfbac9ca47a61))
- *(info)* Consistently show settings - ([b7a886a](https://github.com/aignostics/python-sdk/commit/b7a886a0bc09d51a6090c113e5cbfbac9ca47a61))


# [v0.2.37](https://github.com/aignostics/python-sdk/compare/v0.2.36..v0.2.37) - 2025-06-06

### ⛰️  Features

- *(bucket)* Make expiration time of upload/download properly configurable, and include in info - ([72a0991](https://github.com/aignostics/python-sdk/commit/72a099154ec99a4cb8d14282494c9c00a056e651))

### 🐛 Bug Fixes

- *(bucket)* Use longer 7d expiration time for signed upload urls instead of 1h - ([72a0991](https://github.com/aignostics/python-sdk/commit/72a099154ec99a4cb8d14282494c9c00a056e651))


# [v0.2.36](https://github.com/aignostics/python-sdk/compare/v0.2.34..v0.2.36) - 2025-06-05

### 📚 Documentation

- Generate - ([9021d73](https://github.com/aignostics/python-sdk/commit/9021d73dfdd6ff3e85cc17f633bddbf2f5c4170d))

### 🛡️ Security

- *(jupyter)* CVE-2025-30167 rel. jupyter-core - ([5a595a3](https://github.com/aignostics/python-sdk/commit/5a595a3a5a2cf1d49490d7190d070a59e3590453))


# [v0.2.34](https://github.com/aignostics/python-sdk/compare/v0.2.33..v0.2.34) - 2025-06-04

### ⚙️ Miscellaneous Tasks

- Workaround missing scheme in proxy config - ([9474f0d](https://github.com/aignostics/python-sdk/commit/9474f0dca775508e5e9caac8f9f68b8348987c66))


# [v0.2.33](https://github.com/aignostics/python-sdk/compare/v0.2.32..v0.2.33) - 2025-06-03

### 🚜 Refactor

- *(application)* Don't allow to close download dialog by clicking outside - ([3524d4b](https://github.com/aignostics/python-sdk/commit/3524d4b54849a60270d48213dde94de7909defcc))


# [v0.2.32](https://github.com/aignostics/python-sdk/compare/v0.2.31..v0.2.32) - 2025-06-03

### 🎨 Styling

- *(header,run_describe)* Simplify a bit to make space - ([f2af6c0](https://github.com/aignostics/python-sdk/commit/f2af6c0a19217551b250e442d0a282a9e4c8d5ef))


# [v0.2.31](https://github.com/aignostics/python-sdk/compare/v0.2.30..v0.2.31) - 2025-06-03

### ⛰️  Features

- *(QuPath)* Support updating QuPath - ([7911353](https://github.com/aignostics/python-sdk/commit/7911353fafb74c64aaf73aacbde5c23e6e42baa0))
- *(QuPath)* Use 0.6.0-rc5 - ([7911353](https://github.com/aignostics/python-sdk/commit/7911353fafb74c64aaf73aacbde5c23e6e42baa0))
- *(QuPath)* Deeper info - ([7911353](https://github.com/aignostics/python-sdk/commit/7911353fafb74c64aaf73aacbde5c23e6e42baa0))

### 🚜 Refactor

- *(QuPath)* 20x speed up writing polygons by switching from paquo to groovy - ([7911353](https://github.com/aignostics/python-sdk/commit/7911353fafb74c64aaf73aacbde5c23e6e42baa0))
- *(progress)* Faster progress bars - ([7911353](https://github.com/aignostics/python-sdk/commit/7911353fafb74c64aaf73aacbde5c23e6e42baa0))


# [v0.2.30](https://github.com/aignostics/python-sdk/compare/v0.2.27..v0.2.30) - 2025-06-02

### ⛰️  Features

- *(System)* Enable to enable/disable diagnostics in UI - ([78ce511](https://github.com/aignostics/python-sdk/commit/78ce511f563e895e83e04a4b71276c77dd60e3b9))

### 🐛 Bug Fixes

- *(Windows)* Sanitize paths so they don't contain a colon if not drive letter - ([37dce20](https://github.com/aignostics/python-sdk/commit/37dce20076ef238f3baafbcc53186e50a44c0b60))

### 🚜 Refactor

- *(System)* Move settings logic to service - ([78ce511](https://github.com/aignostics/python-sdk/commit/78ce511f563e895e83e04a4b71276c77dd60e3b9))

### 🎨 Styling

- *(System)* Minimal love for Settings and Info page - ([78ce511](https://github.com/aignostics/python-sdk/commit/78ce511f563e895e83e04a4b71276c77dd60e3b9))


# [v0.2.27](https://github.com/aignostics/python-sdk/compare/v0.2.26..v0.2.27) - 2025-06-01

### ⚙️ Miscellaneous Tasks

- Test of notebook, race - ([b5771a9](https://github.com/aignostics/python-sdk/commit/b5771a9f16b489499fc53da12a6e3d9e578c9f87))


# [v0.2.26](https://github.com/aignostics/python-sdk/compare/v0.2.25..v0.2.26) - 2025-06-01

### 🚜 Refactor

- *(sonarqube)* Annotate generator - ([cea7fde](https://github.com/aignostics/python-sdk/commit/cea7fdec17fff5064c081933b36b6a076b3ce2d0))

### ⚙️ Miscellaneous Tasks

- Non-sequential as there is a dependent one - ([fe19b97](https://github.com/aignostics/python-sdk/commit/fe19b9773f160963c9b39a4a53e9babea49764af))


# [v0.2.25](https://github.com/aignostics/python-sdk/compare/v0.2.23..v0.2.25) - 2025-06-01

### ⛰️  Features

- *(marimo)* Marimo open with downloaded results - ([d8742d6](https://github.com/aignostics/python-sdk/commit/d8742d62304b4448239ab47b9ce8618096867a6f))
- *(marimo)* Open marimo from extension page - ([d8742d6](https://github.com/aignostics/python-sdk/commit/d8742d62304b4448239ab47b9ce8618096867a6f))


# [v0.2.23](https://github.com/aignostics/python-sdk/compare/v0.2.22..v0.2.23) - 2025-06-01

### 🚜 Refactor

- *(wsi)* Simplify further - ([c679a2f](https://github.com/aignostics/python-sdk/commit/c679a2fe1f66e20b88d114a7f1f80e56040efef6))
- *(wsi)* Simplify, and fallback image - ([e494f84](https://github.com/aignostics/python-sdk/commit/e494f84fd9a7a2a5bcc699085570e3f946b33638))

### ⚙️ Miscellaneous Tasks

- *(wsi)* Adapt tests given fallback - ([8d34608](https://github.com/aignostics/python-sdk/commit/8d346088e0a7e2ab03282de93fd4cb83b4270ef7))
- Make gui test more reliable - ([17880af](https://github.com/aignostics/python-sdk/commit/17880afa3f4a84d1a6173293f2ea3c59f2cd8a1b))


# [v0.2.22](https://github.com/aignostics/python-sdk/compare/v0.2.13..v0.2.22) - 2025-06-01

### ⛰️  Features

- *(QuPath)* Create project from results - ([1a31655](https://github.com/aignostics/python-sdk/commit/1a31655771b80bbd9fdc5e6f7d96f67b394562b6))
- *(System)* Manipulate dotenv via CLI, including enable/disabling http proxy, enabling/disabling remote diagnostics - ([1a31655](https://github.com/aignostics/python-sdk/commit/1a31655771b80bbd9fdc5e6f7d96f67b394562b6))
- *(notebook)* Extension page - ([1a31655](https://github.com/aignostics/python-sdk/commit/1a31655771b80bbd9fdc5e6f7d96f67b394562b6))

### 🚜 Refactor

- *(application)* Cleanup - ([1a31655](https://github.com/aignostics/python-sdk/commit/1a31655771b80bbd9fdc5e6f7d96f67b394562b6))

### ⚡ Performance

- *(GUI)* Significantly reduced bootup time, and page load performance - ([1a31655](https://github.com/aignostics/python-sdk/commit/1a31655771b80bbd9fdc5e6f7d96f67b394562b6))

### 🎨 Styling

- *(QuPath)* Some polish for extension page - ([1a31655](https://github.com/aignostics/python-sdk/commit/1a31655771b80bbd9fdc5e6f7d96f67b394562b6))

### ⚙️ Miscellaneous Tasks

- *(tests)* Improved coverage - ([1a31655](https://github.com/aignostics/python-sdk/commit/1a31655771b80bbd9fdc5e6f7d96f67b394562b6))


# [v0.2.13](https://github.com/aignostics/python-sdk/compare/v0.2.12..v0.2.13) - 2025-05-27

### 🚜 Refactor

- Styling of ui theme - ([b87ffb6](https://github.com/aignostics/python-sdk/commit/b87ffb67df666ea0f987b341321c6c560f1113f2))

### 📚 Documentation

- Reorder - ([c3c15b7](https://github.com/aignostics/python-sdk/commit/c3c15b7ddc6ff71caa3cc556da0ff2053209adef))


# [v0.2.12](https://github.com/aignostics/python-sdk/compare/v0.2.11..v0.2.12) - 2025-05-26

### 🐛 Bug Fixes

- *(cli)* List runs count - ([8e113c1](https://github.com/aignostics/python-sdk/commit/8e113c1560fee92057ba4bcce5c81e42bfeffacb))

### 🚜 Refactor

- Simplify, removing noruns - ([274e685](https://github.com/aignostics/python-sdk/commit/274e6858f5a8a3332e4c49421e5c3a0b48d46bef))

### 📚 Documentation

- Update - ([b861b88](https://github.com/aignostics/python-sdk/commit/b861b88bfde53e6493fa12d4b3ea5ccfbf4d3410))
- Reorder - ([b9399b3](https://github.com/aignostics/python-sdk/commit/b9399b33c8eedf76aa2f3f8c6421d139dc6b0243))
- Fix broken link - ([3dbaace](https://github.com/aignostics/python-sdk/commit/3dbaace2a4ca769c7c7b103dfbe51c4b52a5a843))


# [v0.2.11](https://github.com/aignostics/python-sdk/compare/v0.2.10..v0.2.11) - 2025-05-26

### 🎨 Styling

- Naming of navigation points - ([665edc2](https://github.com/aignostics/python-sdk/commit/665edc2dfd9fd8dff4a734f18c8aa01d6182dbc6))


# [v0.2.10](https://github.com/aignostics/python-sdk/compare/v0.2.9..v0.2.10) - 2025-05-26


# [v0.2.9](https://github.com/aignostics/python-sdk/compare/v0.2.8..v0.2.9) - 2025-05-26

### 🚜 Refactor

- Fail properly when starting GUI while settings not configured - ([b2d534e](https://github.com/aignostics/python-sdk/commit/b2d534e0479ad94f02cdf57c961c7fb3a4145123))


# [v0.2.8](https://github.com/aignostics/python-sdk/compare/v0.2.7..v0.2.8) - 2025-05-26

### 🐛 Bug Fixes

- Force .json for geojson - ([214d28e](https://github.com/aignostics/python-sdk/commit/214d28e101a3a3909be1668191644cf83f57019d))


# [v0.2.7](https://github.com/aignostics/python-sdk/compare/v0.2.6..v0.2.7) - 2025-05-26

### 🚜 Refactor

- Simplify - ([05dd892](https://github.com/aignostics/python-sdk/commit/05dd89204bd418f3507b9c7c8737c0c021b6be89))

### ⚙️ Miscellaneous Tasks

- Adapt test to work with python 3.11 - ([4f636a8](https://github.com/aignostics/python-sdk/commit/4f636a8c6dd51ae6bbae5a4ef7c05a625b7fd66e))


# [v0.2.6](https://github.com/aignostics/python-sdk/compare/v0.2.5..v0.2.6) - 2025-05-26

### ⚙️ Miscellaneous Tasks

- Fix test - ([b2741e0](https://github.com/aignostics/python-sdk/commit/b2741e02e7769af9b4a590ffc0a90bc6dbcc215d))


# [v0.2.5](https://github.com/aignostics/python-sdk/compare/v0.2.4..v0.2.5) - 2025-05-26

### 📚 Documentation

- Update - ([e1317d3](https://github.com/aignostics/python-sdk/commit/e1317d38a71877164f508b3021b432a816d3e2fe))


# [v0.2.4](https://github.com/aignostics/python-sdk/compare/v0.2.3..v0.2.4) - 2025-05-26

### ⚙️ Miscellaneous Tasks

- Fix test - ([903f9c8](https://github.com/aignostics/python-sdk/commit/903f9c8adcd7e3c96915edb742b3e1c609440b0a))


# [v0.2.3](https://github.com/aignostics/python-sdk/compare/v0.2.2..v0.2.3) - 2025-05-26

### 📚 Documentation

- Additional pages for read the docs (rtd) - ([c419e12](https://github.com/aignostics/python-sdk/commit/c419e1205a01f8e15700a5ce0bcfc6eeb0c5c056))


# [v0.2.2](https://github.com/aignostics/python-sdk/compare/v0.2.1..v0.2.2) - 2025-05-23

### 📚 Documentation

- Polish incl. updated assets - ([6cd7bbd](https://github.com/aignostics/python-sdk/commit/6cd7bbd939751b42baff5154d9922d77ec8b11fe))


# [v0.2.1](https://github.com/aignostics/python-sdk/compare/v0.2.0..v0.2.1) - 2025-05-23

### 📚 Documentation

- Polish readme intro and oe - ([8c89ab9](https://github.com/aignostics/python-sdk/commit/8c89ab9e5f498585405da461a406083b46d84288))
- Logo - ([eb777b5](https://github.com/aignostics/python-sdk/commit/eb777b5925abc4e601761af3c9a335e0577e4db1))



### ⛰️  Features

- Aignostics Launchpad, Aignostics CLI, Aignostics Client - ([04e23dc](https://github.com/aignostics/python-sdk/commit/04e23dc3ccd0cb287319e6c251ca3e229866e66e))

### ⚙️ Miscellaneous Tasks

- Initial commit - ([bab4425](https://github.com/aignostics/python-sdk/commit/bab442520015b96dd922a0a4fc3a87b920f3fb94))



* @helmut-hoffer-von-ankershoffen made their first contribution


