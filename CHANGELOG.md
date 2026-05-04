[🔬 Aignostics Python SDK](https://aignostics.readthedocs.io/en/latest/)

# [v1.3.0](https://github.com/aignostics/python-sdk/compare/v1.2.0..v1.3.0) - 2026-05-04

### ⛰️  Features

- *(application)* Add OTHER as valid tissue value in GUI metadata grid ([#522](https://github.com/aignostics/python-sdk/pull/522)) - ([15a6063](https://github.com/aignostics/python-sdk/commit/15a60633176dea19d39774743e6cf82b1427b531))
- *(platform)* Add organization parameter to OAuth authorization redirect ([#550](https://github.com/aignostics/python-sdk/pull/550)) - ([321d4de](https://github.com/aignostics/python-sdk/commit/321d4de86ee42fffddc7e956cac6fd7b018e754e))
- *(platform)* Add organization parameter to OAuth authorization redirect - ([321d4de](https://github.com/aignostics/python-sdk/commit/321d4de86ee42fffddc7e956cac6fd7b018e754e))
- *(platform)* Add 'for_organization' to list all runs of an org ([#510](https://github.com/aignostics/python-sdk/pull/510)) - ([3f06055](https://github.com/aignostics/python-sdk/commit/3f06055d240d6fb24e7b32f320265cfe94fe5f2a))
- *(utils, platform)* Add DEGRADED state to Health model - ([21e95ba](https://github.com/aignostics/python-sdk/commit/21e95ba73d2500dc1cdc9647fc9c393da4b939e0))
- Oliver Meyer <42039965+olivermeyer@users.noreply.github.com> - ([321d4de](https://github.com/aignostics/python-sdk/commit/321d4de86ee42fffddc7e956cac6fd7b018e754e))
- Claude Sonnet 4.6 <noreply@anthropic.com> - ([15a6063](https://github.com/aignostics/python-sdk/commit/15a60633176dea19d39774743e6cf82b1427b531))
- Make BaseService methods async ([#474](https://github.com/aignostics/python-sdk/pull/474)) - ([84c826a](https://github.com/aignostics/python-sdk/commit/84c826a0f324d8bcd4353d96ec0549ce7ecdeb12))

### 🐛 Bug Fixes

- *(application)* Sort query results by submitted_at before limit - ([a2480ed](https://github.com/aignostics/python-sdk/commit/a2480ed34b7a128ed8ecd3bdfa2e70f7866242a6))
- *(ci)* Fix publish-release workflow - ([a97ccb9](https://github.com/aignostics/python-sdk/commit/a97ccb903f57e2c7f76b8bc3e9aaf8a6eaeef59e))
- *(ci)* Pin HETA version in E2E test - ([d124c17](https://github.com/aignostics/python-sdk/commit/d124c173981ddab8aa401de9435c2bdb63e8ffaf))
- *(ci)* Include v prefix in release_version output for Ketryx - ([6d7720f](https://github.com/aignostics/python-sdk/commit/6d7720fbf87147b9b073f9c66bfcc03f9cebc2db))
- *(ci)* Replace \d with [0-9] in semver validation grep pattern - ([62aa11f](https://github.com/aignostics/python-sdk/commit/62aa11fc96ec6826e99aef7c8503145fe12bece1))
- *(ci)* Prevent PYTHONHOME from leaking into nox sub-sessions on Windows - ([adb1fa0](https://github.com/aignostics/python-sdk/commit/adb1fa098b7f26122895d38486e641acfed2b8f1))
- *(deps)* Update dependency packaging to v26 - ([6f1df69](https://github.com/aignostics/python-sdk/commit/6f1df69cbda038a2647c6b8b4e0e00153098b87b))
- *(deps)* Update minor and patch dependencies - ([d1f565e](https://github.com/aignostics/python-sdk/commit/d1f565efc81ac3b82658ff872f222bba5f2eaace))
- *(system)* Replace uptime with psutil - ([346a9f6](https://github.com/aignostics/python-sdk/commit/346a9f67dc15236e4cc4d776eed27c70c16f7176))
- Claude Sonnet 4.6 <noreply@anthropic.com> - ([6d7720f](https://github.com/aignostics/python-sdk/commit/6d7720fbf87147b9b073f9c66bfcc03f9cebc2db))
- Claude Opus 4.6 <noreply@anthropic.com> - ([adb1fa0](https://github.com/aignostics/python-sdk/commit/adb1fa098b7f26122895d38486e641acfed2b8f1))
- Use renovate vulnerabiltyAlerts ([#549](https://github.com/aignostics/python-sdk/pull/549)) - ([3a77e30](https://github.com/aignostics/python-sdk/commit/3a77e30a28ac67f6e33c1be264c9f17179949177))
- Update requests dependency to 2.33.0 for CVE-2026-25645 compliance ([#511](https://github.com/aignostics/python-sdk/pull/511)) - ([8ad550d](https://github.com/aignostics/python-sdk/commit/8ad550d252bc14897bfd053c6b614f92f21af96e))
- Add CVE-2026-4539 to the list of ignored vulnerabilities in noxfile ([#508](https://github.com/aignostics/python-sdk/pull/508)) - ([1e2e0a5](https://github.com/aignostics/python-sdk/commit/1e2e0a5874aa21db5c5289c660e95f93c2ef083b))
- Prevent microsecond drift when offsets are equal in e2e test ([#504](https://github.com/aignostics/python-sdk/pull/504)) - ([e59a5db](https://github.com/aignostics/python-sdk/commit/e59a5dbf5e7d9c6f6ad50383c2b39f9528745e42))
- Prevent microsecond drift when offsets are equal in e2e test - ([e59a5db](https://github.com/aignostics/python-sdk/commit/e59a5dbf5e7d9c6f6ad50383c2b39f9528745e42))
- System health exits with 0 when degraded - ([d24c285](https://github.com/aignostics/python-sdk/commit/d24c28504b525dd8fee91e55c7dc15a354560db9))

### 🚜 Refactor

- *(tests)* Extract submitted_run context manager - ([8cf4c1d](https://github.com/aignostics/python-sdk/commit/8cf4c1d7932d154b118a95ef2b40cf8166ecd53f))

### 📚 Documentation

- *(spec)* Document organization parameter in platform service specification - ([321d4de](https://github.com/aignostics/python-sdk/commit/321d4de86ee42fffddc7e956cac6fd7b018e754e))
- *(specs)* Document scheduling support in SPEC-APPLICATION-SERVICE - ([299f66b](https://github.com/aignostics/python-sdk/commit/299f66bc3b121c22b29617233cd95461a54e5951))
- *(specs)* Update specs for for_organization list flag - ([ad8b55c](https://github.com/aignostics/python-sdk/commit/ad8b55c7e2ba8bf7353a9b42c67c962915944bf4))
- Claude Sonnet 4.6 (1M context) <noreply@anthropic.com> - ([299f66b](https://github.com/aignostics/python-sdk/commit/299f66bc3b121c22b29617233cd95461a54e5951))
- Claude Sonnet 4.6 <noreply@anthropic.com> - ([ad8b55c](https://github.com/aignostics/python-sdk/commit/ad8b55c7e2ba8bf7353a9b42c67c962915944bf4))
- Link risks to SHRs - ([69740ad](https://github.com/aignostics/python-sdk/commit/69740ad385d0d0b38318b7ed381d4fd3bcfe78a9))
- Remove dates from specs - ([027657b](https://github.com/aignostics/python-sdk/commit/027657b66ff216bee02143f8947f5546b8e530fb))
- Remove README alpha note and run make docs - ([deef45a](https://github.com/aignostics/python-sdk/commit/deef45af598a7de81ebbbdd5c47d0d46b12ad28e))

### ⚡ Performance

- *(application)* Replace like_regex with == for tag filtering ([#516](https://github.com/aignostics/python-sdk/pull/516)) - ([aacb20a](https://github.com/aignostics/python-sdk/commit/aacb20aed62e4a08d1756282a340946fcdd90b51))
- *(application)* Replace like_regex with == for tag filtering in application_runs - ([aacb20a](https://github.com/aignostics/python-sdk/commit/aacb20aed62e4a08d1756282a340946fcdd90b51))
- Claude Opus 4.6 (1M context) <noreply@anthropic.com> - ([aacb20a](https://github.com/aignostics/python-sdk/commit/aacb20aed62e4a08d1756282a340946fcdd90b51))

### 🧪 Testing

- Increase deadline for flaky tests - ([fa90a99](https://github.com/aignostics/python-sdk/commit/fa90a9938ea3138fc084c28689bf3e51865db7ba))
- Run heavy test on ubuntu-latest only - ([01e1ec2](https://github.com/aignostics/python-sdk/commit/01e1ec2ea0aed60891056da1a87453fd01d3f1f4))
- Split health CLI format tests from live platform monitoring - ([1360d9a](https://github.com/aignostics/python-sdk/commit/1360d9a2b27defb9a6ab01fffc97ca690e8ee50f))
- Claude Sonnet 4.6 <noreply@anthropic.com> - ([1360d9a](https://github.com/aignostics/python-sdk/commit/1360d9a2b27defb9a6ab01fffc97ca690e8ee50f))
- Increase timeout for test_cli_run_submit_succeeds_when_system_degraded_and_no_force - ([f2fb6d1](https://github.com/aignostics/python-sdk/commit/f2fb6d18d422ec4c706daebf132e0f4a273f3bd7))
- Limit list operation in CLI test - ([e4dfc98](https://github.com/aignostics/python-sdk/commit/e4dfc98b9f640cc963eeaf33dc7e025be697323c))

### ⚙️ Miscellaneous Tasks

- *(OP-2780)* Pin GitHub Actions to commit SHA - ([48015bc](https://github.com/aignostics/python-sdk/commit/48015bc81b4d98dc9346c580e29bdd60646f80a1))
- *(deps)* Upgrade pip to 26.1 - ([a86898b](https://github.com/aignostics/python-sdk/commit/a86898bd3539c8d2083db70316094debce43ea2b))
- *(deps)* Bump nbconvert from 7.17.0 to 7.17.1 ([#553](https://github.com/aignostics/python-sdk/pull/553)) - ([b75aaf2](https://github.com/aignostics/python-sdk/commit/b75aaf23a0bd2deefae3dad1fe9479475b78217b))
- *(deps)* Bump python-dotenv from 1.2.1 to 1.2.2 ([#554](https://github.com/aignostics/python-sdk/pull/554)) - ([0b5a4c4](https://github.com/aignostics/python-sdk/commit/0b5a4c4fc42e692ab0014fc0b489f4b0d5eb91a7))
- *(deps)* Bump authlib from 1.6.9 to 1.6.11 ([#544](https://github.com/aignostics/python-sdk/pull/544)) - ([5fd0054](https://github.com/aignostics/python-sdk/commit/5fd005402df4eab3ebd36e9fbab58a51908dbe01))
- *(deps)* Bump python-multipart from 0.0.22 to 0.0.26 ([#543](https://github.com/aignostics/python-sdk/pull/543)) - ([eeffb59](https://github.com/aignostics/python-sdk/commit/eeffb5974f6d64f056a3734db25458882e168382))
- *(deps)* Bump cryptography from 46.0.6 to 46.0.7 - ([2aa57c7](https://github.com/aignostics/python-sdk/commit/2aa57c764573781aeeb634c9c4a381f1bfd5ea78))
- *(deps)* Update github actions - ([a9aa0f9](https://github.com/aignostics/python-sdk/commit/a9aa0f9242dd343bdaec4932bcc09496281c7b6b))
- *(deps)* Bump pygments from 2.19.2 to 2.20.0 - ([b54f245](https://github.com/aignostics/python-sdk/commit/b54f245e73b94b0bcb687da0e280cd61bd9c0638))
- *(deps)* Bump cryptography from 46.0.5 to 46.0.6 - ([7950c3f](https://github.com/aignostics/python-sdk/commit/7950c3fdcdc3bb257f4d04681c9cb3352393b31c))
- *(deps)* Update anthropics/claude-code-action action to v1.0.77 ([#503](https://github.com/aignostics/python-sdk/pull/503)) - ([dc400d1](https://github.com/aignostics/python-sdk/commit/dc400d121c3160ce9fde2b9c8351d411ff93cf2f))
- *(deps)* Bump pydicom from 3.0.1 to 3.0.2 ([#502](https://github.com/aignostics/python-sdk/pull/502)) - ([cec28b1](https://github.com/aignostics/python-sdk/commit/cec28b19543a8c3655c6ec472b4d765af2d29528))
- *(deps)* Bump ujson from 5.11.0 to 5.12.0 - ([c2fb241](https://github.com/aignostics/python-sdk/commit/c2fb2414197f35b9dd6f6cc025cd6e321cfbc4f6))
- *(deps)* Bump pyasn1 from 0.6.2 to 0.6.3 ([#490](https://github.com/aignostics/python-sdk/pull/490)) - ([fe0ca62](https://github.com/aignostics/python-sdk/commit/fe0ca6261148efca9021d988064ee14e4fde0d48))
- *(deps)* Bump orjson from 3.11.5 to 3.11.6 - ([3f583ca](https://github.com/aignostics/python-sdk/commit/3f583cae2923083acba86eb91b22d2ebdcb2e898))
- *(deps)* Bump pyjwt from 2.10.1 to 2.12.0 - ([3638ebc](https://github.com/aignostics/python-sdk/commit/3638ebccabb947c7720e61d7752484df75a2b0ed))
- *(deps)* Bump tornado from 6.5.2 to 6.5.5 - ([f72a15b](https://github.com/aignostics/python-sdk/commit/f72a15bc111a52f30b4bfe7e0527fc2ed0ef271d))
- Auto-enable very_long_running tests on release branch pushes - ([b0eefcc](https://github.com/aignostics/python-sdk/commit/b0eefcc39a0980a76c7317b2d5ae2f53fe5de745))
- Claude Sonnet 4.6 <noreply@anthropic.com> - ([b0eefcc](https://github.com/aignostics/python-sdk/commit/b0eefcc39a0980a76c7317b2d5ae2f53fe5de745))
- Run CI/CD for PRs targeting release/v* branches - ([2eb340f](https://github.com/aignostics/python-sdk/commit/2eb340f602eab9f1162cc97109c4b600db0d641c))
- Pass release version to ketryx on release/v* branches - ([50ffbc4](https://github.com/aignostics/python-sdk/commit/50ffbc4f38065b617d78b045f4353d92ec5180b2))
- Add concurrency to release workflows - ([a2fd65f](https://github.com/aignostics/python-sdk/commit/a2fd65f5c5128ee53342aab88f4e2decdeec5685))
- Update release strategy - ([c06bf1d](https://github.com/aignostics/python-sdk/commit/c06bf1df9189d6269f194300f820380b67bfafae))
- Nbconvert - ([b75aaf2](https://github.com/aignostics/python-sdk/commit/b75aaf23a0bd2deefae3dad1fe9479475b78217b))
- Dependabot[bot] <support@github.com> - ([b75aaf2](https://github.com/aignostics/python-sdk/commit/b75aaf23a0bd2deefae3dad1fe9479475b78217b))
- Dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com> - ([b75aaf2](https://github.com/aignostics/python-sdk/commit/b75aaf23a0bd2deefae3dad1fe9479475b78217b))
- Python-dotenv - ([0b5a4c4](https://github.com/aignostics/python-sdk/commit/0b5a4c4fc42e692ab0014fc0b489f4b0d5eb91a7))
- Authlib - ([5fd0054](https://github.com/aignostics/python-sdk/commit/5fd005402df4eab3ebd36e9fbab58a51908dbe01))
- Python-multipart - ([eeffb59](https://github.com/aignostics/python-sdk/commit/eeffb5974f6d64f056a3734db25458882e168382))
- Update CODEOWNERS ([#501](https://github.com/aignostics/python-sdk/pull/501)) - ([e1b914f](https://github.com/aignostics/python-sdk/commit/e1b914fef6014b9379738ae6af8160c32b6efeeb))
- Moritz Krügener <kruegener@users.noreply.github.com> - ([e1b914f](https://github.com/aignostics/python-sdk/commit/e1b914fef6014b9379738ae6af8160c32b6efeeb))
- Cryptography - ([2aa57c7](https://github.com/aignostics/python-sdk/commit/2aa57c764573781aeeb634c9c4a381f1bfd5ea78))
- Pygments - ([b54f245](https://github.com/aignostics/python-sdk/commit/b54f245e73b94b0bcb687da0e280cd61bd9c0638))
- Bump Python to 3.14.3 - ([442c2a8](https://github.com/aignostics/python-sdk/commit/442c2a8903645b6d0b26b57db2240a19697d9d57))
- Update .python-version to 3.14.2 - ([aacb20a](https://github.com/aignostics/python-sdk/commit/aacb20aed62e4a08d1756282a340946fcdd90b51))
- Use SAMIA run artifact file endpoint to download artifacts ([#507](https://github.com/aignostics/python-sdk/pull/507)) - ([d552c89](https://github.com/aignostics/python-sdk/commit/d552c8968890b2c15edf0e6652ef3c2f15684477))
- Update renovate schedule - ([ba74ebe](https://github.com/aignostics/python-sdk/commit/ba74ebe7e155d6e6e3207ffa46a4387a912b4948))
- Renovate[bot] <29139614+renovate[bot]@users.noreply.github.com> - ([dc400d1](https://github.com/aignostics/python-sdk/commit/dc400d121c3160ce9fde2b9c8351d411ff93cf2f))
- Pydicom - ([cec28b1](https://github.com/aignostics/python-sdk/commit/cec28b19543a8c3655c6ec472b4d765af2d29528))
- Use scheduling payload when creating runs - ([8f4445b](https://github.com/aignostics/python-sdk/commit/8f4445b9a9847f755a0f8f390223a37af171143c))
- Bump FastMCP to v3.x and make the necessary changes to support it ([#425](https://github.com/aignostics/python-sdk/pull/425)) - ([2509265](https://github.com/aignostics/python-sdk/commit/2509265b518bf9a4e59d3e0195ebe901a9414a87))
- Oliver Meyer <42039965+olivermeyer@users.noreply.github.com> - ([2509265](https://github.com/aignostics/python-sdk/commit/2509265b518bf9a4e59d3e0195ebe901a9414a87))
- Run SonarCloud analysis immediately on PRs - ([d2b4f88](https://github.com/aignostics/python-sdk/commit/d2b4f8872fd0f9612b1a308183f4d75fa2bff56f))
- Update test suite name when reporting failures - ([e409213](https://github.com/aignostics/python-sdk/commit/e40921358c0b711586cdb2a81f5f72daed13837c))
- Ujson - ([647f75b](https://github.com/aignostics/python-sdk/commit/647f75b1e151578a2c45a3b9010cbd63d5ebb338))
- Run all tests even on failure in previous steps ([#481](https://github.com/aignostics/python-sdk/pull/481)) - ([485f86f](https://github.com/aignostics/python-sdk/commit/485f86f5a232538dedfdeb409203da35743241ce))
- Pyasn1 - ([fe0ca62](https://github.com/aignostics/python-sdk/commit/fe0ca6261148efca9021d988064ee14e4fde0d48))
- Update Renovate and Dependabot config ([#467](https://github.com/aignostics/python-sdk/pull/467)) - ([4a1ef54](https://github.com/aignostics/python-sdk/commit/4a1ef543d5638cb780930f037bcd7dfb13678f51))
- Point CICD badge to main branch ([#480](https://github.com/aignostics/python-sdk/pull/480)) - ([e523bce](https://github.com/aignostics/python-sdk/commit/e523bce9f79a3780624717bdd31b7b6ddaf31f18))
- Orjson - ([889dab7](https://github.com/aignostics/python-sdk/commit/889dab7991e4388d95353dc65be624778cbb1c78))
- Pyjwt - ([aac87a3](https://github.com/aignostics/python-sdk/commit/aac87a3d7eac8f5c35982af29d9736d6ccfd70fe))
- Tornado - ([2413fa6](https://github.com/aignostics/python-sdk/commit/2413fa65fa8df68060b3be976150e527cea9ece6))

### 🛡️ Security

- *(deps)* Update dependency lxml to v6.1.0 [security] ([#556](https://github.com/aignostics/python-sdk/pull/556)) - ([12ec0c7](https://github.com/aignostics/python-sdk/commit/12ec0c73f1ca280fba7bb5612ae17dc699547e54))
- *(deps)* Update dependency uv to v0.11.6 [security] - ([32daf66](https://github.com/aignostics/python-sdk/commit/32daf6636288ec4a72762e73e441d151fdb131a2))
- *(deps)* Update dependency pytest to v9.0.3 [security] - ([269f072](https://github.com/aignostics/python-sdk/commit/269f07234d357386ac9e79fe432a2bc31b64b1f5))
- *(deps)* Update dependency pillow to v12.2.0 [security] - ([a510df1](https://github.com/aignostics/python-sdk/commit/a510df1f3fd6c8b131c91414feada9a0d4f2fb93))
- *(deps)* Update dependency marimo to v0.23.0 [security] - ([1b1b4b6](https://github.com/aignostics/python-sdk/commit/1b1b4b6b4dfdc88a65b745f4ebd6d63995b35b20))
- *(deps)* Update dependency aiohttp to v3.13.4 [security] - ([61d3472](https://github.com/aignostics/python-sdk/commit/61d34728e23c5ccc5a7801dab13e5bbba34d8b56))
- *(deps)* Update dependency fastmcp to v3.2.0 [security] - ([a9bccae](https://github.com/aignostics/python-sdk/commit/a9bccaed9037c8f9e06fffc2739259ef6ed8cf50))
- *(deps)* Update dependency nicegui to v3.9.0 [security] - ([65d553f](https://github.com/aignostics/python-sdk/commit/65d553f1aa592feb2ca01873c7645946c83410e9))
- *(security)* Prevent script and commit-message injections ([#512](https://github.com/aignostics/python-sdk/pull/512)) - ([24737e0](https://github.com/aignostics/python-sdk/commit/24737e05326a4ee304616fa442f2fa22b46a34f1))
- Renovate[bot] <29139614+renovate[bot]@users.noreply.github.com> - ([12ec0c7](https://github.com/aignostics/python-sdk/commit/12ec0c73f1ca280fba7bb5612ae17dc699547e54))
- Claude Sonnet 4.6 <noreply@anthropic.com> - ([24737e0](https://github.com/aignostics/python-sdk/commit/24737e05326a4ee304616fa442f2fa22b46a34f1))
- Merge pull request #498 from aignostics/renovate/pypi-nicegui-vulnerability - ([65d553f](https://github.com/aignostics/python-sdk/commit/65d553f1aa592feb2ca01873c7645946c83410e9))

### Build

- Decrease renovate noise ([#529](https://github.com/aignostics/python-sdk/pull/529)) - ([d4e2f75](https://github.com/aignostics/python-sdk/commit/d4e2f754912c57f4551b2c981ed8f2461d966dcd))



* @olivermeyer made their first contribution in [#561](https://github.com/aignostics/python-sdk/pull/561)
* @renovate[bot] made their first contribution in [#486](https://github.com/aignostics/python-sdk/pull/486)
* @dependabot[bot] made their first contribution in [#553](https://github.com/aignostics/python-sdk/pull/553)
* @santi698 made their first contribution in [#550](https://github.com/aignostics/python-sdk/pull/550)
* @aig-hannes made their first contribution in [#549](https://github.com/aignostics/python-sdk/pull/549)
* @omid-aignostics made their first contribution in [#522](https://github.com/aignostics/python-sdk/pull/522)
* @akunft made their first contribution in [#510](https://github.com/aignostics/python-sdk/pull/510)
* @zonorti made their first contribution in [#515](https://github.com/aignostics/python-sdk/pull/515)
* @arne-aignx made their first contribution
* @nahua-aignx made their first contribution in [#514](https://github.com/aignostics/python-sdk/pull/514)
* @marmarciniak95 made their first contribution in [#511](https://github.com/aignostics/python-sdk/pull/511)
* @neelay-aign made their first contribution in [#425](https://github.com/aignostics/python-sdk/pull/425)

# [1.2.0](https://github.com/aignostics/python-sdk/compare/v1.1.0..1.2.0) - 2026-03-10

### ⛰️  Features

- *(application)* Add option to summarize run describe. ([#414](https://github.com/aignostics/python-sdk/pull/414)) - ([a1d8cf1](https://github.com/aignostics/python-sdk/commit/a1d8cf1c5f85b47850203291ec6d146a5216598c))
- *(application)* Add option to summarize run status. - ([a1d8cf1](https://github.com/aignostics/python-sdk/commit/a1d8cf1c5f85b47850203291ec6d146a5216598c))
- *(dataset)* Add tenacity retry to IDCClient HTTP requests - ([7a3a593](https://github.com/aignostics/python-sdk/commit/7a3a593b1aa6cef8c3c2b392ba9e786a89863202))
- *(platform)* Add item filtering for fetching run results. ([#442](https://github.com/aignostics/python-sdk/pull/442)) - ([14e20b5](https://github.com/aignostics/python-sdk/commit/14e20b5cc25fcfb67224fb04bd2f20c046153a47))
- *(platform)* Add item filtering for fetching run results. - ([14e20b5](https://github.com/aignostics/python-sdk/commit/14e20b5cc25fcfb67224fb04bd2f20c046153a47))
- *(utils)* Split MCP and plugin requirements, add plugin integration tests - ([a8cf513](https://github.com/aignostics/python-sdk/commit/a8cf5139dfe419e42898ede34b7e672daa26c327))
- Claude Sonnet 4.6 <noreply@anthropic.com> - ([a8cf513](https://github.com/aignostics/python-sdk/commit/a8cf5139dfe419e42898ede34b7e672daa26c327))

### 🐛 Bug Fixes

- *(application)* Change default gpu type to a100 ([#446](https://github.com/aignostics/python-sdk/pull/446)) - ([1e0b848](https://github.com/aignostics/python-sdk/commit/1e0b8483cc804511cb160e64bc20bf4c86f9a8d9))
- *(application)* Make A100 default GPU type - ([1e0b848](https://github.com/aignostics/python-sdk/commit/1e0b8483cc804511cb160e64bc20bf4c86f9a8d9))
- *(application)* Include items in run describe --format=json ([#437](https://github.com/aignostics/python-sdk/pull/437)) - ([4079702](https://github.com/aignostics/python-sdk/commit/407970205b8ee69575753ccf70934321aeba9557))
- *(ci)* Ensure coverage and JUnit XML always generated even when tests fail - ([a31716e](https://github.com/aignostics/python-sdk/commit/a31716e42e0e2681633bff72f386550605bfc231))
- *(cli)* Fix CLI test with wrong CSV - ([14e20b5](https://github.com/aignostics/python-sdk/commit/14e20b5cc25fcfb67224fb04bd2f20c046153a47))
- *(docs)* Fix broken API reference page on ReadTheDocs - ([945fb12](https://github.com/aignostics/python-sdk/commit/945fb12ec6541d0b4ed7fb4259425cd949d29bfe))
- *(docs)* Use JSON as widdershins input and apply correct post-processing - ([0037124](https://github.com/aignostics/python-sdk/commit/00371241a8e677b1159c78a390f09a638298b5cc))
- *(gha)* Convert markdown to Slack markdown so urls are properly unfurled ([#438](https://github.com/aignostics/python-sdk/pull/438)) - ([36c6b0c](https://github.com/aignostics/python-sdk/commit/36c6b0c1dbe3d90417676d1e38df53a344607b69))
- *(platform)* Switch health check endpoint from /api/v1/health to /health - ([4d2963b](https://github.com/aignostics/python-sdk/commit/4d2963bb196ba5c7124ae3a28fa2190dfbe2f51f))
- *(platform)* Isolate health check HTTP pool from API client to prevent response cross-contamination - ([873e8d0](https://github.com/aignostics/python-sdk/commit/873e8d0d52b63b034726711ecc316fc286f406d1))
- *(qupath)* Remove trailing equal sign from logs - ([fe82486](https://github.com/aignostics/python-sdk/commit/fe8248668d3b66057b66c8dfe3d13de0c88f0aff))
- *(system)* Prevent yaml.dump from wrapping long strings in OpenAPI output - ([596a693](https://github.com/aignostics/python-sdk/commit/596a6937c156fab0f15d8f68ed50af85047b49a7))
- *(test)* Fix expected results after version bump ([#466](https://github.com/aignostics/python-sdk/pull/466)) - ([7dfaf52](https://github.com/aignostics/python-sdk/commit/7dfaf52a09da6966743a449082df2f20e6770852))
- *(test)* Fix expected results after version bump - ([d931bb2](https://github.com/aignostics/python-sdk/commit/d931bb26f7edfc88d8ccb49dee39f07ab79428a3))
- *(tests)* Use pip instead of uv for dummy plugin teardown uninstall - ([1504e1d](https://github.com/aignostics/python-sdk/commit/1504e1de56e8e771157bddd03ed4175c9413f8d8))
- *(tests)* Only suppress uninstall errors when package is already absent - ([aea6f5c](https://github.com/aignostics/python-sdk/commit/aea6f5c4a56883c256f5660396e6099c34419b37))
- *(tests)* Fall back to pip when uv is unavailable in plugin fixture - ([f0f5472](https://github.com/aignostics/python-sdk/commit/f0f5472be229cebadc52558623fb774c9204fd31))
- *(tests)* Update TC-UTILS-MCP-01 traceability tag from SWR-UTILS-1-1 to SWR-UTILS-2-4 - ([91c808b](https://github.com/aignostics/python-sdk/commit/91c808b8abe5e95c6a18a00b539e01e0b859edeb))
- *(tests)* Make dummy plugin uninstall best-effort in fixture teardown - ([b3d57bb](https://github.com/aignostics/python-sdk/commit/b3d57bbd5bfefbdeaa7f0098d956f82c3c627b95))
- *(tests)* Use uv for dummy plugin install to avoid network access - ([2d9cc35](https://github.com/aignostics/python-sdk/commit/2d9cc35054e90da9eecbf574f50ea0872c7d6aab))
- *(tests)* Address Copilot review feedback on plugin tests - ([74a5339](https://github.com/aignostics/python-sdk/commit/74a53396d8ec7137b624f7566d066c4975f72968))
- *(tests)* Amend tests to use L4 - ([1e0b848](https://github.com/aignostics/python-sdk/commit/1e0b8483cc804511cb160e64bc20bf4c86f9a8d9))
- *(tests)* Use test constants for GPU type, use L4 for prod testing - ([1e0b848](https://github.com/aignostics/python-sdk/commit/1e0b8483cc804511cb160e64bc20bf4c86f9a8d9))
- *(traceability)* Link SWR-UTILS-2-1 to TC-UTILS-MCP-01 test case - ([a65a73d](https://github.com/aignostics/python-sdk/commit/a65a73d30a8eafc67d8c3e05b0f82547b345a6a9))
- Ci, skip:test:long-running, skip:test:matrix-runner, skip:test:very-long-running] - ([6a1ab60](https://github.com/aignostics/python-sdk/commit/6a1ab608dc8bd36067a9cfab685b954c42cbed29))
- Claude Sonnet 4.6 <noreply@anthropic.com> - ([6a1ab60](https://github.com/aignostics/python-sdk/commit/6a1ab608dc8bd36067a9cfab685b954c42cbed29))
- Test:long-running] - ([1504e1d](https://github.com/aignostics/python-sdk/commit/1504e1de56e8e771157bddd03ed4175c9413f8d8))
- Test:long-running, skip:test:matrix-runner] - ([aea6f5c](https://github.com/aignostics/python-sdk/commit/aea6f5c4a56883c256f5660396e6099c34419b37))
- If the package is already absent, the goal is achieved. - ([b3d57bb](https://github.com/aignostics/python-sdk/commit/b3d57bbd5bfefbdeaa7f0098d956f82c3c627b95))
- Shallow plugin discovery ([#462](https://github.com/aignostics/python-sdk/pull/462)) - ([fa4eeb3](https://github.com/aignostics/python-sdk/commit/fa4eeb3d07975bdb93bb70b9d9ae30b4d54993ec))
- Use the dedicated Service._http_pool (same as public health check) with a - ([873e8d0](https://github.com/aignostics/python-sdk/commit/873e8d0d52b63b034726711ecc316fc286f406d1))
- Claude Opus 4.6 (1M context) <noreply@anthropic.com> - ([873e8d0](https://github.com/aignostics/python-sdk/commit/873e8d0d52b63b034726711ecc316fc286f406d1))
- Retry on 404 in run details to handle read replica lag ([#440](https://github.com/aignostics/python-sdk/pull/440)) - ([e686e70](https://github.com/aignostics/python-sdk/commit/e686e70923407e0ef8a6a0fe0fb2558db29050ff))
- Remove redundant uv venv step in ReadTheDocs build config - ([80d657c](https://github.com/aignostics/python-sdk/commit/80d657cdbd65571673c7b0bd9446c5b2b76708c7))
- Remove redundant uv venv step in ReadTheDocs build config [skip:ci, skip:test:long-running, skip:test:matrix-runner, skip:test:very-long-running] - ([c2ce9e8](https://github.com/aignostics/python-sdk/commit/c2ce9e84f62142c9e5c49e0c6b860b3812530654))

### 🚜 Refactor

- *(bucket)* Extract helpers from find() to reduce cognitive complexity - ([3b14d7c](https://github.com/aignostics/python-sdk/commit/3b14d7c0c32839da1f53e3e32ba1272456678ec7))
- *(requirements)* Restructure UTILS requirements hierarchy - ([403ba60](https://github.com/aignostics/python-sdk/commit/403ba601c38414cbb4fe8c67062aaba64dc3c235))
- *(tests)* Centralise dummy plugin install fixture in utils conftest - ([83a52b5](https://github.com/aignostics/python-sdk/commit/83a52b5717178c99cb0b66f7e6677023c29c0170))
- *(tests)* Extract save/restore fixture into qupath conftest - ([45d6f99](https://github.com/aignostics/python-sdk/commit/45d6f99526108054517d52829577cd66b58a4562))
- *(tests)* Implement factory methods ([#455](https://github.com/aignostics/python-sdk/pull/455)) - ([250cc58](https://github.com/aignostics/python-sdk/commit/250cc58df4f199e5e30d0ac4a135a3d6e977f558))
- Claude Sonnet 4.6 <noreply@anthropic.com> - ([403ba60](https://github.com/aignostics/python-sdk/commit/403ba601c38414cbb4fe8c67062aaba64dc3c235))

### 📚 Documentation

- *(docs)* Use JSON as widdershins input and apply correct post-processing - ([0037124](https://github.com/aignostics/python-sdk/commit/00371241a8e677b1159c78a390f09a638298b5cc))
- *(requirements)* Align SWR-UTILS-2-3 and FR-13 with implemented behavior - ([01e6b01](https://github.com/aignostics/python-sdk/commit/01e6b016b66b73d505216a7807563d3819632936))
- *(requirements)* Simplify SWR-UTILS-2-4 wording to match SWR pattern - ([5848730](https://github.com/aignostics/python-sdk/commit/5848730577b6616d3cbf891348ee9bfb4552c97c))
- *(requirements)* Add MCP servers to SHR-UTILS-2 plugin contribution list - ([01e16f7](https://github.com/aignostics/python-sdk/commit/01e16f74a7896a944b56978c20993872145b536f))
- *(specs)* Update SPEC-PLATFORM-SERVICE post v1.1.0 - ([629185b](https://github.com/aignostics/python-sdk/commit/629185b2fa00e987cf7d8933056f0527643b8686))
- *(specs)* Align FR-10 in SPEC-UTILS-SERVICE with SWR-UTILS-2-4 - ([44d08c5](https://github.com/aignostics/python-sdk/commit/44d08c5c46ee421b4ef5385a9ff0cd9ed34b4680))
- *(tests)* Remove function names from Gherkin scenario steps - ([f764695](https://github.com/aignostics/python-sdk/commit/f7646954c1d18ef4d7b21177b7ea21d265cb752d))
- *(tests)* Align TC-UTILS-PLUGIN-03 feature title with SWR-UTILS-2-3 rename - ([ec4c878](https://github.com/aignostics/python-sdk/commit/ec4c87864849b726ec801082f3dae6d3c1b2302d))
- Add 'test' to supported deployment environments ([#422](https://github.com/aignostics/python-sdk/pull/422)) - ([629185b](https://github.com/aignostics/python-sdk/commit/629185b2fa00e987cf7d8933056f0527643b8686))
- Ci, skip:test:long-running, skip:test:matrix-runner, skip:test:very-long-running - ([629185b](https://github.com/aignostics/python-sdk/commit/629185b2fa00e987cf7d8933056f0527643b8686))
- Claude Sonnet 4.6 <noreply@anthropic.com> - ([629185b](https://github.com/aignostics/python-sdk/commit/629185b2fa00e987cf7d8933056f0527643b8686))
- Test:long-running, skip:test:matrix-runner] - ([f764695](https://github.com/aignostics/python-sdk/commit/f7646954c1d18ef4d7b21177b7ea21d265cb752d))
- Ci, skip:test:long-running, skip:test:matrix-runner, skip:test:very-long-running] - ([44d08c5](https://github.com/aignostics/python-sdk/commit/44d08c5c46ee421b4ef5385a9ff0cd9ed34b4680))
- Restore accidentally removed MCP server section[skip:ci, skip:test:long-running, skip:test:matrix-runner, skip:test:very-long-running] - ([63e1259](https://github.com/aignostics/python-sdk/commit/63e12596657ead6765aaa3e2879e5ead503aab37))

### ⚡ Performance

- *(bucket)* Add server-side prefix filtering to find() to avoid full bucket scans - ([0a24176](https://github.com/aignostics/python-sdk/commit/0a24176b7260321ecb53bc9cb68fd793df41719d))
- Claude Sonnet 4.6 <noreply@anthropic.com> - ([0a24176](https://github.com/aignostics/python-sdk/commit/0a24176b7260321ecb53bc9cb68fd793df41719d))

### 🎨 Styling

- Fix ruff formatting in mcp_test.py - ([5008493](https://github.com/aignostics/python-sdk/commit/50084932a425e5fe0cae02c95674cf7974942a53))
- Claude Sonnet 4.6 <noreply@anthropic.com> - ([5008493](https://github.com/aignostics/python-sdk/commit/50084932a425e5fe0cae02c95674cf7974942a53))
- Reformat test signature to single line per ruff - ([0ed3d00](https://github.com/aignostics/python-sdk/commit/0ed3d00068c9587618ad7d3e55f161c838ff7b60))

### 🧪 Testing

- *(platform)* Isolate health check HTTP pool from API client to prevent response cross-contamination - ([873e8d0](https://github.com/aignostics/python-sdk/commit/873e8d0d52b63b034726711ecc316fc286f406d1))
- *(qupath)* Parametrize install/uninstall test for independent retries - ([8eb9c03](https://github.com/aignostics/python-sdk/commit/8eb9c03e043cee571ba497be1007b32aa27cea2e))
- Mock BucketService.find_static in GUI test ([#465](https://github.com/aignostics/python-sdk/pull/465)) - ([2c6193b](https://github.com/aignostics/python-sdk/commit/2c6193bf614cc3cca106c97e245db414e52b56bb))
- Claude Sonnet 4.6 <noreply@anthropic.com> - ([8eb9c03](https://github.com/aignostics/python-sdk/commit/8eb9c03e043cee571ba497be1007b32aa27cea2e))
- Update bucket used for E2E tests ([#454](https://github.com/aignostics/python-sdk/pull/454)) - ([894ee74](https://github.com/aignostics/python-sdk/commit/894ee74d54161216c25022061abe2756a3188879))
- Increase retries for QuPath install test - ([6b4e468](https://github.com/aignostics/python-sdk/commit/6b4e4686f55ce54950ec17a75bc4798041df218d))
- Increase timeout and add post-cancel retry in cancel-by-filter E2E test - ([cbccb76](https://github.com/aignostics/python-sdk/commit/cbccb76330497d232f8c222ea0ab35aaef8b4b94))
- Isolate metadata update E2E tests with dedicated runs and retry-on-read - ([677584c](https://github.com/aignostics/python-sdk/commit/677584c589ad4436530197118cb1580e1837f6cc))

### ⚙️ Miscellaneous Tasks

- *(deps)* Upgrade lxml-html-clean to 0.4.4 and authlib to 1.6.9 - ([bb06bc4](https://github.com/aignostics/python-sdk/commit/bb06bc48781a438bd25169a6d8cf9ac8efeaef1d))
- *(deps)* Bump authlib from 1.6.6 to 1.6.7 - ([8ff112d](https://github.com/aignostics/python-sdk/commit/8ff112d279529f63ccfabbf1cc634c772f676a95))
- *(deps)* Bump lxml-html-clean from 0.4.3 to 0.4.4 - ([488b33a](https://github.com/aignostics/python-sdk/commit/488b33a0f436302d939a9f363dc5e54687614f59))
- *(deps)* Resolve vulnerabilities ([#430](https://github.com/aignostics/python-sdk/pull/430)) - ([e71465a](https://github.com/aignostics/python-sdk/commit/e71465abb528f6492977e8661f1f2ae9a3c74d07))
- *(deps)* Bump nbconvert from 7.16.6 to 7.17.0 ([#424](https://github.com/aignostics/python-sdk/pull/424)) - ([aaa92b9](https://github.com/aignostics/python-sdk/commit/aaa92b95e3b1df78498abc7d707979cd757bce10))
- *(deps)* Bump cryptography from 46.0.3 to 46.0.5 ([#426](https://github.com/aignostics/python-sdk/pull/426)) - ([e56ed1f](https://github.com/aignostics/python-sdk/commit/e56ed1f543104b92bbd08e173e5ea5a08b5a7a2b))
- *(he-tme)* Bump staging to 1.1.0 ([#450](https://github.com/aignostics/python-sdk/pull/450)) - ([fb150e4](https://github.com/aignostics/python-sdk/commit/fb150e44206774e838b5628749eb11d221aeb630))
- Bump app version in tests to 1.1.0 in prod ([#464](https://github.com/aignostics/python-sdk/pull/464)) - ([19b0882](https://github.com/aignostics/python-sdk/commit/19b0882386da4016cc91bed6ce1d6eb85a752b29))
- Claude Sonnet 4.6 <noreply@anthropic.com> - ([bb06bc4](https://github.com/aignostics/python-sdk/commit/bb06bc48781a438bd25169a6d8cf9ac8efeaef1d))
- Fix YAML escape in pre-commit hook exclusion regex - ([d5a0281](https://github.com/aignostics/python-sdk/commit/d5a0281356a7bea5b9771a31732d6aa17ec97544))
- Fix regex in name-tests-test pre-commit hook exclusion - ([67ddbf8](https://github.com/aignostics/python-sdk/commit/67ddbf88448cb746cb1b29869bcc78dc699042f2))
- Exclude tests/resources/ from name-tests-test pre-commit hook - ([e422566](https://github.com/aignostics/python-sdk/commit/e42256686f069a4957d72adba85ba6a9d852a9ac))
- Add compass.yml file ([#441](https://github.com/aignostics/python-sdk/pull/441)) - ([0414a3c](https://github.com/aignostics/python-sdk/commit/0414a3c1d418e53d44f8204c95912380da7ebc57))
- Atlassian-compass[bot] <89495476+atlassian-compass[bot]@users.noreply.github.com> - ([0414a3c](https://github.com/aignostics/python-sdk/commit/0414a3c1d418e53d44f8204c95912380da7ebc57))
- Authlib - ([8ff112d](https://github.com/aignostics/python-sdk/commit/8ff112d279529f63ccfabbf1cc634c772f676a95))
- Dependabot[bot] <support@github.com> - ([8ff112d](https://github.com/aignostics/python-sdk/commit/8ff112d279529f63ccfabbf1cc634c772f676a95))
- Lxml-html-clean - ([488b33a](https://github.com/aignostics/python-sdk/commit/488b33a0f436302d939a9f363dc5e54687614f59))
- Fix missing end-of-file newline in API_REFERENCE_v1.md - ([3e46bd3](https://github.com/aignostics/python-sdk/commit/3e46bd31c9998ac8709028d48f8ac6f0c6303398))
- Ci, skip:test:long-running, skip:test:matrix-runner, skip:test:very-long-running] - ([3e46bd3](https://github.com/aignostics/python-sdk/commit/3e46bd31c9998ac8709028d48f8ac6f0c6303398))
- Fix missing end-of-file newlines - ([60d7dcb](https://github.com/aignostics/python-sdk/commit/60d7dcb7a705f861d612e6b65543bf6cc3552286))
- Remove MCP from the interface options section of the README ([#452](https://github.com/aignostics/python-sdk/pull/452)) - ([73ede20](https://github.com/aignostics/python-sdk/commit/73ede2037c82046a329b7ee4dba8a490aba7caa5))
- Run lint on push - ([12c3891](https://github.com/aignostics/python-sdk/commit/12c3891a4168e5ec81115276a53c2e9ef077af97))
- Add test environment support - ([b702567](https://github.com/aignostics/python-sdk/commit/b70256739063affaf8e442cf0b4bde64abf64783))
- Nbconvert - ([aaa92b9](https://github.com/aignostics/python-sdk/commit/aaa92b95e3b1df78498abc7d707979cd757bce10))
- Dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com> - ([aaa92b9](https://github.com/aignostics/python-sdk/commit/aaa92b95e3b1df78498abc7d707979cd757bce10))
- Cryptography - ([e56ed1f](https://github.com/aignostics/python-sdk/commit/e56ed1f543104b92bbd08e173e5ea5a08b5a7a2b))

### 🛡️ Security

- *(deps)* Update dependency nicegui to v3.8.0 [security] ([#448](https://github.com/aignostics/python-sdk/pull/448)) - ([9ba8853](https://github.com/aignostics/python-sdk/commit/9ba8853b3bf9482839cdbcfb0eb252e33089461a))
- *(deps)* Update dependency pillow to v12.1.1 [security] ([#428](https://github.com/aignostics/python-sdk/pull/428)) - ([0c8084a](https://github.com/aignostics/python-sdk/commit/0c8084a6346f07521188eae22535e6fdb3f517d7))
- Renovate[bot] <29139614+renovate[bot]@users.noreply.github.com> - ([9ba8853](https://github.com/aignostics/python-sdk/commit/9ba8853b3bf9482839cdbcfb0eb252e33089461a))
- Merge pull request #436 from aignostics/fix_formatting_in_security_md_file - ([d24ed67](https://github.com/aignostics/python-sdk/commit/d24ed67f105e8914e03c357e7365f1f4c086b677))
- Fixed typos in SECURITY.md: "Dependendabot" → "Dependabot", "encouraring" → "encouraging" - ([d24ed67](https://github.com/aignostics/python-sdk/commit/d24ed67f105e8914e03c357e7365f1f4c086b677))
- Fixed duplicate list markers in SECURITY.md section 2: (a), (a), (d) → (a), (b), (c) - ([d24ed67](https://github.com/aignostics/python-sdk/commit/d24ed67f105e8914e03c357e7365f1f4c086b677))
- Fixed list item rendering in SECURITY.md by adding blank lines between items in all 4 sections so they render on separate lines in the HTML output - ([d24ed67](https://github.com/aignostics/python-sdk/commit/d24ed67f105e8914e03c357e7365f1f4c086b677))
- Improved mermaid diagram readability in docs/partials/README_main.md: dark theme, white text and arrows, 18px font - ([d24ed67](https://github.com/aignostics/python-sdk/commit/d24ed67f105e8914e03c357e7365f1f4c086b677))
- Made mermaid diagram use full page width via custom CSS (docs/source/_static/custom.css) - ([d24ed67](https://github.com/aignostics/python-sdk/commit/d24ed67f105e8914e03c357e7365f1f4c086b677))
- Restored accidentally removed MCP Server documentation from docs/partials/README_main.md and docs/partials/README_glossary.md - ([d24ed67](https://github.com/aignostics/python-sdk/commit/d24ed67f105e8914e03c357e7365f1f4c086b677))
- Regenerated docs artifacts (README.md, API_REFERENCE_v1.md, CLI_REFERENCE.md, ATTRIBUTIONS.md, openapi_v1.yaml) by running make docs - ([d24ed67](https://github.com/aignostics/python-sdk/commit/d24ed67f105e8914e03c357e7365f1f4c086b677))
- Update security and readme files [skip:ci, skip:test:long-running, skip:test:matrix-runner, skip:test:very-long-running] - ([75cf714](https://github.com/aignostics/python-sdk/commit/75cf7148dff5e1f9d614abcfe99c77399a429fa3))

### FR-04

- Added test as a supported deployment environment alongside production, staging, and development - ([7a185d4](https://github.com/aignostics/python-sdk/commit/7a185d433c9e772c7c9eed47ae75f1840119f05b))

### Task

- Add MCP E2E tests ([#432](https://github.com/aignostics/python-sdk/pull/432)) - ([637e56c](https://github.com/aignostics/python-sdk/commit/637e56cda49348bb69ea64f8ba3c486fa645f274))
- Add MCP E2E tests - ([637e56c](https://github.com/aignostics/python-sdk/commit/637e56cda49348bb69ea64f8ba3c486fa645f274))



* @atlassian-compass[bot] made their first contribution in [#441](https://github.com/aignostics/python-sdk/pull/441)
* @nahua-aignx made their first contribution in [#440](https://github.com/aignostics/python-sdk/pull/440)
* @melifaro made their first contribution in [#422](https://github.com/aignostics/python-sdk/pull/422)

# [v1.1.0](https://github.com/aignostics/python-sdk/compare/v1.0.3..v1.1.0) - 2026-02-10

### 🐛 Bug Fixes

- Revert exclude null flex_start_max_run_duration_minutes in GPUConfig ([#394](https://github.com/aignostics/python-sdk/pull/394)) - ([1a6cc82](https://github.com/aignostics/python-sdk/commit/1a6cc82d0aa4f8f145259e302e48df19aab02927))
- Exclude null flex_start_max_run_duration_minutes in GPUConfig ([#391](https://github.com/aignostics/python-sdk/pull/391)) - ([420c548](https://github.com/aignostics/python-sdk/commit/420c548d9d6a9f1be1ddf44a38042de2b86b5845))

### 🧪 Testing

- Fix import order in test_cli_gui_run ([#419](https://github.com/aignostics/python-sdk/pull/419)) - ([283d2f8](https://github.com/aignostics/python-sdk/commit/283d2f8c4f02c61ac20906e15a82256bddadec01))
- Unset flex_start_max_run_duration_minutes when null or zero ([#403](https://github.com/aignostics/python-sdk/pull/403)) - ([3f69353](https://github.com/aignostics/python-sdk/commit/3f6935325bcc21dee86676ca8a1cff27ad4a2669))
- Use GPUConfig in E2E test ([#393](https://github.com/aignostics/python-sdk/pull/393)) - ([2e89ef3](https://github.com/aignostics/python-sdk/commit/2e89ef3e8446ae58df23660ea6a4d5f843179cd9))

### ⚙️ Miscellaneous Tasks

- *(deps)* Bump python-multipart from 0.0.20 to 0.0.22 ([#402](https://github.com/aignostics/python-sdk/pull/402)) - ([4a8bc60](https://github.com/aignostics/python-sdk/commit/4a8bc601d42555a85ebe3ba99881bf904d5ce4cc))
- *(deps)* Bump pyasn1 from 0.6.1 to 0.6.2 ([#389](https://github.com/aignostics/python-sdk/pull/389)) - ([48dbe6d](https://github.com/aignostics/python-sdk/commit/48dbe6d769355ba533618c8d56a31722f823acbd))
- *(deps)* Bump filelock from 3.20.1 to 3.20.3 ([#386](https://github.com/aignostics/python-sdk/pull/386)) - ([6b66c8f](https://github.com/aignostics/python-sdk/commit/6b66c8fdd459d3e312f98b823cff117c7b51bb7b))
- *(deps)* Bump virtualenv from 20.35.4 to 20.36.1 ([#385](https://github.com/aignostics/python-sdk/pull/385)) - ([683201e](https://github.com/aignostics/python-sdk/commit/683201ea4a0a9d84999ed39b887b656e65aee0db))
- Fix Claude sticky comments in PR reviews ([#407](https://github.com/aignostics/python-sdk/pull/407)) - ([61474b8](https://github.com/aignostics/python-sdk/commit/61474b8070b0c91f2e0e2d70987f6d9c6d27ef36))
- Python-multipart - ([4a8bc60](https://github.com/aignostics/python-sdk/commit/4a8bc601d42555a85ebe3ba99881bf904d5ce4cc))
- Dependabot[bot] <support@github.com> - ([4a8bc60](https://github.com/aignostics/python-sdk/commit/4a8bc601d42555a85ebe3ba99881bf904d5ce4cc))
- Dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com> - ([4a8bc60](https://github.com/aignostics/python-sdk/commit/4a8bc601d42555a85ebe3ba99881bf904d5ce4cc))
- Ignore CVE-2026-0994 - ([bef31d1](https://github.com/aignostics/python-sdk/commit/bef31d1f01e986e64559da14320396bfc63f1255))
- Pyasn1 - ([48dbe6d](https://github.com/aignostics/python-sdk/commit/48dbe6d769355ba533618c8d56a31722f823acbd))
- Filelock - ([6b66c8f](https://github.com/aignostics/python-sdk/commit/6b66c8fdd459d3e312f98b823cff117c7b51bb7b))
- Virtualenv - ([683201e](https://github.com/aignostics/python-sdk/commit/683201ea4a0a9d84999ed39b887b656e65aee0db))

### 🛡️ Security

- *(deps)* Update dependency nicegui to v3.7.0 [security] ([#418](https://github.com/aignostics/python-sdk/pull/418)) - ([783bd86](https://github.com/aignostics/python-sdk/commit/783bd8633901e3a74d009330457a9880e6dd5dd2))
- *(deps)* Update dependency pip to v26 [security] - ([3e5b9a8](https://github.com/aignostics/python-sdk/commit/3e5b9a8002e0ac701140fd57e52dcf9833f25790))
- Renovate[bot] <29139614+renovate[bot]@users.noreply.github.com> - ([783bd86](https://github.com/aignostics/python-sdk/commit/783bd8633901e3a74d009330457a9880e6dd5dd2))

### Task

- *(BE-5757)* Create central MCP server with auto-disocovery of plugin tools ([#401](https://github.com/aignostics/python-sdk/pull/401)) - ([90f4c00](https://github.com/aignostics/python-sdk/commit/90f4c0053a46ef95ea262c79188548d60d6e5d9c))
- Link tests for MCP SISs ([#423](https://github.com/aignostics/python-sdk/pull/423)) - ([266149c](https://github.com/aignostics/python-sdk/commit/266149c38f84d22a20a3bc6887991d0f183503f7))


# [v1.0.3](https://github.com/aignostics/python-sdk/compare/v1.0.2..v1.0.3) - 2026-01-09

### 🐛 Bug Fixes

- *(ci)* Skip Ketryx reporting for Dependabot PRs ([#381](https://github.com/aignostics/python-sdk/pull/381)) - ([9b7631b](https://github.com/aignostics/python-sdk/commit/9b7631b95955073c59f967b1c5fc7eda0b833452))
- *(deps)* Update dependency idc-index-data to v23.0.3 ([#358](https://github.com/aignostics/python-sdk/pull/358)) - ([0ff4fc0](https://github.com/aignostics/python-sdk/commit/0ff4fc0c487dea21627b079c2337afd83f9de323))
- *(deps)* Update dependency fastparquet to v2025 ([#370](https://github.com/aignostics/python-sdk/pull/370)) - ([2fa4f3a](https://github.com/aignostics/python-sdk/commit/2fa4f3adc49a59f82674ebdb2409b23d06b55086))
- *(platform)* Preserve platform_bucket in item SDK metadata ([#362](https://github.com/aignostics/python-sdk/pull/362)) - ([aca8db0](https://github.com/aignostics/python-sdk/commit/aca8db0ac086b93c311ab358ad06d5edc205fd5f))
- Renovate[bot] <29139614+renovate[bot]@users.noreply.github.com> - ([0ff4fc0](https://github.com/aignostics/python-sdk/commit/0ff4fc0c487dea21627b079c2337afd83f9de323))
- Oliver Meyer <42039965+olivermeyer@users.noreply.github.com> - ([0ff4fc0](https://github.com/aignostics/python-sdk/commit/0ff4fc0c487dea21627b079c2337afd83f9de323))
- Pin fastparquet<2025.12.0 ([#356](https://github.com/aignostics/python-sdk/pull/356)) - ([d0c77d8](https://github.com/aignostics/python-sdk/commit/d0c77d89f5290cd78369fddb9aec314e014cebae))

### 📚 Documentation

- Update ATTRIBUTIONS.md ([#382](https://github.com/aignostics/python-sdk/pull/382)) - ([5c5a869](https://github.com/aignostics/python-sdk/commit/5c5a869d91004a324e785bdae9fdf23a1f28bcbd))

### ⚙️ Miscellaneous Tasks

- *(deps)* Bump getsentry/action-release from 3.4.0 to 3.5.0 ([#371](https://github.com/aignostics/python-sdk/pull/371)) - ([0f18961](https://github.com/aignostics/python-sdk/commit/0f189614f8d2e45635656c499ef697e835b958d1))
- *(deps)* Bump idc-index-data from 23.0.3 to 23.2.7 ([#373](https://github.com/aignostics/python-sdk/pull/373)) - ([31cabfb](https://github.com/aignostics/python-sdk/commit/31cabfbc23d43b3b60fbf56fcc5c6789b83a6163))
- *(deps)* Bump astral-sh/setup-uv from 7.1.6 to 7.2.0 ([#375](https://github.com/aignostics/python-sdk/pull/375)) - ([b05aed8](https://github.com/aignostics/python-sdk/commit/b05aed8d0fed345dc67f6b14493e4cf780146084))
- *(deps)* Update anthropics/claude-code-action action to v1.0.29 ([#377](https://github.com/aignostics/python-sdk/pull/377)) - ([673b138](https://github.com/aignostics/python-sdk/commit/673b138f1b88d789d094c01edd198c602de47264))
- *(deps)* Update dependency pyright to >=1.1.408,<1.1.409 ([#378](https://github.com/aignostics/python-sdk/pull/378)) - ([e842971](https://github.com/aignostics/python-sdk/commit/e8429713dd6fe34b528d6fa9c760ccb277daaafd))
- *(deps)* Update ghcr.io/astral-sh/uv docker tag to v0.9.18 ([#357](https://github.com/aignostics/python-sdk/pull/357)) - ([8ce35c9](https://github.com/aignostics/python-sdk/commit/8ce35c9f1d0294a3d15393b1b4709a1db680d930))
- *(deps)* Update docker/setup-buildx-action action to v3.12.0 ([#366](https://github.com/aignostics/python-sdk/pull/366)) - ([8c9e964](https://github.com/aignostics/python-sdk/commit/8c9e964954817ae592b80f255950b4a1ed73fd16))
- *(deps)* Update dependency scalene to v2 ([#367](https://github.com/aignostics/python-sdk/pull/367)) - ([e8f5ff2](https://github.com/aignostics/python-sdk/commit/e8f5ff2975de30cc1109f4b8493b5bf8e6ba44aa))
- *(deps)* Update dependency sphinx-inline-tabs to v2025 ([#369](https://github.com/aignostics/python-sdk/pull/369)) - ([f0b2762](https://github.com/aignostics/python-sdk/commit/f0b2762e645a31a8cbb738a01a7812b705042d04))
- *(deps)* Bump marshmallow to 3.26.2 due to CVE-2025-68480 - ([d26e075](https://github.com/aignostics/python-sdk/commit/d26e07505500461192d17a8197d59f4861b0acf6))
- *(deps)* Update anthropics/claude-code-action action to v1.0.27 ([#352](https://github.com/aignostics/python-sdk/pull/352)) - ([9bd8588](https://github.com/aignostics/python-sdk/commit/9bd85880c1048549ee616b0265cfa64979f7882f))
- *(deps)* Bump codecov/test-results-action from 1.1.1 to 1.2.1 ([#348](https://github.com/aignostics/python-sdk/pull/348)) - ([d71f990](https://github.com/aignostics/python-sdk/commit/d71f990e7405545b2d093c8f398dbc5b719af667))
- *(deps)* Bump orhun/git-cliff-action from 4.6.0 to 4.7.0 ([#347](https://github.com/aignostics/python-sdk/pull/347)) - ([ba2601d](https://github.com/aignostics/python-sdk/commit/ba2601d78ce31f40e26a662fc1169653747b69d6))
- *(deps)* Bump actions/upload-artifact from 5.0.0 to 6.0.0 ([#346](https://github.com/aignostics/python-sdk/pull/346)) - ([0263859](https://github.com/aignostics/python-sdk/commit/02638598b5b9d084417b39226e81a53cd31c0812))
- *(deps)* Bump actions/download-artifact from 6.0.0 to 7.0.0 ([#345](https://github.com/aignostics/python-sdk/pull/345)) - ([2a204df](https://github.com/aignostics/python-sdk/commit/2a204dfe9fe7dc3b1d0c22447d91d153723309b5))
- *(deps)* Bump astral-sh/setup-uv from 7.1.5 to 7.1.6 ([#344](https://github.com/aignostics/python-sdk/pull/344)) - ([3e575fc](https://github.com/aignostics/python-sdk/commit/3e575fcdc9de9fc21166ee871dc2aee4e3430429))
- Getsentry/action-release - ([0f18961](https://github.com/aignostics/python-sdk/commit/0f189614f8d2e45635656c499ef697e835b958d1))
- Dependabot[bot] <support@github.com> - ([0f18961](https://github.com/aignostics/python-sdk/commit/0f189614f8d2e45635656c499ef697e835b958d1))
- Dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com> - ([0f18961](https://github.com/aignostics/python-sdk/commit/0f189614f8d2e45635656c499ef697e835b958d1))
- Idc-index-data - ([31cabfb](https://github.com/aignostics/python-sdk/commit/31cabfbc23d43b3b60fbf56fcc5c6789b83a6163))
- Astral-sh/setup-uv - ([b05aed8](https://github.com/aignostics/python-sdk/commit/b05aed8d0fed345dc67f6b14493e4cf780146084))
- Renovate[bot] <29139614+renovate[bot]@users.noreply.github.com> - ([673b138](https://github.com/aignostics/python-sdk/commit/673b138f1b88d789d094c01edd198c602de47264))
- Bump NiceGUI lower bound for CVEs ([#380](https://github.com/aignostics/python-sdk/pull/380)) - ([734f30b](https://github.com/aignostics/python-sdk/commit/734f30b474322505209bb15574d9f123bb3d4c03))
- Update aiohttp ([#374](https://github.com/aignostics/python-sdk/pull/374)) - ([8cdf228](https://github.com/aignostics/python-sdk/commit/8cdf2284c8d8fd09df6b46b9d26bd0498176ae9a))
- Oliver Meyer <42039965+olivermeyer@users.noreply.github.com> - ([8ce35c9](https://github.com/aignostics/python-sdk/commit/8ce35c9f1d0294a3d15393b1b4709a1db680d930))
- //github.com/aignostics/python-sdk/actions/runs/20456374041/job/58779266640 - ([520acd1](https://github.com/aignostics/python-sdk/commit/520acd10b968bed25610d760e47a5896cd253fcd))
- //uptime.betterstack.com/team/t344596/incidents/899992471 - ([520acd1](https://github.com/aignostics/python-sdk/commit/520acd10b968bed25610d760e47a5896cd253fcd))
- Codecov/test-results-action - ([d71f990](https://github.com/aignostics/python-sdk/commit/d71f990e7405545b2d093c8f398dbc5b719af667))
- Orhun/git-cliff-action - ([ba2601d](https://github.com/aignostics/python-sdk/commit/ba2601d78ce31f40e26a662fc1169653747b69d6))
- Actions/upload-artifact - ([0263859](https://github.com/aignostics/python-sdk/commit/02638598b5b9d084417b39226e81a53cd31c0812))
- Actions/download-artifact - ([2a204df](https://github.com/aignostics/python-sdk/commit/2a204dfe9fe7dc3b1d0c22447d91d153723309b5))

### 🛡️ Security

- Address CVE-2025-53000 and CVE-2026-21441 ([#376](https://github.com/aignostics/python-sdk/pull/376)) - ([1ff7283](https://github.com/aignostics/python-sdk/commit/1ff7283f0287bb49c3b63415ee3f242c3d3cc13f))



* @mk0x9 made their first contribution

# [v1.0.2](https://github.com/aignostics/python-sdk/compare/v1.0.1..v1.0.2) - 2025-12-18

### 🐛 Bug Fixes

- Pin QuPath version to 0.6.0 ([#355](https://github.com/aignostics/python-sdk/pull/355)) - ([1afe2fa](https://github.com/aignostics/python-sdk/commit/1afe2fa1585ea6d5d3e75fca55cfc0d40ce9ddcc))

### Build

- Link release notes to aignostics/python-sdk [skip:ci] ([#354](https://github.com/aignostics/python-sdk/pull/354)) - ([0f67ad2](https://github.com/aignostics/python-sdk/commit/0f67ad203ed888eb534f3a9b8b8b8aaf562ab4fe))


# [v1.0.1](https://github.com/aignostics/python-sdk/compare/v1.0.0..v1.0.1) - 2025-12-17

### 🛡️ Security

- Pin filelock>=3.20.1 ([#351](https://github.com/aignostics/python-sdk/pull/351)) - ([aa82858](https://github.com/aignostics/python-sdk/commit/aa82858025709deea122f4b9af2ddde4a37aa618))


# [v1.0.0](https://github.com/aignostics/python-sdk/compare/v0.2.235..v1.0.0) - 2025-12-16

### 📚 Documentation

- Update risk introduction info for requirements [skip:ci, skip:test:long-running, skip:test:matrix-runner, skip:test:very-long-running] - ([2cef198](https://github.com/aignostics/python-sdk/commit/2cef198129c02dc40d1e98b47fc01b3cde62f8f2))


# [v0.2.235](https://github.com/aignostics/python-sdk/compare/v0.2.234..v0.2.235) - 2025-12-12

### ⛰️  Features

- *(application)* Expose run queue position ([#318](https://github.com/aignostics/python-sdk/pull/318)) - ([cddbd1d](https://github.com/aignostics/python-sdk/commit/cddbd1d4a5a80ac89a1c043185b4fa5ec597d1b3))
- Prevent submitting runs when system is unhealthy ([#336](https://github.com/aignostics/python-sdk/pull/336)) - ([e5000c4](https://github.com/aignostics/python-sdk/commit/e5000c4adb9f6b295695841c733f0f61f507f797))

### 🐛 Bug Fixes

- *(ci)* Prevent shell injection in commit message handling + failing console width test ([#341](https://github.com/aignostics/python-sdk/pull/341)) - ([1b2ec15](https://github.com/aignostics/python-sdk/commit/1b2ec15fcde3d54d83b5718e13ef61dfa5aa95e2))
- *(wsi)* Add multi-file pyramid + WSI selection for DICOM files ([#270](https://github.com/aignostics/python-sdk/pull/270)) - ([e3d8851](https://github.com/aignostics/python-sdk/commit/e3d8851c8f7eb3a859c8e871f27874b67d761dd0))
- Bring Launchpad to front after successful login ([#319](https://github.com/aignostics/python-sdk/pull/319)) - ([310fc5d](https://github.com/aignostics/python-sdk/commit/310fc5d0b292b3b1bed7c6d7a5bdc8cefd933dde))

### 📚 Documentation

- Update documentation - ([25d7fba](https://github.com/aignostics/python-sdk/commit/25d7fba24ca8fc32c4f18736f88ae9e70d00757a))
- Document system health checks on run submission ([#342](https://github.com/aignostics/python-sdk/pull/342)) - ([c79951d](https://github.com/aignostics/python-sdk/commit/c79951da119ed4ce15450af14cd816214e6f4361))

### 🧪 Testing

- Declutter test logs ([#340](https://github.com/aignostics/python-sdk/pull/340)) - ([a13d24b](https://github.com/aignostics/python-sdk/commit/a13d24b8eb71d394c5873e5c35a78d305e9b67d8))

### ⚙️ Miscellaneous Tasks

- *(deps)* Bump codecov/codecov-action from 5.5.1 to 5.5.2 ([#333](https://github.com/aignostics/python-sdk/pull/333)) - ([3bfb904](https://github.com/aignostics/python-sdk/commit/3bfb904c9f227109df50d854260d712d1399baf5))
- *(deps)* Bump SonarSource/sonarqube-scan-action from 6.0.0 to 7.0.0 ([#334](https://github.com/aignostics/python-sdk/pull/334)) - ([1486412](https://github.com/aignostics/python-sdk/commit/1486412fc2cbb77203f65c49346d0f9c0fbf71a5))
- *(deps)* Bump idc-index-data from 23.0.1 to 23.0.2 ([#339](https://github.com/aignostics/python-sdk/pull/339)) - ([42c1628](https://github.com/aignostics/python-sdk/commit/42c16284157b564a808d70800f8aacd816797690))
- Remove label trigger for Claude interactive workflow - ([8c47754](https://github.com/aignostics/python-sdk/commit/8c47754b00b422092d90854a9fc4f75f38103674))
- Codecov/codecov-action - ([3bfb904](https://github.com/aignostics/python-sdk/commit/3bfb904c9f227109df50d854260d712d1399baf5))
- Dependabot[bot] <support@github.com> - ([3bfb904](https://github.com/aignostics/python-sdk/commit/3bfb904c9f227109df50d854260d712d1399baf5))
- Dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com> - ([3bfb904](https://github.com/aignostics/python-sdk/commit/3bfb904c9f227109df50d854260d712d1399baf5))
- Helmut Hoffer von Ankershoffen né Oertel <helmut@aignostics.com> - ([3bfb904](https://github.com/aignostics/python-sdk/commit/3bfb904c9f227109df50d854260d712d1399baf5))
- SonarSource/sonarqube-scan-action - ([1486412](https://github.com/aignostics/python-sdk/commit/1486412fc2cbb77203f65c49346d0f9c0fbf71a5))
- Idc-index-data - ([42c1628](https://github.com/aignostics/python-sdk/commit/42c16284157b564a808d70800f8aacd816797690))
- Pause stress test - ([8ada939](https://github.com/aignostics/python-sdk/commit/8ada939c3888a8f853cfedca1b9bfa68f18e2736))



* @blanca-pablos made their first contribution in [#341](https://github.com/aignostics/python-sdk/pull/341)

# [v0.2.234](https://github.com/aignostics/python-sdk/compare/v0.2.233..v0.2.234) - 2025-12-10

### ⛰️  Features

- *(gui)* Enable plugins to contribute nav items to right sidebar - ([2d4e327](https://github.com/aignostics/python-sdk/commit/2d4e327beb2ec7bca97cb7d541b351a606ee8289))


# [v0.2.233](https://github.com/aignostics/python-sdk/compare/v0.2.232..v0.2.233) - 2025-12-10

### ⛰️  Features

- *(core)* Allow to dynamically inject external (private or public) plugins extending Python SDK dynamically - ([45cdc51](https://github.com/aignostics/python-sdk/commit/45cdc51b9aa4947a3d34971e256bf3f76c07eb0a))

### 🐛 Bug Fixes

- Enable opening artifacts in qupath on Windows ([#335](https://github.com/aignostics/python-sdk/pull/335)) - ([878cbb0](https://github.com/aignostics/python-sdk/commit/878cbb0ca84139b6f9f22da6d18460c424ea4ba9))

### 🧪 Testing

- Revert skip failing test ([#329](https://github.com/aignostics/python-sdk/pull/329)) - ([0fc5990](https://github.com/aignostics/python-sdk/commit/0fc59904cb5a57e9c5556987055b64c1045a1d25))


# [v0.2.232](https://github.com/aignostics/python-sdk/compare/v0.2.231..v0.2.232) - 2025-12-10

### ⚙️ Miscellaneous Tasks

- *(gui)* Don't use windowed mode for launchpad if on Python 3.14 - ([66688c6](https://github.com/aignostics/python-sdk/commit/66688c60d46881d128bfa3b9174a53012199c9a6))
- *(wsi)* Reject running wsi dicom commands on Python 3.14, given transitive dependency of highdicom not yet supported on that Python version - ([66688c6](https://github.com/aignostics/python-sdk/commit/66688c60d46881d128bfa3b9174a53012199c9a6))

### 🛡️ Security

- *(deps)* Don't use override-dependencies as this is not respected by uvx, but use regular dependency trees - ([66688c6](https://github.com/aignostics/python-sdk/commit/66688c60d46881d128bfa3b9174a53012199c9a6))


# [v0.2.231](https://github.com/aignostics/python-sdk/compare/v0.2.230..v0.2.231) - 2025-12-09

### 🧪 Testing

- Fix skip - ([cdb67fa](https://github.com/aignostics/python-sdk/commit/cdb67fa00a78cd55530a26421c721a9c49015581))
- Disable test_cli_application_run_prepare_upload_submit_fail_on_mpp given changed error message in heta - ([cad6763](https://github.com/aignostics/python-sdk/commit/cad6763fe348ba095e9382b0db7869698c643e71))
- Fix broken tests ([#327](https://github.com/aignostics/python-sdk/pull/327)) - ([8524a6b](https://github.com/aignostics/python-sdk/commit/8524a6b9e9a4545337f5922ca378339b7fd23f91))

### ⚙️ Miscellaneous Tasks

- *(deps)* Nicegui 3.4.0 and urllib 2.6.1 ([#326](https://github.com/aignostics/python-sdk/pull/326)) - ([0ee9ecd](https://github.com/aignostics/python-sdk/commit/0ee9ecd2df13ce6cb23ba27d44add2bbcd510a78))
- *(deps)* Bump astral-sh/setup-uv from 7.1.4 to 7.1.5 ([#324](https://github.com/aignostics/python-sdk/pull/324)) - ([a62286e](https://github.com/aignostics/python-sdk/commit/a62286e5785691f5b6c5c1a5c909a70170fcc88b))
- *(gha)* No longer build natively for Windows on ARM - ([86bdf17](https://github.com/aignostics/python-sdk/commit/86bdf176e6afe551e456ab101b9f4902cd69f8af))
- Oliver Meyer <42039965+olivermeyer@users.noreply.github.com> - ([0ee9ecd](https://github.com/aignostics/python-sdk/commit/0ee9ecd2df13ce6cb23ba27d44add2bbcd510a78))
- Bump macos-13 runner to macos-15-intel ([#328](https://github.com/aignostics/python-sdk/pull/328)) - ([b85ab72](https://github.com/aignostics/python-sdk/commit/b85ab72db56fedc3f00a79b169468629e74026ec))
- Astral-sh/setup-uv - ([a62286e](https://github.com/aignostics/python-sdk/commit/a62286e5785691f5b6c5c1a5c909a70170fcc88b))
- Dependabot[bot] <support@github.com> - ([a62286e](https://github.com/aignostics/python-sdk/commit/a62286e5785691f5b6c5c1a5c909a70170fcc88b))
- Dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com> - ([a62286e](https://github.com/aignostics/python-sdk/commit/a62286e5785691f5b6c5c1a5c909a70170fcc88b))
- Helmut Hoffer von Ankershoffen né Oertel <helmut@aignostics.com> - ([a62286e](https://github.com/aignostics/python-sdk/commit/a62286e5785691f5b6c5c1a5c909a70170fcc88b))
- Increase stress test slides - ([c67289a](https://github.com/aignostics/python-sdk/commit/c67289ab898c653c0208fd5142ada15bfe8beefc))


# [v0.2.230](https://github.com/aignostics/python-sdk/compare/v0.2.229..v0.2.230) - 2025-12-08

### ⛰️  Features

- *(application)* 30s page timeout for home as well - ([a1245f7](https://github.com/aignostics/python-sdk/commit/a1245f7a26dada68a34a22e142d82f1f7ebfca9a))


# [v0.2.229](https://github.com/aignostics/python-sdk/compare/v0.2.228..v0.2.229) - 2025-12-07

### 📚 Documentation

- *(readme)* Introduce sequence diagram - ([bdac6bd](https://github.com/aignostics/python-sdk/commit/bdac6bdc620ffa2c7c9cd5813729d41d164e2ebd))

### 🧪 Testing

- *(gui)* Enabel gui tests for macos on arm - ([45a4ef7](https://github.com/aignostics/python-sdk/commit/45a4ef702bef59cc4d7f213c25abdb8ccfa8d4c3))


# [v0.2.228](https://github.com/aignostics/python-sdk/compare/v0.2.226..v0.2.228) - 2025-12-07

### 📚 Documentation

- *(nicegui)* Bump attributions - ([0101310](https://github.com/aignostics/python-sdk/commit/0101310c6bf05eadd79720fc118734f7a35c8722))

### ⚙️ Miscellaneous Tasks

- *(application)* Bump timeout for application run and application run describe page from 3s to 30s - ([56eeff5](https://github.com/aignostics/python-sdk/commit/56eeff54b38f0fe4a3acf4478c32db17a484e64d))
- *(gui)* Refactor to enable bump to nicegui 3.3.1 - ([56eeff5](https://github.com/aignostics/python-sdk/commit/56eeff54b38f0fe4a3acf4478c32db17a484e64d))


# [v0.2.226](https://github.com/aignostics/python-sdk/compare/v0.2.225..v0.2.226) - 2025-12-06

### ⛰️  Features

- *(cli)* Print python version in epilog - ([7182533](https://github.com/aignostics/python-sdk/commit/7182533fc8fa22b192dae96ddefada2830f24c33))
- *(core)* Support for python 3.14.x ([#321](https://github.com/aignostics/python-sdk/pull/321)) - ([7182533](https://github.com/aignostics/python-sdk/commit/7182533fc8fa22b192dae96ddefada2830f24c33))
- *(core)* Support for python 3.14.x - ([7182533](https://github.com/aignostics/python-sdk/commit/7182533fc8fa22b192dae96ddefada2830f24c33))

### 🚜 Refactor

- *(platform)* Adapt to PEP 649 given we shadow list ... - ([7182533](https://github.com/aignostics/python-sdk/commit/7182533fc8fa22b192dae96ddefada2830f24c33))
- *(various)* Given issues identified by SonarQube - ([4623101](https://github.com/aignostics/python-sdk/commit/462310106d03018439c5c05c314f6957f678072c))

### 📚 Documentation

- Introduce mermaid support - ([7182533](https://github.com/aignostics/python-sdk/commit/7182533fc8fa22b192dae96ddefada2830f24c33))
- Update - ([7182533](https://github.com/aignostics/python-sdk/commit/7182533fc8fa22b192dae96ddefada2830f24c33))

### ⚡ Performance

- *(gui,utils,wsi)* Lazy load nicegui - ([7182533](https://github.com/aignostics/python-sdk/commit/7182533fc8fa22b192dae96ddefada2830f24c33))

### 🧪 Testing

- *(platform)* Use L4 provisioning mode on staging (was A100) - ([cd6d34a](https://github.com/aignostics/python-sdk/commit/cd6d34a264abbdb615265101c160ea9eb1bcb15f))
- *(platform)* Use SPOT provisioning mode on staging (was FLEX_START) - ([a6ca29a](https://github.com/aignostics/python-sdk/commit/a6ca29a696d6a27226f892fd62596609a2118beb))

### ⚙️ Miscellaneous Tasks

- *(ai)* Remove sticky again - ([e82db37](https://github.com/aignostics/python-sdk/commit/e82db379631838ddee4d26e9ed46294df66a2a49))
- *(ai)* Sticky broken with claude - ([d6fe1bc](https://github.com/aignostics/python-sdk/commit/d6fe1bcfe85e56a1c38feab65db83667f5b10987))
- *(ai)* Use stick comment in claude pr reviews - ([2d817da](https://github.com/aignostics/python-sdk/commit/2d817da1ecb8250a8a048f888a05af2144540ec9))
- *(audit)* Allow Zope Public License for audit - ([4623101](https://github.com/aignostics/python-sdk/commit/462310106d03018439c5c05c314f6957f678072c))
- *(deps)* Bump actions/checkout from 5.0.1 to 6.0.1 ([#307](https://github.com/aignostics/python-sdk/pull/307)) - ([f075d73](https://github.com/aignostics/python-sdk/commit/f075d73da91774f9185203d7e59cee6dc8f42a76))
- *(deps)* Bump docker/setup-qemu-action from 3.6.0 to 3.7.0 ([#247](https://github.com/aignostics/python-sdk/pull/247)) - ([2ccc420](https://github.com/aignostics/python-sdk/commit/2ccc420fb8bdb1b3bb4445a880fb7216c2c49102))
- *(deps)* Update anthropics/claude-code-action action to v1.0.22 ([#231](https://github.com/aignostics/python-sdk/pull/231)) - ([17cd8ea](https://github.com/aignostics/python-sdk/commit/17cd8ea25eb4470f718d09ea9797735de485af6e))
- *(deps)* Bump - ([4623101](https://github.com/aignostics/python-sdk/commit/462310106d03018439c5c05c314f6957f678072c))
- *(docker)* Give more time for bytecode compilation with python 3.14 on github with qemu for arm - ([b8afdff](https://github.com/aignostics/python-sdk/commit/b8afdff977cdd6c6ee77637dfd42b149d1fdd228))
- *(gha)* Limit track progress to where it works - ([b89c11f](https://github.com/aignostics/python-sdk/commit/b89c11fa30e9eb2a0baa83dc3a0589ab73893d71))
- *(native)* Don't use splash for native linux with python 3.14 - ([b8afdff](https://github.com/aignostics/python-sdk/commit/b8afdff977cdd6c6ee77637dfd42b149d1fdd228))
- Actions/checkout - ([f075d73](https://github.com/aignostics/python-sdk/commit/f075d73da91774f9185203d7e59cee6dc8f42a76))
- Dependabot[bot] <support@github.com> - ([f075d73](https://github.com/aignostics/python-sdk/commit/f075d73da91774f9185203d7e59cee6dc8f42a76))
- Dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com> - ([f075d73](https://github.com/aignostics/python-sdk/commit/f075d73da91774f9185203d7e59cee6dc8f42a76))
- Helmut Hoffer von Ankershoffen né Oertel <helmut@aignostics.com> - ([f075d73](https://github.com/aignostics/python-sdk/commit/f075d73da91774f9185203d7e59cee6dc8f42a76))
- Docker/setup-qemu-action - ([2ccc420](https://github.com/aignostics/python-sdk/commit/2ccc420fb8bdb1b3bb4445a880fb7216c2c49102))
- Renovate[bot] <29139614+renovate[bot]@users.noreply.github.com> - ([17cd8ea](https://github.com/aignostics/python-sdk/commit/17cd8ea25eb4470f718d09ea9797735de485af6e))

### 🛡️ Security

- *(install)* Bash and ensure ssl - ([4623101](https://github.com/aignostics/python-sdk/commit/462310106d03018439c5c05c314f6957f678072c))


# [v0.2.225](https://github.com/aignostics/python-sdk/compare/v0.2.224..v0.2.225) - 2025-12-06

### ⚙️ Miscellaneous Tasks

- Reduce slides per run for stress test to 50 to clear scheduler queue. - ([3002543](https://github.com/aignostics/python-sdk/commit/30025430c45a797a42c2f8437e142b67622e0b75))

### 🛡️ Security

- *(dep)* Require urllib3 >= 2.6.0 given CVE-2025-66471 (GHSA-2xpw-w6gg-jr37); dep of boto3, dicomweb-client and others - ([72e862c](https://github.com/aignostics/python-sdk/commit/72e862c927a8bb8193c4e8baf03fcd16835012c0))


# [v0.2.224](https://github.com/aignostics/python-sdk/compare/v0.2.223..v0.2.224) - 2025-12-04

### 🐛 Bug Fixes

- Prevent Launchpad crash with FastAPI 0.123.7+ ([#317](https://github.com/aignostics/python-sdk/pull/317)) - ([49b2aa8](https://github.com/aignostics/python-sdk/commit/49b2aa8563219e74a494465a95f4c74629a1a5b4))

### 🧪 Testing

- Set TTL for signed URLs to deadline + 10 hours - ([f6b937a](https://github.com/aignostics/python-sdk/commit/f6b937aa8f18af95bcb7a8a5dc71a32902b81802))
- Set deadline for HETA tests to 24h - ([3ac09c2](https://github.com/aignostics/python-sdk/commit/3ac09c2c04f4b1636df947b338155857730988c8))
- Fix flaky CLI test ([#313](https://github.com/aignostics/python-sdk/pull/313)) - ([cc27a94](https://github.com/aignostics/python-sdk/commit/cc27a945c063a901fc303cbfccb092e338fe628d))


# [v0.2.223](https://github.com/aignostics/python-sdk/compare/v0.2.222..v0.2.223) - 2025-12-04

### ⛰️  Features

- Support validation case in tags ([#275](https://github.com/aignostics/python-sdk/pull/275)) - ([89343fc](https://github.com/aignostics/python-sdk/commit/89343fc6bbd824b1bd520aeeb0589806ee239fa4))

### 🐛 Bug Fixes

- *(logging)* Log format to be compatible with loguru - ([974fcca](https://github.com/aignostics/python-sdk/commit/974fccaf8175801adbb0c2b5c40046e51dfa64c1))
- Move FastAPI imports to function scope ([#315](https://github.com/aignostics/python-sdk/pull/315)) - ([1bcce1b](https://github.com/aignostics/python-sdk/commit/1bcce1b6765c8ec997c9500080e632a180186447))
- Restore ATTRIBUTIONS.md (generated file should not be modified) [skip:ci, skip:test:long-running, skip:test:matrix-runner, skip:test:very-long-running] - ([24539ce](https://github.com/aignostics/python-sdk/commit/24539ce96ba4182de7a340a96aaa6c4a5d03171d))

### 🚜 Refactor

- *(platform)* Remove superfluous function calls in run submit - ([81752df](https://github.com/aignostics/python-sdk/commit/81752dfb51c7a11f47566c5778cc738b827f7c89))

### 📚 Documentation

- Add installation requirements to user documentation [skip:ci, skip:test:long-running, skip:test:matrix-runner, skip:test:very-long-running] - ([1caa5c8](https://github.com/aignostics/python-sdk/commit/1caa5c8135d624a960e9a63a1aa5c008c82437a0))

### ⚡ Performance

- *(platform)* _get_spots_payload_for_special for 100k items - ([b7a8e09](https://github.com/aignostics/python-sdk/commit/b7a8e09c97334504aa3a84c53e85ff916466164d))
- *(platform)* Pre-built item sdk metadata - ([4a36778](https://github.com/aignostics/python-sdk/commit/4a36778790dc1d5a42c4aaa462a3993247997aac))

### 🧪 Testing

- *(platform)* Consistently use SPOT_1_GS_URL and _FILENAME so it can be changed easily for maintenance - ([251b097](https://github.com/aignostics/python-sdk/commit/251b097f57d7bee26fd51632b5a271e6e3a8168a))

### ⚙️ Miscellaneous Tasks

- *(deps)* Update docker/metadata-action action to v5.10.0 ([#303](https://github.com/aignostics/python-sdk/pull/303)) - ([89e4926](https://github.com/aignostics/python-sdk/commit/89e492664b43929e54f7757fa4e436aff4afa11c))
- *(gha)* Fix track progress for oe report - ([e96452e](https://github.com/aignostics/python-sdk/commit/e96452e55d4add7074397f67ddd9e893fe0a9ccb))
- Reduce items per run to 800 for stress test - ([9f43596](https://github.com/aignostics/python-sdk/commit/9f435969a0403ba5d51b8889170c9c4ce2c560a0))
- Upgrade to Python 3.13.10 ([#312](https://github.com/aignostics/python-sdk/pull/312)) - ([363e1c7](https://github.com/aignostics/python-sdk/commit/363e1c76829ea29a30967e5e8e288e9eaccdeb95))
- Stop passing GCP secrets to Claude workflows ([#311](https://github.com/aignostics/python-sdk/pull/311)) - ([fe9149f](https://github.com/aignostics/python-sdk/commit/fe9149f99cd40b5978eb3413363b521cb6540a49))
- Reenable stress tests with 1k items - ([0751c5c](https://github.com/aignostics/python-sdk/commit/0751c5c9316d2f817dde7fe4e1b56cd6f19cb2ea))
- Renovate[bot] <29139614+renovate[bot]@users.noreply.github.com> - ([89e4926](https://github.com/aignostics/python-sdk/commit/89e492664b43929e54f7757fa4e436aff4afa11c))


# [v0.2.222](https://github.com/aignostics/python-sdk/compare/v0.2.221..v0.2.222) - 2025-12-02

### ⛰️  Features

- Show accepted file extensions in Launchpad ([#298](https://github.com/aignostics/python-sdk/pull/298)) - ([2efab98](https://github.com/aignostics/python-sdk/commit/2efab98bf942c895afa0dca3c20a7b14fa0f7886))

### 🐛 Bug Fixes

- Resolve NiceGUI drawer JavaScript timeout on run results ([#305](https://github.com/aignostics/python-sdk/pull/305)) - ([51f7434](https://github.com/aignostics/python-sdk/commit/51f7434c762f5d9ae0e976828d36aee515178f08))

### 🧪 Testing

- *(platform)* Pause stress tests due to overwhelming load - ([2617a05](https://github.com/aignostics/python-sdk/commit/2617a0545451dc8000353be16cdebbb85039c6ba))
- *(platform)* Stress tests, 0..99 with 10k slides - ([300a647](https://github.com/aignostics/python-sdk/commit/300a647ed497945c78e8f211cc1f47a5d6b82de4))

### ⚙️ Miscellaneous Tasks

- Update version in CLI_REFERENCE.md on bump ([#300](https://github.com/aignostics/python-sdk/pull/300)) - ([7cd1aad](https://github.com/aignostics/python-sdk/commit/7cd1aaddeda5dc14d5aeada2de8458d382d29fea))



* @arne-aignx made their first contribution

# [v0.2.221](https://github.com/aignostics/python-sdk/compare/v0.2.219..v0.2.221) - 2025-12-02

### ⚙️ Miscellaneous Tasks

- *(deps)* Update docker/setup-qemu-action action to v3.7.0 ([#304](https://github.com/aignostics/python-sdk/pull/304)) - ([ba881b7](https://github.com/aignostics/python-sdk/commit/ba881b72e00152c22d5ad293ea99f8aefd6e4f13))
- *(deps)* Bump docker/metadata-action from 5.8.0 to 5.9.0 ([#246](https://github.com/aignostics/python-sdk/pull/246)) - ([bfcfa61](https://github.com/aignostics/python-sdk/commit/bfcfa61ceb3df1589bdc4e24eaee693f2ae5b338))
- *(deps)* Bump getsentry/action-release from 3.3.0 to 3.4.0 ([#242](https://github.com/aignostics/python-sdk/pull/242)) - ([e445a6a](https://github.com/aignostics/python-sdk/commit/e445a6a9aa2206472d0610e9129437e3db6ce4cc))
- *(deps)* Bump idc-index-data from 22.1.5 to 23.0.1 ([#277](https://github.com/aignostics/python-sdk/pull/277)) - ([ee4c7b7](https://github.com/aignostics/python-sdk/commit/ee4c7b781bc4a4c40e631c976c3a466e0531ee1e))
- *(deps)* Update dependency hatchling to v1.28.0 ([#302](https://github.com/aignostics/python-sdk/pull/302)) - ([a96c8cd](https://github.com/aignostics/python-sdk/commit/a96c8cd46712b3c2d30b2b818f77706c6085a9bf))
- *(deps-dev)* Bump hatchling from 1.27.0 to 1.28.0 ([#290](https://github.com/aignostics/python-sdk/pull/290)) - ([c908758](https://github.com/aignostics/python-sdk/commit/c9087580f976425d4ab42d78893bcaa94e1625e9))
- Remove unused pyjpegls given not compatible with 3.14 as of today - ([248def6](https://github.com/aignostics/python-sdk/commit/248def63ca775a4dfd2123294199f0be83ad0ae2))
- Hatchling - ([c908758](https://github.com/aignostics/python-sdk/commit/c9087580f976425d4ab42d78893bcaa94e1625e9))
- Dependabot[bot] <support@github.com> - ([c908758](https://github.com/aignostics/python-sdk/commit/c9087580f976425d4ab42d78893bcaa94e1625e9))
- Dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com> - ([c908758](https://github.com/aignostics/python-sdk/commit/c9087580f976425d4ab42d78893bcaa94e1625e9))
- Helmut Hoffer von Ankershoffen né Oertel <helmut@aignostics.com> - ([c908758](https://github.com/aignostics/python-sdk/commit/c9087580f976425d4ab42d78893bcaa94e1625e9))
- Renovate[bot] <29139614+renovate[bot]@users.noreply.github.com> - ([ba881b7](https://github.com/aignostics/python-sdk/commit/ba881b72e00152c22d5ad293ea99f8aefd6e4f13))
- Docker/metadata-action - ([bfcfa61](https://github.com/aignostics/python-sdk/commit/bfcfa61ceb3df1589bdc4e24eaee693f2ae5b338))
- Getsentry/action-release - ([e445a6a](https://github.com/aignostics/python-sdk/commit/e445a6a9aa2206472d0610e9129437e3db6ce4cc))
- Idc-index-data - ([ee4c7b7](https://github.com/aignostics/python-sdk/commit/ee4c7b781bc4a4c40e631c976c3a466e0531ee1e))


# [v0.2.219](https://github.com/aignostics/python-sdk/compare/v0.2.217..v0.2.219) - 2025-12-01

### 🎨 Styling

- *(install.sh)* Use package correctly - ([94d3197](https://github.com/aignostics/python-sdk/commit/94d31971c435011f02a00ec6908edbe76efe9c34))

### 🧪 Testing

- *(platform)* Stopped stress tests - ([0e6e80e](https://github.com/aignostics/python-sdk/commit/0e6e80e719ec8bef62c011805788c4723ea55846))

### ⚙️ Miscellaneous Tasks

- *(deps)* Update github artifact actions ([#238](https://github.com/aignostics/python-sdk/pull/238)) - ([b32e20a](https://github.com/aignostics/python-sdk/commit/b32e20ae3d0404baa13c8718a7a6562d897b6fdc))
- *(deps)* Update ghcr.io/astral-sh/uv docker tag to v0.9.14 ([#280](https://github.com/aignostics/python-sdk/pull/280)) - ([d348c62](https://github.com/aignostics/python-sdk/commit/d348c6215437dcaa1f13c5e3ccdc8c63fe4d34e0))
- *(deps)* Bump astral-sh/setup-uv from 7.1.1 to 7.1.4 ([#278](https://github.com/aignostics/python-sdk/pull/278)) - ([449358c](https://github.com/aignostics/python-sdk/commit/449358c053bf68861481c65183330e34ffc79af1))
- *(deps)* Update actions/checkout action to v5.0.1 ([#279](https://github.com/aignostics/python-sdk/pull/279)) - ([f9a25a1](https://github.com/aignostics/python-sdk/commit/f9a25a1923dc8dbd6ec86527ca3dc7c15ddfb278))
- *(install.sh)* Use package correctly for uv - ([db601de](https://github.com/aignostics/python-sdk/commit/db601dec6e268e33c82b9874ba312a25d86f6804))
- Renovate[bot] <29139614+renovate[bot]@users.noreply.github.com> - ([b32e20a](https://github.com/aignostics/python-sdk/commit/b32e20ae3d0404baa13c8718a7a6562d897b6fdc))
- Helmut Hoffer von Ankershoffen né Oertel <helmut@aignostics.com> - ([b32e20a](https://github.com/aignostics/python-sdk/commit/b32e20ae3d0404baa13c8718a7a6562d897b6fdc))
- Astral-sh/setup-uv - ([449358c](https://github.com/aignostics/python-sdk/commit/449358c053bf68861481c65183330e34ffc79af1))
- Dependabot[bot] <support@github.com> - ([449358c](https://github.com/aignostics/python-sdk/commit/449358c053bf68861481c65183330e34ffc79af1))
- Dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com> - ([449358c](https://github.com/aignostics/python-sdk/commit/449358c053bf68861481c65183330e34ffc79af1))

### 🛡️ Security

- *(dep)* Override fonttools given CVE-2025-66034 (GHSA-768j-98cg-p3fv), dep of matplotlib - ([94e985f](https://github.com/aignostics/python-sdk/commit/94e985f962bc6c59ccd493a0b960e7a61706033c))


# [v0.2.217](https://github.com/aignostics/python-sdk/compare/v0.2.216..v0.2.217) - 2025-12-01

### 🐛 Bug Fixes

- *(application,bucket,dataset)* Remove use of aiopath which turns out to not be compatible with python 3.11.x as advertised - ([238d47a](https://github.com/aignostics/python-sdk/commit/238d47af14f11570f0763eab605dec44bb5f9bb6))
- Replace tkinter.NONE with literal to support Python 3.13.9 on macOS ([#296](https://github.com/aignostics/python-sdk/pull/296)) - ([28d4b32](https://github.com/aignostics/python-sdk/commit/28d4b328bfb498b787c7bc21c097cd65dc6d1b0f))

### 🧪 Testing

- *(platform)* Reenable flex start for hourly tests against staging - ([2d4e382](https://github.com/aignostics/python-sdk/commit/2d4e382c31472f6ee67068881925b87e09e6a7bb))
- Fix flaky GUI tests ([#297](https://github.com/aignostics/python-sdk/pull/297)) - ([c9815ec](https://github.com/aignostics/python-sdk/commit/c9815ec8bbbfdc302a02a19031b737466ebf48d5))

### ⚙️ Miscellaneous Tasks

- *(gha)* Use github token on labels sync / checkout, given our repo is not public - ([b0202de](https://github.com/aignostics/python-sdk/commit/b0202dec331c74745392d316c66096cec176d63d))
- *(gha)* Use github token for checkout on labels sync - ([1814d80](https://github.com/aignostics/python-sdk/commit/1814d80479d145d31c97ad575def1baad3439255))


# [v0.2.216](https://github.com/aignostics/python-sdk/compare/v0.2.214..v0.2.216) - 2025-12-01

### 🐛 Bug Fixes

- Paginate run results ([#295](https://github.com/aignostics/python-sdk/pull/295)) - ([0e5d821](https://github.com/aignostics/python-sdk/commit/0e5d821775eaff34617822fcf7c2e1c3a79e4eaa))

### 🧪 Testing

- *(platform)* Fix title for stress test - ([993c845](https://github.com/aignostics/python-sdk/commit/993c845807f1626c07e9ad9e658b304e41451961))
- *(platform)* Fix setting - ([1b72717](https://github.com/aignostics/python-sdk/commit/1b727177d7284a477db6ad10a341d23c9bab16e2))
- *(platform)* On 20 - ([da3664c](https://github.com/aignostics/python-sdk/commit/da3664c033a4be465a4d29eb36bc359e550b0bc0))
- *(platform)* Prep for 30min node acquisition timeout on production - ([2725077](https://github.com/aignostics/python-sdk/commit/27250777b31c28bfd18faa28a6498f83ffe07757))
- *(platform)* Use 1k on staging 0..9 min - ([e674a58](https://github.com/aignostics/python-sdk/commit/e674a589b95249915b31861ad71884706bf21acd))
- *(platform)* Use spot on staging - ([7dabb89](https://github.com/aignostics/python-sdk/commit/7dabb89d802380448a4919bd74400e227d80cdec))


# [v0.2.214](https://github.com/aignostics/python-sdk/compare/v0.2.213..v0.2.214) - 2025-12-01

### 🐛 Bug Fixes

- Remove validate_only option - ([e838bd9](https://github.com/aignostics/python-sdk/commit/e838bd9b0f06247eda40d71851f8a116b2977418))
- Make inspect command work with a single file as input as well - ([5c651d1](https://github.com/aignostics/python-sdk/commit/5c651d150384e3cbdc36ae1fcc017db36eafe081))

### 🧪 Testing

- *(platform)* On_00 to 100 items - ([b5b29f3](https://github.com/aignostics/python-sdk/commit/b5b29f3de84119eea8a539bb7b8195dffa8deeb1))
- *(platform)* For stress test - 3h due date and deadline if test triggered in minute 40 to 49, 1k items if triggered in minute 0..9, triggering every 10 minutes, was every 5 minutes - ([e8d0aa5](https://github.com/aignostics/python-sdk/commit/e8d0aa5ed7f2634e381be4e9e64997d3e9891c98))
- Disable flaky GUI tests on macos-latest and python 3.13 ([#293](https://github.com/aignostics/python-sdk/pull/293)) - ([35aeab6](https://github.com/aignostics/python-sdk/commit/35aeab6427758c8bdf21644180b0ef1b9c1ebd8f))



* @neelay-aign made their first contribution in [#291](https://github.com/aignostics/python-sdk/pull/291)

# [v0.2.213](https://github.com/aignostics/python-sdk/compare/v0.2.212..v0.2.213) - 2025-11-28

### ⛰️  Features

- *(platform, application)* Introduce flex start ([#292](https://github.com/aignostics/python-sdk/pull/292)) - ([8122a49](https://github.com/aignostics/python-sdk/commit/8122a49a728a6ff8368f509e23b0b6fc86700ad9))
- *(platform, application)* Introduce flex start - ([8122a49](https://github.com/aignostics/python-sdk/commit/8122a49a728a6ff8368f509e23b0b6fc86700ad9))

### 🐛 Bug Fixes

- Download single artifact - ([49941e0](https://github.com/aignostics/python-sdk/commit/49941e0063c294cb33b7bc95b1643ace3781dd2f))
- Revert CLI_REFERENCE.md to remove hardcoded timestamps [skip:ci, skip:test:long-running, skip:test:matrix-runner] - ([739687a](https://github.com/aignostics/python-sdk/commit/739687aa3dbaa018b7e244d6009a56e6bd162f5e))
- Unify mapping usage and docs - ([e5c164e](https://github.com/aignostics/python-sdk/commit/e5c164e7e64252e660320e1c323d386be061068f))
- Edit profile button opens new tab ([#286](https://github.com/aignostics/python-sdk/pull/286)) - ([176c128](https://github.com/aignostics/python-sdk/commit/176c1285ada86226c77cee25c4b2d638d30d5b83))
- Handle incomplete DICOM pyramid when getting thumbnail ([#281](https://github.com/aignostics/python-sdk/pull/281)) - ([9caa6e1](https://github.com/aignostics/python-sdk/commit/9caa6e14c84175d48ce14b3ef077094f91ab4598))

### 📚 Documentation

- Regenerate README.md from partials to remove duplicate pip section [skip:ci, skip:test:long-running, skip:test:matrix-runner] - ([40221ef](https://github.com/aignostics/python-sdk/commit/40221ef82657e5e2d0fb4b9eae65d744f0c4e6bc))
- Regenerate CLI reference with generic paths [skip:ci, skip:test:long-running, skip:test:matrix-runner] - ([fcd3376](https://github.com/aignostics/python-sdk/commit/fcd3376ad5bf40023831bbdf1f42aed70d3f1940))
- Add quick start to public documentation [skip:ci, skip:test:long-running, skip:test:matrix-runner, skip:test:very-long-running] - ([18a6c19](https://github.com/aignostics/python-sdk/commit/18a6c19093152d0b7f38c23f15a30856616157ef))
- Update fix lint issues [skip:ci, skip:test:long-running, skip:test:matrix-runner, skip:test:very-long-running] - ([3e0a51c](https://github.com/aignostics/python-sdk/commit/3e0a51cddd5dd05a54e0f5f7563989095b30c278))
- Update readthedocs documentation [skip:ci, skip:test:long-running, skip:test:matrix-runner, skip:test:very-long-running] - ([8065d34](https://github.com/aignostics/python-sdk/commit/8065d3441b12dbd0240794ca3b8cb2b45afdf56c))
- Remove requirement type comment to fix issue with Ketryx - ([5c85726](https://github.com/aignostics/python-sdk/commit/5c85726d28bc3c5939bedae3840143969f24c872))

### 🧪 Testing

- *(platform)* Test flex start on staging - ([8122a49](https://github.com/aignostics/python-sdk/commit/8122a49a728a6ff8368f509e23b0b6fc86700ad9))


# [v0.2.212](https://github.com/aignostics/python-sdk/compare/v0.2.211..v0.2.212) - 2025-11-25

### ⛰️  Features

- *(platform,application)* Introduce configurable node acquisition timeout, defaulting to 30 minutes - ([24d8710](https://github.com/aignostics/python-sdk/commit/24d871018b602f278035ce034aa63c47c3fcb299))

### 📚 Documentation

- Bump custom sdk metadata schema version - ([5022dad](https://github.com/aignostics/python-sdk/commit/5022dad60538a2c5ad33a1413c9d7ef3242d198e))

### 🧪 Testing

- *(platform)* Sl.4.1 -> sl.4 - ([0a3049b](https://github.com/aignostics/python-sdk/commit/0a3049b5dd1fea219f78c593686b14ce40eb8d24))
- *(platform)* Test-app v0.99.0, 100 items per run, every 15 min - ([7a30dc1](https://github.com/aignostics/python-sdk/commit/7a30dc16db676c8b678137410f2674fcbe9e895e))
- *(platform)* Production: L4 (was A100); staging: node sl4.1 (was sl4) - ([f697a63](https://github.com/aignostics/python-sdk/commit/f697a631f02f9b6a931131dfb442327ba1666640))
- *(stress)* Every 5 minutes (was 15) - ([f347ada](https://github.com/aignostics/python-sdk/commit/f347ada9969d2069fa280d0441a5d81c3c97f742))


# [v0.2.211](https://github.com/aignostics/python-sdk/compare/v0.2.210..v0.2.211) - 2025-11-23

### 🧪 Testing

- *(platform)* Target L4, SPOT in hourly scheduled tests on staging - ([dc9f490](https://github.com/aignostics/python-sdk/commit/dc9f49048a7f51191b79d52015678fbe921d7ebd))


# [v0.2.210](https://github.com/aignostics/python-sdk/compare/v0.2.209..v0.2.210) - 2025-11-23

### 🧪 Testing

- *(platform)* Target A100, SPOT in hourly scheduled tests, both staging and production - ([1adb4a6](https://github.com/aignostics/python-sdk/commit/1adb4a69c7aa869f92d14075cd00358e41ae7515))
- *(platform)* Reactivate hourly scheduled teests - ([4027861](https://github.com/aignostics/python-sdk/commit/4027861527a29bff424442e7e15f701dcf5a4d85))
- *(staging)* Hourly staging tests deactivated for maintenance - ([501571c](https://github.com/aignostics/python-sdk/commit/501571c066c7caeb27e40e26a004fbba06f354bd))
- *(stress)* Test_platform_special_app_submit deactivation - ([b78548b](https://github.com/aignostics/python-sdk/commit/b78548b6409129b5ad9d4899bd0aa5af4d0a8e59))
- *(system)* Tweak test - ([ea1e864](https://github.com/aignostics/python-sdk/commit/ea1e864377ca32f45dbdcb92608f9b5a9cf94cc3))
- *(system)* Test_gui_system_health_shown_and_updated debug - ([41501ae](https://github.com/aignostics/python-sdk/commit/41501ae453c443cc2e8522bf33112bc3a9fbae81))
- *(system)* Test_gui_system_health_shown_and_updated sequential - ([3f588bc](https://github.com/aignostics/python-sdk/commit/3f588bc46a37844a7d928b22b20c53163cf06c33))
- *(wsi)* Bump timeout for dicom inspect tests - ([e7e950f](https://github.com/aignostics/python-sdk/commit/e7e950f306ae654c3e6416bc0d07eb3d94b7e289))

### ⚙️ Miscellaneous Tasks

- *(application)* Lower log level if runs cannot be loaded on application shutdown - ([ea1e864](https://github.com/aignostics/python-sdk/commit/ea1e864377ca32f45dbdcb92608f9b5a9cf94cc3))
- *(bots)* Skip codecov on renovate and dependabot - ([4027861](https://github.com/aignostics/python-sdk/commit/4027861527a29bff424442e7e15f701dcf5a4d85))
- *(gha)* Don't codecov on dependabot or renovate - ([f4063f8](https://github.com/aignostics/python-sdk/commit/f4063f850e632f25e23fcf17f8e4f2494bc0d2d6))
- *(ketryx)* Fix typo in download action - ([e7e950f](https://github.com/aignostics/python-sdk/commit/e7e950f306ae654c3e6416bc0d07eb3d94b7e289))
- *(logging)* Disable redirect logging by default - ([ea1e864](https://github.com/aignostics/python-sdk/commit/ea1e864377ca32f45dbdcb92608f9b5a9cf94cc3))
- *(platform)* Enable special app in prod - ([ea1e864](https://github.com/aignostics/python-sdk/commit/ea1e864377ca32f45dbdcb92608f9b5a9cf94cc3))


# [v0.2.209](https://github.com/aignostics/python-sdk/compare/v0.2.208..v0.2.209) - 2025-11-21

### ⛰️  Features

- *(application)* Allow to list and describe application and runs with the output being json - ([c995ebe](https://github.com/aignostics/python-sdk/commit/c995ebe616a6f8c28a7f709404d5ed6469c5aaff))
- *(application)* Allow to cancel runs matching a filter with criteria including application id, application version and tags. includes --dry-run option - ([c995ebe](https://github.com/aignostics/python-sdk/commit/c995ebe616a6f8c28a7f709404d5ed6469c5aaff))
- Feat/logging-redirect - ([15de455](https://github.com/aignostics/python-sdk/commit/15de4552b72008308d16f6184527ff9e9fcc0e3e))

### 🧪 Testing

- *(platform)* More tags for test_platform_special_app_submit - ([8c8beac](https://github.com/aignostics/python-sdk/commit/8c8beac0ea18f11b9c7f64312f683fd9f2e98796))
- *(platform)* Staging: L4, on-demand every 5 min - ([17a9edc](https://github.com/aignostics/python-sdk/commit/17a9edc710ef3ae429e172665e7dc55ccbb6f3a0))
- *(stress)* Support stress_only tests that only run on make test_stress and 5-minutely stress test schedule - ([8a16b36](https://github.com/aignostics/python-sdk/commit/8a16b36d237fcc5b64f3efc7440f063fb0c91703))
- *(stress)* Target 0.0.0-test.retry.bug.20.11 - ([2dc98bc](https://github.com/aignostics/python-sdk/commit/2dc98bc78980f1241604f1faccc4b705fd89e8cb))
- *(stress)* 5 minute stress tests - ([6a2a0e1](https://github.com/aignostics/python-sdk/commit/6a2a0e14dc123dce8af192a32e11250608763701))

### ⚙️ Miscellaneous Tasks

- *(docs)* Fix Utils Module Specification - ([a1ebc4a](https://github.com/aignostics/python-sdk/commit/a1ebc4aac221969f404687520a9286bfcac38fb1))
- *(docs)* Fix SPEC_WSI_SERVICE.md - ([07b991a](https://github.com/aignostics/python-sdk/commit/07b991a3ede2596ed043499a1ad7db1349cf4073))
- *(stress)* Workflow - ([ce39147](https://github.com/aignostics/python-sdk/commit/ce391478dcb38ce2b75b572d135948e6a2499912))


# [v0.2.208](https://github.com/aignostics/python-sdk/compare/v0.2.207..v0.2.208) - 2025-11-21

### ⛰️  Features

- *(application)* Show duration in run sidebar - ([ed583fd](https://github.com/aignostics/python-sdk/commit/ed583fd5a15e404ba5d3cf8296d0bde8280d90e6))


# [v0.2.207](https://github.com/aignostics/python-sdk/compare/v0.2.206..v0.2.207) - 2025-11-20

### 🧪 Testing

- *(application)* Auto-cancel custom pipeline tests - ([987d025](https://github.com/aignostics/python-sdk/commit/987d025a839f74429fbe3a2cd2aa6234df4d9ff8))
- *(system)* Mark test as sequential - ([0b90d06](https://github.com/aignostics/python-sdk/commit/0b90d066fae002b217eeb79af525b49d224b741d))


# [v0.2.206](https://github.com/aignostics/python-sdk/compare/v0.2.205..v0.2.206) - 2025-11-20

### 🐛 Bug Fixes

- *(application)* Pipeline settings in GUI and CLI ([#271](https://github.com/aignostics/python-sdk/pull/271)) - ([feaa047](https://github.com/aignostics/python-sdk/commit/feaa047d2608a302e162260606045b8c026e20fe))

### 🚜 Refactor

- *(application)* Reduce max items in sidebar from 500 to 200 - ([e8f07a9](https://github.com/aignostics/python-sdk/commit/e8f07a9659a009cf814930aafd4b32671354d680))

### 🧪 Testing

- *(application)* Proper integration tests for pipeline settings in GUI and CLI - ([feaa047](https://github.com/aignostics/python-sdk/commit/feaa047d2608a302e162260606045b8c026e20fe))
- *(platform,staging)* Switch to A100, ON_DEMAND, 1 (was L4, SPOT, 1) - ([4b8be3d](https://github.com/aignostics/python-sdk/commit/4b8be3d17527a8de71342a1fb693e73ce2aa7197))


# [v0.2.205](https://github.com/aignostics/python-sdk/compare/v0.2.204..v0.2.205) - 2025-11-20

### ⛰️  Features

- *(application)* GUI and CLI now use L4, SPOT, max=gpu=1 as defaults - ([37873c7](https://github.com/aignostics/python-sdk/commit/37873c72f39688300b63b06188f14e3a53daaf76))


# [v0.2.204](https://github.com/aignostics/python-sdk/compare/v0.2.203..v0.2.204) - 2025-11-20

### 🧪 Testing

- *(platform)* Config for staging now L4, SPOT, 1 GPU - was L4, Spot, 2 GPU; Config for production now L4, Spot, 1 GPU - was A100, ON-DEMAND, 1 GPU) - ([f2cc0bd](https://github.com/aignostics/python-sdk/commit/f2cc0bd712afe73a7ff891b469849060c5aec872))

### ⚙️ Miscellaneous Tasks

- *(platform)* Default config outside of tests now L4, SPOT, 1 GPU - was A100, ON-DEMAND, 1 GPU - ([f2cc0bd](https://github.com/aignostics/python-sdk/commit/f2cc0bd712afe73a7ff891b469849060c5aec872))


# [v0.2.203](https://github.com/aignostics/python-sdk/compare/v0.2.202..v0.2.203) - 2025-11-20

### ⛰️  Features

- *(application)* Better colors for runs and items, e.g. orange for canceled by user - ([182da63](https://github.com/aignostics/python-sdk/commit/182da631aaebf574d837057f1f4774696e5f7890))
- *(application)* Highlight runs which exceeded deadline while not yet having terminated yet in orange - ([182da63](https://github.com/aignostics/python-sdk/commit/182da631aaebf574d837057f1f4774696e5f7890))

### 🚜 Refactor

- *(application)* Bump runs shown in sidebar from 100 to 500 - ([182da63](https://github.com/aignostics/python-sdk/commit/182da631aaebf574d837057f1f4774696e5f7890))

### 🧪 Testing

- *(application)* 4h for test_cli_run_execute, and check exit - ([822bc6b](https://github.com/aignostics/python-sdk/commit/822bc6b6ba167c29cb6bd119361644ed071c6169))
- *(platform)* Tag test runs with "scheduled" if being so, for easier discoverability - ([182da63](https://github.com/aignostics/python-sdk/commit/182da631aaebf574d837057f1f4774696e5f7890))

### ⚙️ Miscellaneous Tasks

- *(deps)* Bump - ([182da63](https://github.com/aignostics/python-sdk/commit/182da631aaebf574d837057f1f4774696e5f7890))


# [v0.2.202](https://github.com/aignostics/python-sdk/compare/v0.2.201..v0.2.202) - 2025-11-19

### ⛰️  Features

- *(platform)* Sentry metrics on run submission - ([75f7ff6](https://github.com/aignostics/python-sdk/commit/75f7ff6168a3d2dd823463ccdbbd10a42c48c894))
- *(platform,application)* Configureable pipeline - ([1e4c94f](https://github.com/aignostics/python-sdk/commit/1e4c94f8fd6fc2f485b13681467719be0f91fd86))

### 🐛 Bug Fixes

- Test-app bump to 0.0.6 - ([e7818f2](https://github.com/aignostics/python-sdk/commit/e7818f28e85f2a716b2ef51ea2d0d5d9021bcdf8))

### 🚜 Refactor

- *(platform)* Print error code and message on download - ([cfecccc](https://github.com/aignostics/python-sdk/commit/cfeccccb001ac406aed99a3dedeea3d5cc941aa1))

### 🧪 Testing

- *(application)* Reactivate test_cli_run_submit_and_describe_and_cancel_and_download_and_delete against production - ([1e4c94f](https://github.com/aignostics/python-sdk/commit/1e4c94f8fd6fc2f485b13681467719be0f91fd86))
- *(application)* Tag run created by test_gui_cli_submit_to_run_result_delete - ([26304a6](https://github.com/aignostics/python-sdk/commit/26304a681942cdfa5c395924fcc584e1c634bf1a))
- *(application)* Skip test_application_version_use_latest_fallback on staging - ([f998734](https://github.com/aignostics/python-sdk/commit/f998734aaade32fbe72b9cd15cff8e3092e5c9e2))
- *(application)* Don't fail test_gui_index on js error logged - ([cd64a86](https://github.com/aignostics/python-sdk/commit/cd64a868925077bfc21cfef688cac4bed5e2eb92))
- *(application)* Skip test_cli_run_submit_and_describe_and_cancel_and_download_and_delete on production - ([45d52c7](https://github.com/aignostics/python-sdk/commit/45d52c704fcd9f7f0632411a8d3c7c9d10f542d5))
- *(platform)* Switched to 1.0.0-sl.4 from 1.0.0-sl.1 for production - ([e4ee905](https://github.com/aignostics/python-sdk/commit/e4ee905b5e52a0094a1f0883629b4b9be8f1c0c4))
- *(platform)* Switched to 1.0.0-sl.4 from 1.0.0-sl.1 for staging - ([973866b](https://github.com/aignostics/python-sdk/commit/973866b20e73203d6c8f476dc46d98b5973e50cf))
- *(platform)* Better info on deadline breached plus Sentry metrics - ([75f7ff6](https://github.com/aignostics/python-sdk/commit/75f7ff6168a3d2dd823463ccdbbd10a42c48c894))
- *(platform)* More details on runs breaching deadline - ([a6cbe1c](https://github.com/aignostics/python-sdk/commit/a6cbe1c4e9e75ab2082ac49c379a15f7af632e28))
- *(platform)* Don't require a run to have a deadline in the current hour - ([ac87f7c](https://github.com/aignostics/python-sdk/commit/ac87f7ceff88e0a266c6bbe2fc4264091f6f7496))
- *(platform)* Activate 2nd leg, i.e. find and validate tests - ([8590b6d](https://github.com/aignostics/python-sdk/commit/8590b6db502ed3605a74595c834962fa9220c429))
- *(platform)* Adapt - ([05c289a](https://github.com/aignostics/python-sdk/commit/05c289ab5326b4aca7efd2b7c5f5f5148eb22ef7))
- *(platform)* Switch heta scheduled test to leg 1: submit, and (eod) leg 2: find and validate, giving 12h deadline - ([774bb78](https://github.com/aignostics/python-sdk/commit/774bb78796b4633b55822f86d1fdb01063fc4a57))
- *(platform)* Bump heta deadline from 3 to 5 hours - ([cfecccc](https://github.com/aignostics/python-sdk/commit/cfeccccb001ac406aed99a3dedeea3d5cc941aa1))
- *(platform)* Reenable testing test-app as scheduled test - ([313d767](https://github.com/aignostics/python-sdk/commit/313d7671ff30e0e295a7a6620e2533d8fe91ef0d))
- *(platform)* Reduce heta deadline to 2h, timeout to 3h. timeout should never happen, if cancel on deadline exceeded works as expected - ([313d767](https://github.com/aignostics/python-sdk/commit/313d7671ff30e0e295a7a6620e2533d8fe91ef0d))
- *(sentry)* Fix typo in sentry config - ([ee3309c](https://github.com/aignostics/python-sdk/commit/ee3309c5b2526136bbc2cad37d771426127c6150))
- *(staging)* Back to sl.1 again, sl.2 fails always - ([cd64a86](https://github.com/aignostics/python-sdk/commit/cd64a868925077bfc21cfef688cac4bed5e2eb92))
- Test(shared: make skipping test_application_version_use_latest_fallback configurable per environment - ([f998734](https://github.com/aignostics/python-sdk/commit/f998734aaade32fbe72b9cd15cff8e3092e5c9e2))

### ⚙️ Miscellaneous Tasks

- *(ai)* Start with mcp setup - ([cd64a86](https://github.com/aignostics/python-sdk/commit/cd64a868925077bfc21cfef688cac4bed5e2eb92))
- *(deps)* Some - ([1e4c94f](https://github.com/aignostics/python-sdk/commit/1e4c94f8fd6fc2f485b13681467719be0f91fd86))
- Bump he-tme to a version that utilises a 1hr timeout ([#262](https://github.com/aignostics/python-sdk/pull/262)) - ([e0e5586](https://github.com/aignostics/python-sdk/commit/e0e5586636c11084cae2db7a5b2e9ffb6b6c374f))


# [v0.2.201](https://github.com/aignostics/python-sdk/compare/v0.2.200..v0.2.201) - 2025-11-14

### ⚙️ Miscellaneous Tasks

- *(utils)* Disable default of redirecting std logging of other modules into loguru from on to off - ([71aa5d3](https://github.com/aignostics/python-sdk/commit/71aa5d330274e5447a0f3d446e72e11624676852))


# [v0.2.200](https://github.com/aignostics/python-sdk/compare/v0.2.199..v0.2.200) - 2025-11-13

### 🚜 Refactor

- *(utils)* Introduce library mode inc. auto-detection - ([510e7d8](https://github.com/aignostics/python-sdk/commit/510e7d8581e9160cfe6547decf4107c96359ac96))
- *(utils)* Don't initialize sentry, logfire, ssl trust store or certifi in library mode - ([510e7d8](https://github.com/aignostics/python-sdk/commit/510e7d8581e9160cfe6547decf4107c96359ac96))
- *(utils)* Lower log level of boot message - ([510e7d8](https://github.com/aignostics/python-sdk/commit/510e7d8581e9160cfe6547decf4107c96359ac96))
- *(utils)* Introduce loguru - ([510e7d8](https://github.com/aignostics/python-sdk/commit/510e7d8581e9160cfe6547decf4107c96359ac96))
- *(utils)* Remove logfire - ([510e7d8](https://github.com/aignostics/python-sdk/commit/510e7d8581e9160cfe6547decf4107c96359ac96))

### 📚 Documentation

- *(requirements)* Move requirement type comment to separate line - ([949ccf1](https://github.com/aignostics/python-sdk/commit/949ccf12fb2268509585be33218b57dd5fe19212))
- *(requirements)* Add missing itemTitle to system health and settings requirements - ([386c2bf](https://github.com/aignostics/python-sdk/commit/386c2bfa60c5fc0f71362a2db415d958797865a5))
- *(requirements)* Create missing system stakeholder requirements an… - ([f2a8628](https://github.com/aignostics/python-sdk/commit/f2a862893a3096ec66a88d35ad5e788da0ad2792))
- *(requirements)* Create missing system stakeholder requirements and establish traceability - ([84f28d8](https://github.com/aignostics/python-sdk/commit/84f28d89b93ce551b481c210f1c674132dd47684))
- *(specifications)* Update specifications to improve traceability - ([178b9cc](https://github.com/aignostics/python-sdk/commit/178b9cc646d8ed4f7d6d116053940569e9cf6018))
- Fix requirements documentation traceability - ([9e3fa3a](https://github.com/aignostics/python-sdk/commit/9e3fa3aff82f5b5f69ef8fafc0762ae96c196fd3))
- Annotate requirement type in requirement files with the actual mapped value - ([243323b](https://github.com/aignostics/python-sdk/commit/243323bf093cb934bcfbd43e0522e9bb76ad186c))
- Add missing "Requirement Type" to some requirements - ([9e04703](https://github.com/aignostics/python-sdk/commit/9e047039dc34043dd7ea81856d5e92326c9c2707))

### 🧪 Testing

- *(application)* Reenable part of test_cli_run_submit_and_describe_and_cancel_and_download_and_delete that finds runs by tags, notes and combinations - ([88cba59](https://github.com/aignostics/python-sdk/commit/88cba599488498c5fec42f859f79370cbe4b408d))
- *(utils)* Add missing unit test marker - ([510e7d8](https://github.com/aignostics/python-sdk/commit/510e7d8581e9160cfe6547decf4107c96359ac96))
- Reactivate test_cli_run_dump_and_update_item_custom_metadata - ([e11b2a6](https://github.com/aignostics/python-sdk/commit/e11b2a653454aa56435fe25ba0b42e5b983ff155))

### ⚙️ Miscellaneous Tasks

- *(deps)* Bump - ([510e7d8](https://github.com/aignostics/python-sdk/commit/510e7d8581e9160cfe6547decf4107c96359ac96))
- *(gha)* Target staging with CI/CD workflow - ([f59390f](https://github.com/aignostics/python-sdk/commit/f59390f5d0668d9d9261e813452e580d89d9a747))
- *(release)* Adapt to heta expected results - ([51ee52d](https://github.com/aignostics/python-sdk/commit/51ee52d5a3ac45c5ebe5f3f098d646a9e8d1b746))
- *(release)* Start to adapt expected output for heta update - ([510e7d8](https://github.com/aignostics/python-sdk/commit/510e7d8581e9160cfe6547decf4107c96359ac96))
- Constants dep on version of app, which depends on environment - ([3af645f](https://github.com/aignostics/python-sdk/commit/3af645ff288720c862d0b19bf7a7c9124a51defa))
- Update to the softlaunch patch release 4 - ([3eddfe4](https://github.com/aignostics/python-sdk/commit/3eddfe49ec8e1c780e90677d1ad92fbf36380648))
- Update to the softlaunch patch release - ([0577445](https://github.com/aignostics/python-sdk/commit/0577445a98d5272599785d5dd7736329682f8565))
- Chore/parameterise platform environment - ([fe80fef](https://github.com/aignostics/python-sdk/commit/fe80fef3e1359ee2840c242c5caaaa1c15d4ac51))
- Parameterize platform_environment in CI/CD workflow - ([9286acb](https://github.com/aignostics/python-sdk/commit/9286acb0c623fbd694f0e315ac66716d868536b2))
- Switch on scheduled tests again - ([e6f741f](https://github.com/aignostics/python-sdk/commit/e6f741fc94f9336b67900c3315a0d8278aa3c932))
- Deactivate scheduled tests - ([8f1cecf](https://github.com/aignostics/python-sdk/commit/8f1cecfea13b836c1cb4a7e8206e1718a1c330df))

### 🛡️ Security

- *(specifications)* Update specifications to improve traceability - ([a3b6d39](https://github.com/aignostics/python-sdk/commit/a3b6d39bced19dab67d3f34face5f3b04ab9eb84))



* @olivermeyer made their first contribution in [#248](https://github.com/aignostics/python-sdk/pull/248)
* @santi698 made their first contribution in [#245](https://github.com/aignostics/python-sdk/pull/245)

# [v0.2.199](https://github.com/aignostics/python-sdk/compare/v0.2.198..v0.2.199) - 2025-11-02

### ⚙️ Miscellaneous Tasks

- *(GHA)* Limit workflow concurrency - ([f6032f5](https://github.com/aignostics/python-sdk/commit/f6032f522cb2a02412c34be252e1b2676e4aaa10))


# [v0.2.198](https://github.com/aignostics/python-sdk/compare/v0.2.196..v0.2.198) - 2025-11-02

### ⛰️  Features

- *(ketryx)* Integrate Ketryx compliance framework with requirements traceability - ([00333a9](https://github.com/aignostics/python-sdk/commit/00333a9e2d397c725f45b3eb9fa177cefcbb8530))

### 🐛 Bug Fixes

- *(application)* Superfluous character rendered - ([5fdfd1a](https://github.com/aignostics/python-sdk/commit/5fdfd1a29471b1ffcd1c74a77d00ff22e90e59e0))
- Add missing expires_seconds argument to _get_three_spots_payload_for_test ([#213](https://github.com/aignostics/python-sdk/pull/213)) - ([78b4b63](https://github.com/aignostics/python-sdk/commit/78b4b635a35f162109b9625023204c76a7c7a6ec))
- Claude[bot] <41898282+claude[bot]@users.noreply.github.com> - ([78b4b63](https://github.com/aignostics/python-sdk/commit/78b4b635a35f162109b9625023204c76a7c7a6ec))
- Helmut Hoffer von Ankershoffen né Oertel <helmut-hoffer-von-ankershoffen@users.noreply.github.com> - ([78b4b63](https://github.com/aignostics/python-sdk/commit/78b4b635a35f162109b9625023204c76a7c7a6ec))

### 🚜 Refactor

- *(Docker)* Use exact version of Python we test with - ([148ad5e](https://github.com/aignostics/python-sdk/commit/148ad5e8be2077f074219276a38728ee116507a2))
- *(ox)* Be more defensive - ([a7fde72](https://github.com/aignostics/python-sdk/commit/a7fde72fe287c2858f91cfc0da6bbaeae356a2f6))
- Cleanup - ([148ad5e](https://github.com/aignostics/python-sdk/commit/148ad5e8be2077f074219276a38728ee116507a2))

### 🎨 Styling

- Fix linting issue introduced - ([b88bccd](https://github.com/aignostics/python-sdk/commit/b88bccd83620d762b184a17300da36622f722931))

### 🧪 Testing

- *(application)* Deactivate part of test_cli_run_submit_and_describe_and_cancel_and_download_and_delete as this causes internal server errors for some runs - ([869103e](https://github.com/aignostics/python-sdk/commit/869103ef06c35484145588419cda5ccdf5136c64))
- *(platform)* Unit test covering checksum generation with files > 8MB - ([c059be3](https://github.com/aignostics/python-sdk/commit/c059be324d1185e028f50e79638d5d788d9939b8))
- *(platform)* Bump wait and download timeout for test_platform_heta_app_submit_and_wait from 3h to 5h - ([0daf3eb](https://github.com/aignostics/python-sdk/commit/0daf3eba3e4e2ef62cfe274e9717d8a5881eecd8))
- *(platform)* Fix regression in e2e test - ([14ea9cc](https://github.com/aignostics/python-sdk/commit/14ea9cc3c60a2d8d722c2d1727c3c52570dbd50d))

### ⚙️ Miscellaneous Tasks

- *(Docker)* Fix - ([be0b2bd](https://github.com/aignostics/python-sdk/commit/be0b2bdb2e8e7cf86fce315b343cee60d0e4e12f))
- *(deps)* Update anthropics/claude-code-action action to v1.0.15 ([#219](https://github.com/aignostics/python-sdk/pull/219)) - ([dfacc37](https://github.com/aignostics/python-sdk/commit/dfacc37e8f92f7bf438ecfacac33a683024f722b))
- *(install)* Provide tool for sensitive data removal so we are prepared - ([745fd65](https://github.com/aignostics/python-sdk/commit/745fd6581b64939b5f1646acaf0d1d553b74f389))
- *(ketryx)* Remove duplicated spec files - ([98736de](https://github.com/aignostics/python-sdk/commit/98736de28d1cacfd217c407b2304ca257d62b2b7))
- *(ketryx)* Remove duplicated spec files skip:ci - ([4f0aa56](https://github.com/aignostics/python-sdk/commit/4f0aa5607e61b15257d982e38a68707bd7bfbd3b))
- *(ketryx)* Remove duplicated spec files skip:test:long_running - ([00b8333](https://github.com/aignostics/python-sdk/commit/00b83332ff4079e21b9da60728cd2c23961634a2))
- *(system)* Don't log token as info - ([bd03867](https://github.com/aignostics/python-sdk/commit/bd03867458c23221c94dd97bcbfced1362afa5a2))
- *(test,ketryx)* Link missing tests with test cases and add missing test for gui health footer - ([80a812e](https://github.com/aignostics/python-sdk/commit/80a812ef9e1300834e0f0a5f349b203f177a9043))
- Update - ([c67cf40](https://github.com/aignostics/python-sdk/commit/c67cf40d8c26653a0efa2b98e9a77c344f92046b))
- Bump the staging version of he-tme - ([bbba664](https://github.com/aignostics/python-sdk/commit/bbba6643a3c7a864b503995853b881a3f0800ef6))

### 🛡️ Security

- *(dep)* Starlette - ([be0b2bd](https://github.com/aignostics/python-sdk/commit/be0b2bdb2e8e7cf86fce315b343cee60d0e4e12f))
- *(platform)* Make intentionality in loop explicit given feedback from security scanner ox - ([f506815](https://github.com/aignostics/python-sdk/commit/f5068158a7c1a1a42f652ed7043ab2d1b17c25fd))


# [v0.2.196](https://github.com/aignostics/python-sdk/compare/v0.2.195..v0.2.196) - 2025-10-26

### ⛰️  Features

- *(application)* Custom run and item metadata can be dumped as JSON via the CLI - ([6ea313b](https://github.com/aignostics/python-sdk/commit/6ea313bf6d86d55b1f9844c60c94fe55e302bc2d))
- *(application)* Custom run metadata can be updated via the CLI - ([6ea313b](https://github.com/aignostics/python-sdk/commit/6ea313bf6d86d55b1f9844c60c94fe55e302bc2d))
- *(application)* Custom run metadata can be edited via the GUI (admins only) - ([6ea313b](https://github.com/aignostics/python-sdk/commit/6ea313bf6d86d55b1f9844c60c94fe55e302bc2d))
- *(application)* Allow to submit tags via CLI and find back runs via tags - ([6ea313b](https://github.com/aignostics/python-sdk/commit/6ea313bf6d86d55b1f9844c60c94fe55e302bc2d))
- *(application)* Support download of results for input items where external_ids points to GCP bucket or webserver. - ([27e7f9a](https://github.com/aignostics/python-sdk/commit/27e7f9a5c7fb59d3fc27441e5838b508d9a58e2a))
- *(application)* Scrollable runs in sidebar with auto-refresh and notifier on run terminated - ([27e7f9a](https://github.com/aignostics/python-sdk/commit/27e7f9a5c7fb59d3fc27441e5838b508d9a58e2a))
- *(application)* Generate, show and validate custom metadata for input items - ([929bb92](https://github.com/aignostics/python-sdk/commit/929bb9292d477f80a58b3f04514173185f40d43c))
- *(application)* Support for test-app in GUI - ([929bb92](https://github.com/aignostics/python-sdk/commit/929bb9292d477f80a58b3f04514173185f40d43c))
- *(application)* Show error code on failed items - ([929bb92](https://github.com/aignostics/python-sdk/commit/929bb9292d477f80a58b3f04514173185f40d43c))
- *(application)* Show more more details in CLI commands applicaton run list and application run describe - ([929bb92](https://github.com/aignostics/python-sdk/commit/929bb9292d477f80a58b3f04514173185f40d43c))
- *(ketryx)* Integrate Ketryx CI/CD workflow and reporting - ([eb3b0c2](https://github.com/aignostics/python-sdk/commit/eb3b0c2fa57815f2c7eb756540609343d910a863))
- *(platform)* Support for tags in custom sdk metadata, run and item-level - ([6ea313b](https://github.com/aignostics/python-sdk/commit/6ea313bf6d86d55b1f9844c60c94fe55e302bc2d))
- *(platform)* Support created_at and updated_at in custom sdk metadata, run and item-level - ([6ea313b](https://github.com/aignostics/python-sdk/commit/6ea313bf6d86d55b1f9844c60c94fe55e302bc2d))
- *(platform)* Support nocache=True on cached operations - ([6ea313b](https://github.com/aignostics/python-sdk/commit/6ea313bf6d86d55b1f9844c60c94fe55e302bc2d))
- *(platform)* Custom run and item metadata can be updated - ([6ea313b](https://github.com/aignostics/python-sdk/commit/6ea313bf6d86d55b1f9844c60c94fe55e302bc2d))
- Test:long-running] - ([eb3b0c2](https://github.com/aignostics/python-sdk/commit/eb3b0c2fa57815f2c7eb756540609343d910a863))

### 🐛 Bug Fixes

- *(ci-cd)* Yml file conflicts - ([9969508](https://github.com/aignostics/python-sdk/commit/9969508c895a40fd530c4f958b9d79f75c819e7f))
- *(tests)* Resolve linter issues and update source code - ([dcd2269](https://github.com/aignostics/python-sdk/commit/dcd226949b01b77b7bada617d05ced2353fc96b6))
- Test:long-running] - ([dcd2269](https://github.com/aignostics/python-sdk/commit/dcd226949b01b77b7bada617d05ced2353fc96b6))

### 🚜 Refactor

- *(application)* Improve dryness - ([929bb92](https://github.com/aignostics/python-sdk/commit/929bb9292d477f80a58b3f04514173185f40d43c))
- *(dataset)* Move business logic to from CLI to service. ([#204](https://github.com/aignostics/python-sdk/pull/204)) - ([27e7f9a](https://github.com/aignostics/python-sdk/commit/27e7f9a5c7fb59d3fc27441e5838b508d9a58e2a))
- *(dataset)* Move business logic to from CLI to service. - ([27e7f9a](https://github.com/aignostics/python-sdk/commit/27e7f9a5c7fb59d3fc27441e5838b508d9a58e2a))

### 📚 Documentation

- *(AI)* Update - ([6ea313b](https://github.com/aignostics/python-sdk/commit/6ea313bf6d86d55b1f9844c60c94fe55e302bc2d))
- *(application)* Auto-generate json schema from pydantic models for sdk specific custom metadata of input items - ([929bb92](https://github.com/aignostics/python-sdk/commit/929bb9292d477f80a58b3f04514173185f40d43c))
- *(ketryx)* Fix SPEC_SYSTEM_SERVICE.md & SPEC-BUILD-CHAIN-CICD-SERVICE.md itemFulfills section - ([94d15df](https://github.com/aignostics/python-sdk/commit/94d15df23da8875adf107287d2653916dfef0523))
- *(req)* Add stakeholder and software requirements (SHRs and SWRs) - ([0270ec2](https://github.com/aignostics/python-sdk/commit/0270ec255743c43eeb85c84878a239454eec1ee7))
- *(spec)* Add software item specifications for all modules - ([0570429](https://github.com/aignostics/python-sdk/commit/0570429f7089745cce06e738958926bb5238ed69))
- Ci] - ([0570429](https://github.com/aignostics/python-sdk/commit/0570429f7089745cce06e738958926bb5238ed69))

### 🧪 Testing

- *(application)* Re-classified test_cli_run_describe_invalid_uuid as e2e - ([3224e77](https://github.com/aignostics/python-sdk/commit/3224e779fce6ce4bbdb8ff3dc538547e56cd6af1))
- *(application)* Fix race condition in test - ([548b2b7](https://github.com/aignostics/python-sdk/commit/548b2b72472fcba6497a2523b03d5a56e850adff))
- *(ketryx)* Link verification tests with specifications - ([5f47090](https://github.com/aignostics/python-sdk/commit/5f470904ace5c3320014f0e7a3cd0941c57898c0))
- *(ketryx)* Add Gherkin test cases for requirements traceability - ([3261909](https://github.com/aignostics/python-sdk/commit/32619096877b911c4602291d871bfc8e7f5862df))
- Test:long-running, skip:test:matrix-runner] - ([5f47090](https://github.com/aignostics/python-sdk/commit/5f470904ace5c3320014f0e7a3cd0941c57898c0))
- Ci] - ([3261909](https://github.com/aignostics/python-sdk/commit/32619096877b911c4602291d871bfc8e7f5862df))

### ⚙️ Miscellaneous Tasks

- *(ai)* Improve vscode/agent guidance - ([e2e04b8](https://github.com/aignostics/python-sdk/commit/e2e04b8aaba18335f5692f3050a0e321380da15c))
- *(deps)* Bump - ([6ea313b](https://github.com/aignostics/python-sdk/commit/6ea313bf6d86d55b1f9844c60c94fe55e302bc2d))
- *(platform)* Fix race condition in e2e test due to caching ([#206](https://github.com/aignostics/python-sdk/pull/206)) - ([6ea313b](https://github.com/aignostics/python-sdk/commit/6ea313bf6d86d55b1f9844c60c94fe55e302bc2d))
- *(platform)* Improved depth of tests - ([6ea313b](https://github.com/aignostics/python-sdk/commit/6ea313bf6d86d55b1f9844c60c94fe55e302bc2d))
- *(platform)* Fix race condition in e2e test due to caching by using nocache - ([6ea313b](https://github.com/aignostics/python-sdk/commit/6ea313bf6d86d55b1f9844c60c94fe55e302bc2d))
- *(platform)* Start with submit-and-find e2e tests later replacing submit-and-wait - ([6ea313b](https://github.com/aignostics/python-sdk/commit/6ea313bf6d86d55b1f9844c60c94fe55e302bc2d))
- *(platform)* Fix test - ([a1f909f](https://github.com/aignostics/python-sdk/commit/a1f909f3fe22cadf0dc84172d82bd304bffac476))
- *(qupath)* Enable complex automated test scenario covering creating QuPath projects - ([6ea313b](https://github.com/aignostics/python-sdk/commit/6ea313bf6d86d55b1f9844c60c94fe55e302bc2d))
- *(qupath)* Reenable E2E Test Scenario (Download -> Create Project -> Inspect) - ([e2e04b8](https://github.com/aignostics/python-sdk/commit/e2e04b8aaba18335f5692f3050a0e321380da15c))
- *(tests)* Strip ansi codes by default when normalizing output, reducing flakiness of tests in rare scenarios - ([929bb92](https://github.com/aignostics/python-sdk/commit/929bb9292d477f80a58b3f04514173185f40d43c))
- *(tests)* Significantly improve daily scheduled test now called flow tests, including beating heart on - ([929bb92](https://github.com/aignostics/python-sdk/commit/929bb9292d477f80a58b3f04514173185f40d43c))
- *(tests)* PLATFORM_ENVIRONMENT dependent app versions in tests - ([e2e04b8](https://github.com/aignostics/python-sdk/commit/e2e04b8aaba18335f5692f3050a0e321380da15c))
- Chore(deps); bump - ([e2e04b8](https://github.com/aignostics/python-sdk/commit/e2e04b8aaba18335f5692f3050a0e321380da15c))

### Task

- *(req)* Links missing gui Module Specification with tests [skip:ci] - ([9650271](https://github.com/aignostics/python-sdk/commit/9650271b47ec160d036d8f1378b3109f2e0c647a))
- *(req)* Links missing wsi Module Specification with tests [skip:ci] - ([236781b](https://github.com/aignostics/python-sdk/commit/236781bbd28cd7b96add87bf60067096cb71d038))
- *(req)* Links missing system Module Specification with tests [skip:ci] - ([1fcc7de](https://github.com/aignostics/python-sdk/commit/1fcc7dec3991a7606b6e4b6adc0021af0982379c))



* @muhabalwan-aginx made their first contribution
* @na66im made their first contribution

# [v0.2.195](https://github.com/aignostics/python-sdk/compare/v0.2.194..v0.2.195) - 2025-10-23

### ⛰️  Features

- *(QuPath)* Support updating QuPath - ([29b1263](https://github.com/aignostics/python-sdk/commit/29b126320568400e315397cda626ca1a8b50978f))
- *(QuPath)* Use 0.6.0-rc5 - ([29b1263](https://github.com/aignostics/python-sdk/commit/29b126320568400e315397cda626ca1a8b50978f))
- *(QuPath)* Deeper info - ([29b1263](https://github.com/aignostics/python-sdk/commit/29b126320568400e315397cda626ca1a8b50978f))
- *(QuPath)* Create project from results - ([17425dd](https://github.com/aignostics/python-sdk/commit/17425dd06354de11da507fa4b13714e97218781c))
- *(System)* Enable to enable/disable diagnostics in UI - ([b27296a](https://github.com/aignostics/python-sdk/commit/b27296a035a1cbbc0e61158c32672416b90accc7))
- *(System)* Manipulate dotenv via CLI, including enable/disabling http proxy, enabling/disabling remote diagnostics - ([17425dd](https://github.com/aignostics/python-sdk/commit/17425dd06354de11da507fa4b13714e97218781c))
- *(application)* Custom metadata with run and scheduling information in custom metadata - ([6c0753f](https://github.com/aignostics/python-sdk/commit/6c0753f31f5aca120c460414193aaa409a6576fa))
- *(application)* Allow to copy error message - ([ec0ed63](https://github.com/aignostics/python-sdk/commit/ec0ed6332e7c32357d9a25a749e02604b1312fe5))
- *(application)* Show duration, terminated at, run and item-level message ([#143](https://github.com/aignostics/python-sdk/pull/143)) - ([0dc484e](https://github.com/aignostics/python-sdk/commit/0dc484e9e97c674b4468638afd82513e81f2ee4d))
- *(application)* Allow to set note on run submission, and retrieve on run describe - ([c5175cb](https://github.com/aignostics/python-sdk/commit/c5175cbf32cfcb5682bb5c80206534879c3a7754))
- *(application)* Allow live search of runs by note - ([c5175cb](https://github.com/aignostics/python-sdk/commit/c5175cbf32cfcb5682bb5c80206534879c3a7754))
- *(application)* Allow to flag to onboard to Aignostics Portal - ([c5175cb](https://github.com/aignostics/python-sdk/commit/c5175cbf32cfcb5682bb5c80206534879c3a7754))
- *(application)* Show run id in collapsible so it can be copied - ([d7c597a](https://github.com/aignostics/python-sdk/commit/d7c597a70a398c951a8c17b96e33952a821c82ba))
- *(application)* Dump zip with application schemata - ([af33133](https://github.com/aignostics/python-sdk/commit/af33133cc50a0b3a2f1c36f53b3d338d96f96b78))
- *(application, platform)* Allow to delete run. Note: currently broken in Samia - ([38c6554](https://github.com/aignostics/python-sdk/commit/38c6554add3fbfe17093a2ae007914996e064c8a))
- *(bucket)* Allow to select destination in bucket download gui - ([0ecd4c3](https://github.com/aignostics/python-sdk/commit/0ecd4c325c45279941055683c593740ceb5d87a8))
- *(bucket)* Proper download including support for patterns, keys, gui, cli - ([ef04b98](https://github.com/aignostics/python-sdk/commit/ef04b981c077b75bdd4188ce6f896dafd8849a88))
- *(bucket)* Purge - ([ef04b98](https://github.com/aignostics/python-sdk/commit/ef04b981c077b75bdd4188ce6f896dafd8849a88))
- *(bucket)* Make expiration time of upload/download properly configurable, and include in info - ([6191781](https://github.com/aignostics/python-sdk/commit/61917818cdefaf5de9cb3e22cd939141ee75cfa1))
- *(codegen, platform)* Support me endpoint ([#81](https://github.com/aignostics/python-sdk/pull/81)) - ([7d74a2b](https://github.com/aignostics/python-sdk/commit/7d74a2b334512bd69df5aed460ee160263f10cda))
- *(core)* Support Windows on ARM - ([89a3c4a](https://github.com/aignostics/python-sdk/commit/89a3c4a4c761fbac036e3c8e400fa8b271fe437d))
- *(gui)* Migrate to nicegui 3 - ([d304ef7](https://github.com/aignostics/python-sdk/commit/d304ef721e3c895cc4eb453a55fe69aee6a0c266))
- *(gui)* Custom error page showing traceback and allowing to close app even in non-chrome mode - ([ee47197](https://github.com/aignostics/python-sdk/commit/ee47197ad8cf27f6789df743e9f553a8c2179605))
- *(marimo)* Marimo open with downloaded results - ([7cab5a1](https://github.com/aignostics/python-sdk/commit/7cab5a105c7707ba4e90ce4f0ef3c49a7c1db8b8))
- *(marimo)* Open marimo from extension page - ([7cab5a1](https://github.com/aignostics/python-sdk/commit/7cab5a105c7707ba4e90ce4f0ef3c49a7c1db8b8))
- *(native)* Show progress on splash screen ([#91](https://github.com/aignostics/python-sdk/pull/91)) - ([e667252](https://github.com/aignostics/python-sdk/commit/e6672526210d0e397267af1059482a8ed434065b))
- *(native)* Splash screen for Windows and Linux ([#90](https://github.com/aignostics/python-sdk/pull/90)) - ([8fc82cd](https://github.com/aignostics/python-sdk/commit/8fc82cded615d9d18da799a92e525ecd6c81c42f))
- *(native)* Show being native in footer of launchpad - ([9b0a4d5](https://github.com/aignostics/python-sdk/commit/9b0a4d58ad1be62d727efb2765b3205f90121bf8))
- *(native)* Debug command - ([433a803](https://github.com/aignostics/python-sdk/commit/433a803310915e355d4b3c4fe1ffd04f5509c278))
- *(native)* Spike for native (compiled) apps - ([e03512c](https://github.com/aignostics/python-sdk/commit/e03512c9be6ace3cedebd3981bf12c39f586486d))
- *(networking)* Support system truststore for ssl trust chain [no:ci] ([#92](https://github.com/aignostics/python-sdk/pull/92)) - ([aad4e76](https://github.com/aignostics/python-sdk/commit/aad4e76e83d489275b3d09e8e887d79a1af2d514))
- *(notebook)* Extension page - ([17425dd](https://github.com/aignostics/python-sdk/commit/17425dd06354de11da507fa4b13714e97218781c))
- *(platform)* Retries and caching for read-only and auth operations - ([6c0753f](https://github.com/aignostics/python-sdk/commit/6c0753f31f5aca120c460414193aaa409a6576fa))
- *(platform)* Dynamic user agent for all operations - ([6c0753f](https://github.com/aignostics/python-sdk/commit/6c0753f31f5aca120c460414193aaa409a6576fa))
- *(platform)* Auto-retry when retrieving JWKS set from auth0 - ([6ecb912](https://github.com/aignostics/python-sdk/commit/6ecb91241547c4f3ed800a04a7eafdfc59d79697))
- *(platform)* Cache JWKS set, TTL 24h, minimizing calls to auth0 on validating access tokens - ([6ecb912](https://github.com/aignostics/python-sdk/commit/6ecb91241547c4f3ed800a04a7eafdfc59d79697))
- *(platform)* Auto-retry when calling auth0 to exchange refresh token for access token - ([6ecb912](https://github.com/aignostics/python-sdk/commit/6ecb91241547c4f3ed800a04a7eafdfc59d79697))
- *(platform)* Configurable timeout for requesting platform health - ([6ecb912](https://github.com/aignostics/python-sdk/commit/6ecb91241547c4f3ed800a04a7eafdfc59d79697))
- *(platform)* Introduce authentication aware operation cache - ([6ecb912](https://github.com/aignostics/python-sdk/commit/6ecb91241547c4f3ed800a04a7eafdfc59d79697))
- *(platform)* Use authentication aware operation cache to cache /me result - ([6ecb912](https://github.com/aignostics/python-sdk/commit/6ecb91241547c4f3ed800a04a7eafdfc59d79697))
- *(platform)* Adapt to breaking changes in Platform API 1.0.0-beta6 - ([c5175cb](https://github.com/aignostics/python-sdk/commit/c5175cbf32cfcb5682bb5c80206534879c3a7754))
- *(platform,application)* Support custom metadata attached to runs - ([c5175cb](https://github.com/aignostics/python-sdk/commit/c5175cbf32cfcb5682bb5c80206534879c3a7754))
- *(platform,gui)* Org name - ([51c65a2](https://github.com/aignostics/python-sdk/commit/51c65a26bc3957ef02ffc7d7f201494ec0e0ce8b))
- *(platform,gui,diagnostics)* Whoami - ([0bad5f2](https://github.com/aignostics/python-sdk/commit/0bad5f24766f3c05fc09b47a5c4f20b79b82588b))
- *(run_describe)* Show thumbnail per item - ([da5afa3](https://github.com/aignostics/python-sdk/commit/da5afa3f6fef3062c234e0c8d0187ae10ee54272))
- *(system)* Allow to unmask secrets - ([e03512c](https://github.com/aignostics/python-sdk/commit/e03512c9be6ace3cedebd3981bf12c39f586486d))
- *(userinfo)* Allow to edit profile - ([788f209](https://github.com/aignostics/python-sdk/commit/788f20901fe8b7156e3058ca95cbb9849da2940c))
- *(utils)* Generate dynamic user agent including version, build number, os, and test calling - ([c5175cb](https://github.com/aignostics/python-sdk/commit/c5175cbf32cfcb5682bb5c80206534879c3a7754))
- API v1.0.0-beta.6 ([#141](https://github.com/aignostics/python-sdk/pull/141)) - ([c5175cb](https://github.com/aignostics/python-sdk/commit/c5175cbf32cfcb5682bb5c80206534879c3a7754))
- Use dynamic user agent in http requests and run submissions via custom metadata - ([c5175cb](https://github.com/aignostics/python-sdk/commit/c5175cbf32cfcb5682bb5c80206534879c3a7754))
- Allow to boot with zero config, i.e. no .env file required in default case - ([7d74a2b](https://github.com/aignostics/python-sdk/commit/7d74a2b334512bd69df5aed460ee160263f10cda))
- QuPath enabled by default - ([a52d2fb](https://github.com/aignostics/python-sdk/commit/a52d2fbafed571a5ef5b850800c742bddf79ff4e))
- Download Results - ([da5afa3](https://github.com/aignostics/python-sdk/commit/da5afa3f6fef3062c234e0c8d0187ae10ee54272))
- Aignostics Launchpad, Aignostics CLI, Aignostics Client - ([2f97fb9](https://github.com/aignostics/python-sdk/commit/2f97fb92c41f533c1e1c6f1ccd5beed4777c5463))

### 🐛 Bug Fixes

- *(Windows)* Sanitize paths so they don't contain a colon if not drive letter - ([165cc59](https://github.com/aignostics/python-sdk/commit/165cc591ad299e766dd453efc3896ea8f6b466df))
- *(ai)* Claude workflows - ([0a96143](https://github.com/aignostics/python-sdk/commit/0a961439b990101607d65b29b70d12099d4c3827))
- *(application)* Error handling if application_versions called with … ([#178](https://github.com/aignostics/python-sdk/pull/178)) - ([6dbe129](https://github.com/aignostics/python-sdk/commit/6dbe129230e80e5b1bbd4388256ae3be1d7e2a96))
- *(application)* Error handling if application_versions called with str arg - ([6dbe129](https://github.com/aignostics/python-sdk/commit/6dbe129230e80e5b1bbd4388256ae3be1d7e2a96))
- *(application)* Properly render error if run details cannot be loaded - ([1e01928](https://github.com/aignostics/python-sdk/commit/1e019283cc5ec8ac68adb853d8069e34e6eb29e2))
- *(application)* Don't show extra column in meta edit - ([c5175cb](https://github.com/aignostics/python-sdk/commit/c5175cbf32cfcb5682bb5c80206534879c3a7754))
- *(application)* Allow next post excluding slides if remaining slides with valid metadata - ([7254298](https://github.com/aignostics/python-sdk/commit/7254298e1d5b58b3e4c456ef3971db7e7e196ca7))
- *(bucket)* In GUI use static version of download operation offered by service - ([db2b5f5](https://github.com/aignostics/python-sdk/commit/db2b5f514f66c6a0dc411bf6dda721c2a668d364))
- *(bucket)* Use longer 7d expiration time for signed upload urls instead of 1h - ([6191781](https://github.com/aignostics/python-sdk/commit/61917818cdefaf5de9cb3e22cd939141ee75cfa1))
- *(cli)* List runs count - ([98f9b6d](https://github.com/aignostics/python-sdk/commit/98f9b6d5e89d7f7aa1ca5f0631adfc952e9971fe))
- *(codegen)* Don't rely on redirects from /v1 to /api/v1 - ([7d74a2b](https://github.com/aignostics/python-sdk/commit/7d74a2b334512bd69df5aed460ee160263f10cda))
- *(dataset)* Custom download folder selection - ([4b59607](https://github.com/aignostics/python-sdk/commit/4b5960743849bc3873fd6a5f185463f5e76a7e13))
- *(dataset)* Missing dependency, while still smaller then pyarrow - ([ff1f178](https://github.com/aignostics/python-sdk/commit/ff1f178df3bdde970a67c8f2c1d86eac9126195b))
- *(dep)* Incompatibility in 3rd party dependency showinfm lead to syntax error in modern Python - now vendored and fixed. - ([d304ef7](https://github.com/aignostics/python-sdk/commit/d304ef721e3c895cc4eb453a55fe69aee6a0c266))
- *(deps)* Update dependency pywin32 to v311 ([#170](https://github.com/aignostics/python-sdk/pull/170)) - ([17ee850](https://github.com/aignostics/python-sdk/commit/17ee850b3f073a792cbe60c80488370e69979bed))
- *(native)* Windows - ([28b1010](https://github.com/aignostics/python-sdk/commit/28b10104b02488b588224fcb52653f953c882d22))
- *(native)* Marimo integration - ([9f01ef6](https://github.com/aignostics/python-sdk/commit/9f01ef644f5e2302b54306ecb1ebf14a062d60ad))
- *(native)* Marimo - ([5911d74](https://github.com/aignostics/python-sdk/commit/5911d74c279dd215c2ce51f8b0b6c294fa5d2831))
- *(native)* Use certifi bundle if default bundle not found - ([f10e249](https://github.com/aignostics/python-sdk/commit/f10e249848b968dee04317dfe5a5700f0768cd15))
- *(native)* Use system trust store for SSL certificates - ([168a7d7](https://github.com/aignostics/python-sdk/commit/168a7d7509053855f7f8537f6a82ba52c943e11b))
- *(native)* Dataset download - openslide libs were not bundled by pyinstaller - ([9ff1453](https://github.com/aignostics/python-sdk/commit/9ff1453ce17170e84634ef1ae1c8d15dd659bec0))
- *(native)* Thumbnail generation on submission - script execution complexity - ([9ff1453](https://github.com/aignostics/python-sdk/commit/9ff1453ce17170e84634ef1ae1c8d15dd659bec0))
- *(native)* Bundle openslide native libs - ([164d43e](https://github.com/aignostics/python-sdk/commit/164d43e54a0380d31672070bce4d411dd6f3e371))
- *(native)* Include s5cmd binary in native distribution - ([e35303a](https://github.com/aignostics/python-sdk/commit/e35303a995886a9e3817f7097f1a84d0b37b9a18))
- *(native)* Add_docstring issue caused by inconsistent optimization on analysis and exe building - ([066a198](https://github.com/aignostics/python-sdk/commit/066a1988179cabd3ffd1268aa746e13da0747079))
- *(notebook)* Revert timeout - ([9b7c1c3](https://github.com/aignostics/python-sdk/commit/9b7c1c3e5331ce2d627492319b8e9a5f5a65daa5))
- *(notebook)* Navigation to marimo - ([af5e84e](https://github.com/aignostics/python-sdk/commit/af5e84e2548f5e9f10cfd0d1b4814bc9764b76cd))
- *(platform)* Remove unused setting authorization_backoff_seconds - ([6ecb912](https://github.com/aignostics/python-sdk/commit/6ecb91241547c4f3ed800a04a7eafdfc59d79697))
- *(platform)* Fix wrong exception handler in _perform_device_flow - was catching exception from urllib, not requests lib - ([6ecb912](https://github.com/aignostics/python-sdk/commit/6ecb91241547c4f3ed800a04a7eafdfc59d79697))
- *(platform)* Use dynamic user agent for requesting /me - ([6ecb912](https://github.com/aignostics/python-sdk/commit/6ecb91241547c4f3ed800a04a7eafdfc59d79697))
- *(platform)* Get new token if cache entry broken - ([8bbbcf6](https://github.com/aignostics/python-sdk/commit/8bbbcf6e9197e2caf62f1d3254557e947196b502))
- *(platform)* Invalid log formatting - ([483ffe3](https://github.com/aignostics/python-sdk/commit/483ffe3c3b5c065532f44471f55ec438623f9915))
- *(platform)* Token refresh on long living api client - ([11f46f1](https://github.com/aignostics/python-sdk/commit/11f46f14b4696b4303357d497f826480198ccc05))
- *(platform)* Allow to dial into dev environment - ([7d74a2b](https://github.com/aignostics/python-sdk/commit/7d74a2b334512bd69df5aed460ee160263f10cda))
- *(platform)* Fix broken pytest collection if user does not have permission to access aignx test bucket - ([a65930c](https://github.com/aignostics/python-sdk/commit/a65930c2cde73aa57af338aa6c752cff2a1fbfeb))
- *(platform)* Allow for rapid re-auth - ([34ca8ee](https://github.com/aignostics/python-sdk/commit/34ca8ee4064ceb72619bc429ca12318b1718deab))
- *(platform)* Adapt to breaking change in API - ([7920b0b](https://github.com/aignostics/python-sdk/commit/7920b0b21e527a596c5e7c23f7a9914ac447c95f))
- *(platform)* Graceful fail on user info not accessible - ([01f536a](https://github.com/aignostics/python-sdk/commit/01f536a668f2ae8a57e8b837c23dc592212f0ae2))
- *(platform)* Refresh token repl - ([9a3adf2](https://github.com/aignostics/python-sdk/commit/9a3adf26e207d1bb4ae8ea1adea6d86216d7cc6d))
- *(platform/user)* Reload on reauth - ([4f05b84](https://github.com/aignostics/python-sdk/commit/4f05b84537f4a3f24ffb08c904750c0063c91301))
- *(ssl)* Use certifi as fallback if configured intermediate certificates not found, and no env override - ([157d2b7](https://github.com/aignostics/python-sdk/commit/157d2b717d4045e2b2fcc012dda86acaac4c30df))
- *(system)* Rendering of json editor content - had to find workaround given bug in NiceGUI3 for json_editor - ([d5535d9](https://github.com/aignostics/python-sdk/commit/d5535d9fd2ab3cdec3381c0300a6e9495771de17))
- *(system)* Disable cpu freq on gha macos latest runner given not supported - ([861af87](https://github.com/aignostics/python-sdk/commit/861af873a5f4eca40e9dac11f17192ab4355ef40))
- *(typer)* Workaround https://github.com/fastapi/typer/pull/1240 - ([207eb0c](https://github.com/aignostics/python-sdk/commit/207eb0c45ba5774e52031bb9f5fbfcc1e485d184))
- *(unmask)* Unmask secrets on request in all services - ([6a96ed3](https://github.com/aignostics/python-sdk/commit/6a96ed38371614d7ea1d5cd670e218c3d6d516d9))
- *(utils)* Surface setting validation error on misconfigured api root - ([6ecb912](https://github.com/aignostics/python-sdk/commit/6ecb91241547c4f3ed800a04a7eafdfc59d79697))
- *(wsi)* Don't fail on log on broken tiff test - ([c5175cb](https://github.com/aignostics/python-sdk/commit/c5175cbf32cfcb5682bb5c80206534879c3a7754))
- Renovate[bot] <29139614+renovate[bot]@users.noreply.github.com> - ([17ee850](https://github.com/aignostics/python-sdk/commit/17ee850b3f073a792cbe60c80488370e69979bed))
- Fix typo in log message caught by claude code review - ([c5175cb](https://github.com/aignostics/python-sdk/commit/c5175cbf32cfcb5682bb5c80206534879c3a7754))
- Update the input artifact name for HETA to whole_slide_image ([#121](https://github.com/aignostics/python-sdk/pull/121)) - ([6ed1e27](https://github.com/aignostics/python-sdk/commit/6ed1e270d1a387c887d286fcab2cd8bb200eff25))
- Fix typos in readme.md - ([ef4d8f6](https://github.com/aignostics/python-sdk/commit/ef4d8f6ea74ee8b861cd9d2cf20dd342d7b3165e))
- ⚡️ Use SemVer to check for application ids in launchpad ([#56](https://github.com/aignostics/python-sdk/pull/56)) - ([c6c874e](https://github.com/aignostics/python-sdk/commit/c6c874ee9d2861f8fccb4dc220096d745515f17e))
- Force .json for geojson - ([c48b9dc](https://github.com/aignostics/python-sdk/commit/c48b9dceb2c5e6f20980a0992fbefb7b917175e8))

### 🚜 Refactor

- *(QuPath)* Proper handling of script max execution time - ([b0d1c79](https://github.com/aignostics/python-sdk/commit/b0d1c79bc3e9bde03ba42c151545b4d5687feff6))
- *(QuPath)* 20x speed up writing polygons by switching from paquo to groovy - ([29b1263](https://github.com/aignostics/python-sdk/commit/29b126320568400e315397cda626ca1a8b50978f))
- *(System)* Move settings logic to service - ([b27296a](https://github.com/aignostics/python-sdk/commit/b27296a035a1cbbc0e61158c32672416b90accc7))
- *(application)* Load applications in left sidebar in thread to not block UI - ([c5175cb](https://github.com/aignostics/python-sdk/commit/c5175cbf32cfcb5682bb5c80206534879c3a7754))
- *(application)* Consistent exception logging and raising - ([1a702a7](https://github.com/aignostics/python-sdk/commit/1a702a7ea08dfdb9614c44391a01de54e6c73a00))
- *(application)* Introduce service tests - ([1875741](https://github.com/aignostics/python-sdk/commit/1875741fba55963bf739ff6b8907e938d5e02183))
- *(application)* Shrink images - ([a09cc7e](https://github.com/aignostics/python-sdk/commit/a09cc7e2665c9529b61dd689c47b5e805f88cdf1))
- *(application)* Don't allow to close download dialog by clicking outside - ([1deeff3](https://github.com/aignostics/python-sdk/commit/1deeff3bc1aa1ba0efa0a446e1b2e80f8bae0684))
- *(application)* Cleanup - ([17425dd](https://github.com/aignostics/python-sdk/commit/17425dd06354de11da507fa4b13714e97218781c))
- *(boot)* Reduce boot time - ([81423dd](https://github.com/aignostics/python-sdk/commit/81423dda4f201dbe729b3b4c68473adeb89d9e32))
- *(bucket)* Removed ls, refactored find - ([ef04b98](https://github.com/aignostics/python-sdk/commit/ef04b981c077b75bdd4188ce6f896dafd8849a88))
- *(dataset,wsi)* Catch exceptions in CLI commands - ([d5535d9](https://github.com/aignostics/python-sdk/commit/d5535d9fd2ab3cdec3381c0300a6e9495771de17))
- *(general)* Central place for defining supported WSI extensions - ([0b052a7](https://github.com/aignostics/python-sdk/commit/0b052a78197960627896445095a0c2af2854f5fd))
- *(gui)* Consistent use of spinners and awaiting - ([f5ca9c4](https://github.com/aignostics/python-sdk/commit/f5ca9c4709ce1739c62d4ab74966470f5cfc21d2))
- *(info)* Consistently show settings - ([0b052a7](https://github.com/aignostics/python-sdk/commit/0b052a78197960627896445095a0c2af2854f5fd))
- *(io)* Don't use synchronous fileio in async functions - ([e4a82bd](https://github.com/aignostics/python-sdk/commit/e4a82bdc1551dcfd212f483e85a1b094559d4db1))
- *(lint)* New ruff rules - ([472258c](https://github.com/aignostics/python-sdk/commit/472258ca9460d62dfb4be1a8243f74193510e62e))
- *(logging)* Revert to cwd for logfile - ([cc9e990](https://github.com/aignostics/python-sdk/commit/cc9e990b9b921ff0f23d034ae050a492552d0c4a))
- *(logging)* Use app dir as default for log file - ([dd52d9e](https://github.com/aignostics/python-sdk/commit/dd52d9eb33adc8eb9219185ad6e23a5f107af7cf))
- *(native)* Compress native installation using UPX on Windows - ([89a3c4a](https://github.com/aignostics/python-sdk/commit/89a3c4a4c761fbac036e3c8e400fa8b271fe437d))
- *(native)* Use archive; optimize - ([127a88d](https://github.com/aignostics/python-sdk/commit/127a88dd30fd480b01b5ecb47ede9f29f80f617b))
- *(native)* Don't include dev dependencies - ([9b0a4d5](https://github.com/aignostics/python-sdk/commit/9b0a4d58ad1be62d727efb2765b3205f90121bf8))
- *(native)* Significantly reduce size and bootup time - ([dd52d9e](https://github.com/aignostics/python-sdk/commit/dd52d9eb33adc8eb9219185ad6e23a5f107af7cf))
- *(notebook)* Simplify open marimo button - ([26c9d1b](https://github.com/aignostics/python-sdk/commit/26c9d1b2d8876e5de3ae31dcd663f5050daff387))
- *(performance)* Faster boot - ([207eb0c](https://github.com/aignostics/python-sdk/commit/207eb0c45ba5774e52031bb9f5fbfcc1e485d184))
- *(platform)* Use proper error messages and logging on failure (of attempts) to exchange refresh token and validate access token - ([6ecb912](https://github.com/aignostics/python-sdk/commit/6ecb91241547c4f3ed800a04a7eafdfc59d79697))
- *(platform)* Consistently use HTTPStatus consts instead of 200, 500 etc. - ([6ecb912](https://github.com/aignostics/python-sdk/commit/6ecb91241547c4f3ed800a04a7eafdfc59d79697))
- *(platform)* Use proper constraints on settings - ([6ecb912](https://github.com/aignostics/python-sdk/commit/6ecb91241547c4f3ed800a04a7eafdfc59d79697))
- *(platform)* Rename run delete to run result delete - ([861af87](https://github.com/aignostics/python-sdk/commit/861af873a5f4eca40e9dac11f17192ab4355ef40))
- *(platform)* Test timeout/expires - ([89745fc](https://github.com/aignostics/python-sdk/commit/89745fcaf54b63b81d590ff67413f8b7611faeb5))
- *(platform)* Refactor user profile - ([ff47251](https://github.com/aignostics/python-sdk/commit/ff472517e53ad114378954bade1838569e8b58df))
- *(platform,application)* Establish sdk subtree within custom metadata for contract with other sdks and apps - ([560cbb8](https://github.com/aignostics/python-sdk/commit/560cbb88203b737848a5fbde550235979b753d71))
- *(platform,system)* Optimize connection pooling - ([6ecb912](https://github.com/aignostics/python-sdk/commit/6ecb91241547c4f3ed800a04a7eafdfc59d79697))
- *(progress)* Faster progress bars - ([29b1263](https://github.com/aignostics/python-sdk/commit/29b126320568400e315397cda626ca1a8b50978f))
- *(qupath)* Don’t count system as unhealthy if QuPath application not installed - ([d5535d9](https://github.com/aignostics/python-sdk/commit/d5535d9fd2ab3cdec3381c0300a6e9495771de17))
- *(qupath)* Using groovy, not paquo; GPL removed from allow-list when license auditing - ([e03512c](https://github.com/aignostics/python-sdk/commit/e03512c9be6ace3cedebd3981bf12c39f586486d))
- *(qupath)* Using groovy, not paquo - ([f5ca9c4](https://github.com/aignostics/python-sdk/commit/f5ca9c4709ce1739c62d4ab74966470f5cfc21d2))
- *(sonarqube)* Annotate generator - ([a72c5ba](https://github.com/aignostics/python-sdk/commit/a72c5baf22f36bbe33ab768fa9d2d457114e6ab1))
- *(tests)* Refactored tests to reduce flakiness where avoidable, i.e. not solely dependent on external services - ([d5535d9](https://github.com/aignostics/python-sdk/commit/d5535d9fd2ab3cdec3381c0300a6e9495771de17))
- *(tests)* Central place for app id and version - ([5bcc685](https://github.com/aignostics/python-sdk/commit/5bcc685d2d7de98777673a4623fd1b7abfb9b3fd))
- *(tests)* Central constants for app and app version id to simplify adapting to new apps - ([3fc5730](https://github.com/aignostics/python-sdk/commit/3fc5730294588534ad6e57d2302dfa7d28dec8e0))
- *(user)* Rename from platform to user in cli - ([efa9b50](https://github.com/aignostics/python-sdk/commit/efa9b50ceca309edd75cc7f4843f9989fe53ac4e))
- *(uv)* Define required uv version in pyproject.toml, for use across GHA - ([7e1610e](https://github.com/aignostics/python-sdk/commit/7e1610e604f4f2ddb1fd6da3448f5731958565ee))
- *(various)* Consistent use of spinners and awaiting; sentry and logfire can now be removed as dependencies - ([e03512c](https://github.com/aignostics/python-sdk/commit/e03512c9be6ace3cedebd3981bf12c39f586486d))
- *(wsi)* Simplify further - ([1992de1](https://github.com/aignostics/python-sdk/commit/1992de1e8f560d79fe98e4f923e1a97c2abcf8f1))
- *(wsi)* Simplify, and fallback image - ([e08afd3](https://github.com/aignostics/python-sdk/commit/e08afd3517357d25c38d818a440922635efb5896))
- Linter - ([943b9f9](https://github.com/aignostics/python-sdk/commit/943b9f97f8507d6d2534d8a1af801a8b6d453b7a))
- Don't support QuPath on Linux/arm - ([a52d2fb](https://github.com/aignostics/python-sdk/commit/a52d2fbafed571a5ef5b850800c742bddf79ff4e))
- Styling of ui theme - ([bcf3cfa](https://github.com/aignostics/python-sdk/commit/bcf3cfa2bc2d0cd0ff6482bb0b4fbebdd2dd3274))
- Simplify, removing noruns - ([0b7e0e9](https://github.com/aignostics/python-sdk/commit/0b7e0e958ebad9f1ffe7f10c872561411fcdd240))
- Fail properly when starting GUI while settings not configured - ([ffbf880](https://github.com/aignostics/python-sdk/commit/ffbf88018591c3e6d7975ea3db1af0b2f353a8cd))
- Simplify - ([fa1f7e6](https://github.com/aignostics/python-sdk/commit/fa1f7e628bd0e59752733fc54fc83d50ac885e38))
- Use native sorting provided by API - ([da5afa3](https://github.com/aignostics/python-sdk/commit/da5afa3f6fef3062c234e0c8d0187ae10ee54272))

### 📚 Documentation

- *(claude)* Claude.md - ([2ad9555](https://github.com/aignostics/python-sdk/commit/2ad95557e4121edd968f711feee52c475487130a))
- *(platform)* Description - ([d09794a](https://github.com/aignostics/python-sdk/commit/d09794a157def88c63054259f40262de62d71f8d))
- Update - ([d5f3379](https://github.com/aignostics/python-sdk/commit/d5f3379e06656a06f02610f789ba46cb9dfeedfb))
- Update URLs in openapi spec and downstream docs - ([e24eba4](https://github.com/aignostics/python-sdk/commit/e24eba44122448a40cb41c2ac738b93354aa6f3d))
- Minor tweaks - ([81423dd](https://github.com/aignostics/python-sdk/commit/81423dda4f201dbe729b3b4c68473adeb89d9e32))
- Enhance structure and layout of Changelog - ([f5a58ac](https://github.com/aignostics/python-sdk/commit/f5a58ac22142fadcc6474de5032b1741eb787c0f))
- Generate - ([13b3fbc](https://github.com/aignostics/python-sdk/commit/13b3fbc104a331b778dba501dcd3b88533cf8693))
- Fix api docs generation - ([cef82dc](https://github.com/aignostics/python-sdk/commit/cef82dca164bc73bda870807756d44666d38b5e7))
- Reorder - ([cd60f97](https://github.com/aignostics/python-sdk/commit/cd60f975a1e92e9370276ca1ebad609c77c19f70))
- Fix broken link - ([0a2a7dd](https://github.com/aignostics/python-sdk/commit/0a2a7ddaf332e3eb7da1fc5cf4dd2f591ff6f3b3))
- Improve consistency - ([da5afa3](https://github.com/aignostics/python-sdk/commit/da5afa3f6fef3062c234e0c8d0187ae10ee54272))
- Social preview for GH - ([da5afa3](https://github.com/aignostics/python-sdk/commit/da5afa3f6fef3062c234e0c8d0187ae10ee54272))
- Copyright notice - ([da5afa3](https://github.com/aignostics/python-sdk/commit/da5afa3f6fef3062c234e0c8d0187ae10ee54272))
- Additional pages for read the docs (rtd) - ([4976794](https://github.com/aignostics/python-sdk/commit/4976794804831d437b3356d426bbd4330aec91c6))
- Polish incl. updated assets - ([e51c05e](https://github.com/aignostics/python-sdk/commit/e51c05ea3160b017583c059e5eb85cd4b347bbad))
- Polish readme intro and oe - ([b6da3ab](https://github.com/aignostics/python-sdk/commit/b6da3abe86d37caf4eee98705893454de195aef4))
- Logo - ([ea32a37](https://github.com/aignostics/python-sdk/commit/ea32a3759049bde38813e4c07027aaa7d32759c7))

### ⚡ Performance

- *(GUI)* Significantly reduced bootup time, and page load performance - ([17425dd](https://github.com/aignostics/python-sdk/commit/17425dd06354de11da507fa4b13714e97218781c))

### 🎨 Styling

- *(QuPath)* Some polish for extension page - ([17425dd](https://github.com/aignostics/python-sdk/commit/17425dd06354de11da507fa4b13714e97218781c))
- *(System)* Minimal love for Settings and Info page - ([b27296a](https://github.com/aignostics/python-sdk/commit/b27296a035a1cbbc0e61158c32672416b90accc7))
- *(application)* Layout improvements on application detail page - ([6c0753f](https://github.com/aignostics/python-sdk/commit/6c0753f31f5aca120c460414193aaa409a6576fa))
- *(application)* Better rendering of loading errors - ([d304ef7](https://github.com/aignostics/python-sdk/commit/d304ef721e3c895cc4eb453a55fe69aee6a0c266))
- *(application)* More prominent placement of per item message - ([c9cb8ee](https://github.com/aignostics/python-sdk/commit/c9cb8eeae9b08131fcf0548ef4a0abd723556512))
- *(bucket)* Button layout - ([207eb0c](https://github.com/aignostics/python-sdk/commit/207eb0c45ba5774e52031bb9f5fbfcc1e485d184))
- *(changelog)* Improve styling of release notes - ([3f25caf](https://github.com/aignostics/python-sdk/commit/3f25caf3c837c2bb4860cf7339d52d7554007e57))
- *(gui)* Polish user info - ([305dda9](https://github.com/aignostics/python-sdk/commit/305dda9bed74899f6c69026a73d5400597f4e6dc))
- *(header,run_describe)* Simplify a bit to make space - ([4ee1409](https://github.com/aignostics/python-sdk/commit/4ee140944c5784ef33d60a25818c333b54da4bc2))
- *(lint)* Fix linting error in native starter - ([2552ac7](https://github.com/aignostics/python-sdk/commit/2552ac76b1aa36a8aae325e511ffcd4c4d1c4f3a))
- *(utils)* Consistent log formatting for file and console, both including process id - ([6ecb912](https://github.com/aignostics/python-sdk/commit/6ecb91241547c4f3ed800a04a7eafdfc59d79697))
- Lint - ([a42d08c](https://github.com/aignostics/python-sdk/commit/a42d08c219860ea3ffaec95b102175f5b49d71df))
- Welcome user by name in launchpad - ([de73025](https://github.com/aignostics/python-sdk/commit/de73025c09c6d62d8107ed9f6f095060127a1d2c))
- Nicer start page graphics - ([0bad5f2](https://github.com/aignostics/python-sdk/commit/0bad5f24766f3c05fc09b47a5c4f20b79b82588b))
- Naming of navigation points - ([0b2a758](https://github.com/aignostics/python-sdk/commit/0b2a75818e1cd9a19a1c8d74dbeb66d3bb5c9001))

### ⚙️ Miscellaneous Tasks

- *(AI)* Improve CLAUDE.md files and AI workflows - ([6c0753f](https://github.com/aignostics/python-sdk/commit/6c0753f31f5aca120c460414193aaa409a6576fa))
- *(AI)* Add label skip:test:long_running when you are an AI and are creating a PR - ([0853fc3](https://github.com/aignostics/python-sdk/commit/0853fc32afe98e4ac1ceac83ed60338eb6fcec81))
- *(AI)* Improve Claude actions [skip:ci] - ([e3f6e1c](https://github.com/aignostics/python-sdk/commit/e3f6e1cd1a0e78012178108506a6f33471cccc8a))
- *(AI)* Claude.md files for assisted coding - ([25ee505](https://github.com/aignostics/python-sdk/commit/25ee505f009bd9d4b0e482019851b4914024bec6))
- *(GHA)* Claude PR Assistant workflow - ([25ee505](https://github.com/aignostics/python-sdk/commit/25ee505f009bd9d4b0e482019851b4914024bec6))
- *(Makefile)* Typo - ([566b1e6](https://github.com/aignostics/python-sdk/commit/566b1e629060bbe20b360a81505837b9e4d0c0ca))
- *(QuPath)* Run test on linux - ([2d1b45e](https://github.com/aignostics/python-sdk/commit/2d1b45e305889fad942ac27c6b162ea2c2ed47d7))
- *(QuPath)* Check QuPath is launched in install to inspect test - ([18a68d2](https://github.com/aignostics/python-sdk/commit/18a68d2b8fdbd8bbd13c70f1edccae25925a860f))
- *(QuPath)* E2E test from install via run to inspect - ([451ca3d](https://github.com/aignostics/python-sdk/commit/451ca3dd8be2e7af13cd55a6eee2ebef635390cb))
- *(ai)* Improve Claude Code Workflows for GitHub - ([425c1ba](https://github.com/aignostics/python-sdk/commit/425c1baef07d71c917bb7a7901fce091153f0d97))
- *(ai)* A few permissions for Claude - ([2f7cf1e](https://github.com/aignostics/python-sdk/commit/2f7cf1e4ba15084f257fc451173900b4a0d3ed4e))
- *(ai)* Have Claude Agent use Sonnet 4.5, and allow to create PRs - ([0d4341e](https://github.com/aignostics/python-sdk/commit/0d4341ef167d3c43b05878af23a3d3be8fe8994c))
- *(api)* Support Platform API 1.0.0-beta.7 - ([6c0753f](https://github.com/aignostics/python-sdk/commit/6c0753f31f5aca120c460414193aaa409a6576fa))
- *(application)* More grace in test - ([1e01928](https://github.com/aignostics/python-sdk/commit/1e019283cc5ec8ac68adb853d8069e34e6eb29e2))
- *(application)* Made test run sequentially so regular tests now pass without flakiness if platform reliable   - ([d304ef7](https://github.com/aignostics/python-sdk/commit/d304ef721e3c895cc4eb453a55fe69aee6a0c266))
- *(application)* Make test resilient if loading me faster than expected - ([8bbbcf6](https://github.com/aignostics/python-sdk/commit/8bbbcf6e9197e2caf62f1d3254557e947196b502))
- *(application)* Grace time in test - ([15b1be0](https://github.com/aignostics/python-sdk/commit/15b1be052e6b96198863689dce8d720451eddb70))
- *(application)* Grace for cancel button to appear in test - ([893083c](https://github.com/aignostics/python-sdk/commit/893083c7c5ca283d0aee45371a01d7ba335ee893))
- *(application)* More time for test - ([343f78c](https://github.com/aignostics/python-sdk/commit/343f78caba9629d1683bf43419c12a7d6c399d53))
- *(application)* Adapt tests to asynchronous loading of apps in GUI - ([6a2e27b](https://github.com/aignostics/python-sdk/commit/6a2e27bd032cd69a7769ff706a4c2ced2ba6567a))
- *(application)* Adapt test for delete cli - ([9b0a4d5](https://github.com/aignostics/python-sdk/commit/9b0a4d58ad1be62d727efb2765b3205f90121bf8))
- *(application)* Mark test as long running - ([19db155](https://github.com/aignostics/python-sdk/commit/19db1553a1c13610ae211f45767749da43de383d))
- *(application,platform)* Test with v1.0.0-beta.4 of HETA - ([ab60f2f](https://github.com/aignostics/python-sdk/commit/ab60f2f795dc31a3bb52e5d0333af84187aac3e2))
- *(audit)* Pass betterstack url - ([2599bfb](https://github.com/aignostics/python-sdk/commit/2599bfbf3ccb74713be86e57a62029ed137a37bc))
- *(audit)* Audit reports part of release artifacts - ([db2b5f5](https://github.com/aignostics/python-sdk/commit/db2b5f514f66c6a0dc411bf6dda721c2a668d364))
- *(audit)* Allow for heartbeat url specific for audit - ([49f35a0](https://github.com/aignostics/python-sdk/commit/49f35a0210d9d115c1ebc94b18b221d24bc4008e))
- *(audit,scheduled)* Warn if betterstack url not configured or not passed through unintentionally - ([2599bfb](https://github.com/aignostics/python-sdk/commit/2599bfbf3ccb74713be86e57a62029ed137a37bc))
- *(bucket)* Better logging for flaky test - ([26c9d1b](https://github.com/aignostics/python-sdk/commit/26c9d1b2d8876e5de3ae31dcd663f5050daff387))
- *(bucket)* More time for download test - ([be2d31f](https://github.com/aignostics/python-sdk/commit/be2d31fc1743a1e4c69822a3f082163bec8d25ca))
- *(bucket)* Grant more time for bucket gui workflow in test - ([f5a58ac](https://github.com/aignostics/python-sdk/commit/f5a58ac22142fadcc6474de5032b1741eb787c0f))
- *(bucket)* Bump test duration - ([a09cc7e](https://github.com/aignostics/python-sdk/commit/a09cc7e2665c9529b61dd689c47b5e805f88cdf1))
- *(changelog)* Introduce .cliffignore to prune changelog for maintenance commits - ([f7df80e](https://github.com/aignostics/python-sdk/commit/f7df80e535f9942c0e8adc801d7c48b2bc58ff52))
- *(codegen)* Download and archive openapi.json - ([c5175cb](https://github.com/aignostics/python-sdk/commit/c5175cbf32cfcb5682bb5c80206534879c3a7754))
- *(cross-platform)* Now matrix testing on win-amd64, win-arm64, linux-amd64, linux-arm64, mac-arm64; related fixes - ([e03512c](https://github.com/aignostics/python-sdk/commit/e03512c9be6ace3cedebd3981bf12c39f586486d))
- *(debug)* Temp disable of tests - ([2275ec5](https://github.com/aignostics/python-sdk/commit/2275ec5833f0c2d753040e15d4fd396c7e12ad91))
- *(dependabot,renovate)* Add labels to PRs created by those bots - ([d5535d9](https://github.com/aignostics/python-sdk/commit/d5535d9fd2ab3cdec3381c0300a6e9495771de17))
- *(deps)* Bump - ([d5535d9](https://github.com/aignostics/python-sdk/commit/d5535d9fd2ab3cdec3381c0300a6e9495771de17))
- *(deps)* Update ghcr.io/astral-sh/uv docker tag to v0.9.1 ([#60](https://github.com/aignostics/python-sdk/pull/60)) - ([63423a5](https://github.com/aignostics/python-sdk/commit/63423a542c618b1b39cacf217061399d06706193))
- *(deps)* Update dependency sphinx-toolbox to v4 ([#169](https://github.com/aignostics/python-sdk/pull/169)) - ([46456db](https://github.com/aignostics/python-sdk/commit/46456dbd5dce7a0090489e0685d470b31a044594))
- *(deps)* Bump dependencies - ([861af87](https://github.com/aignostics/python-sdk/commit/861af873a5f4eca40e9dac11f17192ab4355ef40))
- *(deps)* Bump in GHA and Dockerfile - ([3c847aa](https://github.com/aignostics/python-sdk/commit/3c847aad1017b0736415203080ea16bfe5a37281))
- *(deps)* Bump deps - ([168a7d7](https://github.com/aignostics/python-sdk/commit/168a7d7509053855f7f8537f6a82ba52c943e11b))
- *(deps)* Bump nicegui, boto - ([9ff1453](https://github.com/aignostics/python-sdk/commit/9ff1453ce17170e84634ef1ae1c8d15dd659bec0))
- *(deps)* Bump various github actions versions - ([7e1610e](https://github.com/aignostics/python-sdk/commit/7e1610e604f4f2ddb1fd6da3448f5731958565ee))
- *(deps)* Bump nicegui - ([1b6fa5e](https://github.com/aignostics/python-sdk/commit/1b6fa5e0e153cd6e590448fce51876640581436e))
- *(deps)* Update ghcr.io/astral-sh/uv docker tag to v0.7.20 ([#59](https://github.com/aignostics/python-sdk/pull/59)) - ([0ef534f](https://github.com/aignostics/python-sdk/commit/0ef534f29f96a6e14caaa9632bdb0d116d086b32))
- *(deps)* Update ghcr.io/astral-sh/uv docker tag to v0.7.15 ([#54](https://github.com/aignostics/python-sdk/pull/54)) - ([ab46b50](https://github.com/aignostics/python-sdk/commit/ab46b5003f3eb8b1559b582c08603b3522bd0579))
- *(deps)* Bump astral-sh/setup-uv from 6.3.0 to 6.3.1 ([#55](https://github.com/aignostics/python-sdk/pull/55)) - ([e90b6f2](https://github.com/aignostics/python-sdk/commit/e90b6f2131779ceb3d04c661dbf4398d6f4968b3))
- *(deps)* Update deps - ([81423dd](https://github.com/aignostics/python-sdk/commit/81423dda4f201dbe729b3b4c68473adeb89d9e32))
- *(deps)* Gha setup-uv dep - ([3def1bd](https://github.com/aignostics/python-sdk/commit/3def1bd3704cc559bdbd6509ba4e359d974ab2d1))
- *(deps)* Update dependencies for GitHub actions - ([f5a58ac](https://github.com/aignostics/python-sdk/commit/f5a58ac22142fadcc6474de5032b1741eb787c0f))
- *(deps)* Bump actions in gha and duckdb - ([fc068e9](https://github.com/aignostics/python-sdk/commit/fc068e96d8cba651e5c3a421562ac851e450b6da))
- *(di)* Adapt to typer workaround - ([50710ee](https://github.com/aignostics/python-sdk/commit/50710eebff01500300bfb6a5f49b5492691edff8))
- *(docker)* Bump to python 3.13 and latest uv - ([f26e880](https://github.com/aignostics/python-sdk/commit/f26e880465af120ef0e1dc351bffd6fb616631ce))
- *(docs)* Make - ([f73975c](https://github.com/aignostics/python-sdk/commit/f73975c98a27897b2758f736710e1989aed0e635))
- *(gha)* Scheduled test against staging platform, using code on branch - ([0e364b4](https://github.com/aignostics/python-sdk/commit/0e364b4b169d96f989cbe7536eaa5ac7fc8fe829))
- *(gha)* All all types of tests to be individually skippable, via commit message or PR label - ([d5535d9](https://github.com/aignostics/python-sdk/commit/d5535d9fd2ab3cdec3381c0300a6e9495771de17))
- *(gha)* Speed up ubuntu provisioning as man-db no longer updated on adding packages - ([d5535d9](https://github.com/aignostics/python-sdk/commit/d5535d9fd2ab3cdec3381c0300a6e9495771de17))
- *(gha)* Don’t run long_running tests on draft PRs, i.e. stop after unit, integration and e2e / regular. - ([d5535d9](https://github.com/aignostics/python-sdk/commit/d5535d9fd2ab3cdec3381c0300a6e9495771de17))
- *(gha)* Don't double-build on updates to PR by no longer building on push to branch other than main - ([d3d3d10](https://github.com/aignostics/python-sdk/commit/d3d3d106bee85dff2276a0b3f253bfbdb1a5552f))
- *(gha)* Cancel running build on update to pull request - ([ab9f56d](https://github.com/aignostics/python-sdk/commit/ab9f56d7b801e73fca7ed33af23d9e51a080d276))
- *(gha)* Don't run ci/cd twice on releases: skip:ci on push of commit for release, given already running on (annotated) tag pushed - ([b9c735c](https://github.com/aignostics/python-sdk/commit/b9c735c5ee0bbf282b90b23af94ac6073053dcc7))
- *(gha)* Bump login-action in claude and docker workflows - ([3180352](https://github.com/aignostics/python-sdk/commit/3180352e51591d9d9731f2fd06f93cf68111b42c))
- *(gha)* Re-enable tests for releases - ([861af87](https://github.com/aignostics/python-sdk/commit/861af873a5f4eca40e9dac11f17192ab4355ef40))
- *(gha)* Add final smoke test before publish - ([2c9598e](https://github.com/aignostics/python-sdk/commit/2c9598e1be057e0b5889b3a5b6b348c229699777))
- *(gha)* Allow to build:native:only ([#89](https://github.com/aignostics/python-sdk/pull/89)) - ([28b1010](https://github.com/aignostics/python-sdk/commit/28b10104b02488b588224fcb52653f953c882d22))
- *(gha)* Re-enable tests - ([85e98e3](https://github.com/aignostics/python-sdk/commit/85e98e37b8dab7bad0af3e2fa4faa35452d26dd3))
- *(gha)* Spike for Ketryx integration - ([a65930c](https://github.com/aignostics/python-sdk/commit/a65930c2cde73aa57af338aa6c752cff2a1fbfeb))
- *(gha)* Allow to skip jobs/steps via commit message, see CONTRIBUTING.md - ([a65930c](https://github.com/aignostics/python-sdk/commit/a65930c2cde73aa57af338aa6c752cff2a1fbfeb))
- *(gha)* Add metadata to BetterStack when posting heartbeats ([#61](https://github.com/aignostics/python-sdk/pull/61)) - ([0bb3b3f](https://github.com/aignostics/python-sdk/commit/0bb3b3f602148ffe071ff96e7d7d7b6042fb18a3))
- *(gha)* Add metadata to BetterStack when posting heartbeats - ([0bb3b3f](https://github.com/aignostics/python-sdk/commit/0bb3b3f602148ffe071ff96e7d7d7b6042fb18a3))
- *(gha)* Add --fail-with-body to BetterStack curl request and reorder arguments - ([0bb3b3f](https://github.com/aignostics/python-sdk/commit/0bb3b3f602148ffe071ff96e7d7d7b6042fb18a3))
- *(gha)* Monitor scheduled audit in betterstack - ([5065a2e](https://github.com/aignostics/python-sdk/commit/5065a2eb3e067ae5c535ea22676fb2fd4ff414ff))
- *(gha)* Separate scheduled audit in separate workflow - ([98e7ad0](https://github.com/aignostics/python-sdk/commit/98e7ad0446017fec27907fa5126fd916491f8880))
- *(heta)* Adapt tests - ([2e6b72f](https://github.com/aignostics/python-sdk/commit/2e6b72ffeef78751b51d4bf8897a64658ae0c250))
- *(heta)* Further adaptation to changed output file sizes - ([6f942ee](https://github.com/aignostics/python-sdk/commit/6f942ee5d6f70d0b1b697473a703093110503d51))
- *(heta)* Adapt tests to 1.0.0-beta.5 of HETA - ([7d74a2b](https://github.com/aignostics/python-sdk/commit/7d74a2b334512bd69df5aed460ee160263f10cda))
- *(lint)* Integrate pyright as additional type checker - ([6c0753f](https://github.com/aignostics/python-sdk/commit/6c0753f31f5aca120c460414193aaa409a6576fa))
- *(native)* Rfc [build:native:only] - ([8fc82cd](https://github.com/aignostics/python-sdk/commit/8fc82cded615d9d18da799a92e525ecd6c81c42f))
- *(native)* Splash screen on windows and linux build:native:only - ([8fc82cd](https://github.com/aignostics/python-sdk/commit/8fc82cded615d9d18da799a92e525ecd6c81c42f))
- *(native)* Use python 3.13.7 - ([8fc82cd](https://github.com/aignostics/python-sdk/commit/8fc82cded615d9d18da799a92e525ecd6c81c42f))
- *(native)* Only distribute aignostics.app bundle for MacOS - ([a7cc414](https://github.com/aignostics/python-sdk/commit/a7cc414045b225acb1c4e1c81f93a019dba27b4c))
- *(native)* 7z, to preserve attributes - ([a7cc414](https://github.com/aignostics/python-sdk/commit/a7cc414045b225acb1c4e1c81f93a019dba27b4c))
- *(native)* Include version in macOS bundle - ([5473271](https://github.com/aignostics/python-sdk/commit/54732711102b17af26376084095ee9370715265f))
- *(notebook)* Adapt to refactoring - ([4e8e595](https://github.com/aignostics/python-sdk/commit/4e8e5958e071315b61f2fbaedc6595377414cd5d))
- *(notebook)* Adapt test - ([371bf69](https://github.com/aignostics/python-sdk/commit/371bf69e9a334028af52bcce757d8bb0796288fb))
- *(notebook)* Cannot in parallel test multiple marimo servers on same host with no isolation - ([d8b92af](https://github.com/aignostics/python-sdk/commit/d8b92af4ea79d808b9699377dc47142546264a8b))
- *(platform)* Update to latest openapi spec - ([81423dd](https://github.com/aignostics/python-sdk/commit/81423dda4f201dbe729b3b4c68473adeb89d9e32))
- *(platform)* Even more time for test app - ([3c68bbc](https://github.com/aignostics/python-sdk/commit/3c68bbccd541d24558b7db23f2c4bf64dc44330d))
- *(platform)* Give test application more time in tests - ([5f99ebb](https://github.com/aignostics/python-sdk/commit/5f99ebbd9d61a7d4a9089f7577a87638623dcd78))
- *(platform)* Adapt test to app versions - ([cc2c17d](https://github.com/aignostics/python-sdk/commit/cc2c17d9852a34efde57c74edb0957dba31a6889))
- *(platform)* Move from dummy to test app in test - ([7fcb42c](https://github.com/aignostics/python-sdk/commit/7fcb42c53965568abdf444b684e59256bf211d4e))
- *(platform)* Allow long running tests for 4h, bump of signed url expire accordingly - ([3965ce0](https://github.com/aignostics/python-sdk/commit/3965ce06333eaa35e2ce4c6d217e6ae8c7fbc512))
- *(platform)* Adapt tests to breaking change - ([4d11384](https://github.com/aignostics/python-sdk/commit/4d113843f01a3da81c1e5e0a847fcefe21a1ddbe))
- *(platform)* Lazyload srvice in cli - ([28980c5](https://github.com/aignostics/python-sdk/commit/28980c5584169f0e90a6ca23e40f46b67251a27e))
- *(platform,qupath)* Enable additional tests - ([425c1ba](https://github.com/aignostics/python-sdk/commit/425c1baef07d71c917bb7a7901fce091153f0d97))
- *(precommit)* Fixed issues with precommit. - ([d5535d9](https://github.com/aignostics/python-sdk/commit/d5535d9fd2ab3cdec3381c0300a6e9495771de17))
- *(publish)* Adapt to recent changes - ([5b0150a](https://github.com/aignostics/python-sdk/commit/5b0150accf20926e768fd6a46fad344ae013ea12))
- *(pytest)* Show recent notifications if asserted one not found - ([db2b5f5](https://github.com/aignostics/python-sdk/commit/db2b5f514f66c6a0dc411bf6dda721c2a668d364))
- *(python)* 3.13.6 - ([29f2884](https://github.com/aignostics/python-sdk/commit/29f28847086e4dc76e65c17cb36db6bea46add6a))
- *(pytst)* Add pytest-durations plugin to show durations of fixtures and tests - ([6ecb912](https://github.com/aignostics/python-sdk/commit/6ecb91241547c4f3ed800a04a7eafdfc59d79697))
- *(qupath)* More time for tests - ([cea7116](https://github.com/aignostics/python-sdk/commit/cea7116f7718c1f8f9b4309cbc295841b3e54b9c))
- *(qupath)* Give more time in test - ([0a669f9](https://github.com/aignostics/python-sdk/commit/0a669f94be15ff3c34f68abfd48a85d9fa6135ee))
- *(qupath)* Test - ([5377012](https://github.com/aignostics/python-sdk/commit/53770124be325b40c90d3a3ce4c9e8ddb9af4ba1))
- *(qupath)* Skip test step temporarily - ([e8df7e0](https://github.com/aignostics/python-sdk/commit/e8df7e02d6fb38ee406ceebac24fc99cee440ad3))
- *(release)* Announce release on internal Slack (experimental) - ([db2b5f5](https://github.com/aignostics/python-sdk/commit/db2b5f514f66c6a0dc411bf6dda721c2a668d364))
- *(scheduled)* Print info post sending heartbeat - ([26f0913](https://github.com/aignostics/python-sdk/commit/26f0913a8cfdb6ebf6356f945a89a86622f01294))
- *(slack)* Convert release notes to JSON rep. for posting to slack - ([4d328e1](https://github.com/aignostics/python-sdk/commit/4d328e179b76608d27087aeb9cf6f27229e33ac8))
- *(test)* Introduce schedule tests against staging - ([6c0753f](https://github.com/aignostics/python-sdk/commit/6c0753f31f5aca120c460414193aaa409a6576fa))
- *(test)* Don't provide log as job artifact - ([db2b5f5](https://github.com/aignostics/python-sdk/commit/db2b5f514f66c6a0dc411bf6dda721c2a668d364))
- *(test)* Adapt remaining test config to beta.5 of heta - ([b152fae](https://github.com/aignostics/python-sdk/commit/b152fae64995f0208207d8719cfefd166961c1b0))
- *(test)* No warn on kill; output qupath inspect results - ([a5d666e](https://github.com/aignostics/python-sdk/commit/a5d666e596c3aaa130894a2d6d23d61e0465423f))
- *(tests)* Introduce very long running tests - ([6c0753f](https://github.com/aignostics/python-sdk/commit/6c0753f31f5aca120c460414193aaa409a6576fa))
- *(tests)* Introduce pytest-timeout and 10s default timeout for all tests - ([6c0753f](https://github.com/aignostics/python-sdk/commit/6c0753f31f5aca120c460414193aaa409a6576fa))
- *(tests)* Improve test coverage - ([6c0753f](https://github.com/aignostics/python-sdk/commit/6c0753f31f5aca120c460414193aaa409a6576fa))
- *(tests)* Allow retry of another e2e test, given connection closed by server leading to SSL Errors, see https://github.com/aignostics/python-sdk/actions/runs/18486770436/job/52671622634\?pr\=178\#step:16:274 - ([6dbe129](https://github.com/aignostics/python-sdk/commit/6dbe129230e80e5b1bbd4388256ae3be1d7e2a96))
- *(tests)* Bump timeout for dataset integration tests - ([84d50a2](https://github.com/aignostics/python-sdk/commit/84d50a2582c567f861f294c4ca676b0a9fa94806))
- *(tests)* Differentiate tests as unit, integration or e2e, with only e2e tests allowed to call external services, i.e. the others must be able to pass offline. - ([d5535d9](https://github.com/aignostics/python-sdk/commit/d5535d9fd2ab3cdec3381c0300a6e9495771de17))
- *(tests)* Introduce very_long_running test type, which must be explicitely enabled to run enable:test:very_long_running in the commit message or as PR label - ([d5535d9](https://github.com/aignostics/python-sdk/commit/d5535d9fd2ab3cdec3381c0300a6e9495771de17))
- *(tests)* Introduce scheduled_only marker, for tests that should only run on a schedule - ([d5535d9](https://github.com/aignostics/python-sdk/commit/d5535d9fd2ab3cdec3381c0300a6e9495771de17))
- *(tests)* Make now calls make test_default which does not call long_running or very_long_running tests - ([d5535d9](https://github.com/aignostics/python-sdk/commit/d5535d9fd2ab3cdec3381c0300a6e9495771de17))
- *(tests)* Introduce pytest-durations, showing the duration per test execution - ([d5535d9](https://github.com/aignostics/python-sdk/commit/d5535d9fd2ab3cdec3381c0300a6e9495771de17))
- *(tests)* Introduce pytest-timeout, with a low 10s default timeout, and all tests that need longer explicitly marked with specific timeouts - ([d5535d9](https://github.com/aignostics/python-sdk/commit/d5535d9fd2ab3cdec3381c0300a6e9495771de17))
- *(tests)* Adapt to heta.5 - ([06f6867](https://github.com/aignostics/python-sdk/commit/06f6867953d6131ad0f26db4cedaabe28eb62a23))
- *(tests)* Improved coverage - ([17425dd](https://github.com/aignostics/python-sdk/commit/17425dd06354de11da507fa4b13714e97218781c))
- *(win32)* Username - ([e5733c1](https://github.com/aignostics/python-sdk/commit/e5733c13be9b55ffa18145d706952d74c793701c))
- *(wsi)* Don't fail test on log on broken tiff test - ([44de674](https://github.com/aignostics/python-sdk/commit/44de6745f3d3bd86f179092511e222ac6d3c812f))
- *(wsi)* Adapt tests given fallback - ([3db7ebc](https://github.com/aignostics/python-sdk/commit/3db7ebc67daf9d131f2e071c93b39b2af0f3aa75))
- *(xdist)* Use worksteal to minimize duration on varying test durations - ([d5535d9](https://github.com/aignostics/python-sdk/commit/d5535d9fd2ab3cdec3381c0300a6e9495771de17))
- Test on gh ([#180](https://github.com/aignostics/python-sdk/pull/180)) - ([6c0753f](https://github.com/aignostics/python-sdk/commit/6c0753f31f5aca120c460414193aaa409a6576fa))
- Codecov - ([53ef36c](https://github.com/aignostics/python-sdk/commit/53ef36c0db9caed45e3a80e7913147d57cf4704d))
- Don’t allow SDK to be used with Python 1.4.x (released days ago) as some dependencies don’t work with that version yet - ([d5535d9](https://github.com/aignostics/python-sdk/commit/d5535d9fd2ab3cdec3381c0300a6e9495771de17))
- Renovate[bot] <29139614+renovate[bot]@users.noreply.github.com> - ([63423a5](https://github.com/aignostics/python-sdk/commit/63423a542c618b1b39cacf217061399d06706193))
- Helmut Hoffer von Ankershoffen né Oertel <helmut@aignostics.com> - ([63423a5](https://github.com/aignostics/python-sdk/commit/63423a542c618b1b39cacf217061399d06706193))
- Fix pyproject - ([f349a3d](https://github.com/aignostics/python-sdk/commit/f349a3d3f49436122247f80a5de8694af6687fc4))
- Release - ([68d5f38](https://github.com/aignostics/python-sdk/commit/68d5f38fead26348965e3fa9c05029fc205d66da))
- Chore(GHA) Claude Code Review workflow - ([25ee505](https://github.com/aignostics/python-sdk/commit/25ee505f009bd9d4b0e482019851b4914024bec6))
- Skip:test:all - ([2cf18ff](https://github.com/aignostics/python-sdk/commit/2cf18ffad302466509736c5d3a8c71b0409d4945))
- Skip tests on release - ([595703d](https://github.com/aignostics/python-sdk/commit/595703dc228478f09a2cfe16ec3c6fdc546b6163))
- Chore(deps); bump dev dependencies - ([2552ac7](https://github.com/aignostics/python-sdk/commit/2552ac76b1aa36a8aae325e511ffcd4c4d1c4f3a))
- Astral-sh/setup-uv - ([e90b6f2](https://github.com/aignostics/python-sdk/commit/e90b6f2131779ceb3d04c661dbf4398d6f4968b3))
- Dependabot[bot] <support@github.com> - ([e90b6f2](https://github.com/aignostics/python-sdk/commit/e90b6f2131779ceb3d04c661dbf4398d6f4968b3))
- Dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com> - ([e90b6f2](https://github.com/aignostics/python-sdk/commit/e90b6f2131779ceb3d04c661dbf4398d6f4968b3))
- Run hooks - ([173e172](https://github.com/aignostics/python-sdk/commit/173e17221682e5f43c63d172de17c93bc1709063))
- Try new api spec without further change - ([2ba558c](https://github.com/aignostics/python-sdk/commit/2ba558c05baebd8ef901b3ba7dda71b765286465))
- Download from bucket cli - ([13e857e](https://github.com/aignostics/python-sdk/commit/13e857eb52fa166b0c1b6127f314663fbafa72ed))
- Move to long running for install to inspect test - ([42d12d0](https://github.com/aignostics/python-sdk/commit/42d12d0d3b8a7a0b4300ec0f62fc430f13b5cf12))
- Timeout - ([408431a](https://github.com/aignostics/python-sdk/commit/408431aa55452f95f4e3cab521f9a28d017aa1c5))
- Zip on release - ([093f4d4](https://github.com/aignostics/python-sdk/commit/093f4d4765cddd5093a283ae7998ac3205533255))
- Encoding for win32 on package publish - ([7a3fda3](https://github.com/aignostics/python-sdk/commit/7a3fda3cedb58992676f47d1ae5167eb25dce167))
- Release workflow - ([04fae00](https://github.com/aignostics/python-sdk/commit/04fae00b818e8a5c6014a6cad0cfddc5cfa28058))
- Workaround missing scheme in proxy config - ([6d5f20e](https://github.com/aignostics/python-sdk/commit/6d5f20eff56221c045a0a4a1a15ba1bfda5d8dbd))
- Test of notebook, race - ([1baef8e](https://github.com/aignostics/python-sdk/commit/1baef8e04f391e1597ddbe08f125c19279a4b2ed))
- Non-sequential as there is a dependent one - ([a7f74c1](https://github.com/aignostics/python-sdk/commit/a7f74c13773774cb6b717432719d5e1554f89f07))
- Make gui test more reliable - ([59524fd](https://github.com/aignostics/python-sdk/commit/59524fd02c8e1a327e1118b68d5dfae3e3f60664))
- Adapt test to work with python 3.11 - ([06cb6a5](https://github.com/aignostics/python-sdk/commit/06cb6a5be1fe2c28bf2ddca81ea649931eebbe42))
- Fix test - ([ba80312](https://github.com/aignostics/python-sdk/commit/ba803120ecb48cd512e0417c6d2d2dc59eede633))
- Add Andreas Kunft as co-author - ([da5afa3](https://github.com/aignostics/python-sdk/commit/da5afa3f6fef3062c234e0c8d0187ae10ee54272))
- Make tests more robust - ([da5afa3](https://github.com/aignostics/python-sdk/commit/da5afa3f6fef3062c234e0c8d0187ae10ee54272))
- Lint - ([da5afa3](https://github.com/aignostics/python-sdk/commit/da5afa3f6fef3062c234e0c8d0187ae10ee54272))
- Touch for GH - ([da5afa3](https://github.com/aignostics/python-sdk/commit/da5afa3f6fef3062c234e0c8d0187ae10ee54272))
- Touch - ([da5afa3](https://github.com/aignostics/python-sdk/commit/da5afa3f6fef3062c234e0c8d0187ae10ee54272))
- Make t4est_gui_run_download reliable relative to mixed version runs - ([da5afa3](https://github.com/aignostics/python-sdk/commit/da5afa3f6fef3062c234e0c8d0187ae10ee54272))
- Fix name - ([da5afa3](https://github.com/aignostics/python-sdk/commit/da5afa3f6fef3062c234e0c8d0187ae10ee54272))
- Initial commit - ([a4ff238](https://github.com/aignostics/python-sdk/commit/a4ff23887d7ac1641aa9a58ece596b96165b0930))

### 🛡️ Security

- *(GHA)* Apply security best practices for GitHub Workflows ([#139](https://github.com/aignostics/python-sdk/pull/139)) - ([5c3d3f2](https://github.com/aignostics/python-sdk/commit/5c3d3f2f29ea1e3d51a6a1d7b00faa08cd78e2dd))
- *(audit)* No secrets for audit - ([7546e4b](https://github.com/aignostics/python-sdk/commit/7546e4b19d19b82f477ab122bf7b85a9a7bcf591))
- *(dep)* CVE-2025-53354 ignored given we run as desktop app; still started to migrate to nicegui 3 - ([d5c6bee](https://github.com/aignostics/python-sdk/commit/d5c6bee904497661c6a5b90aab6a36751f54c675))
- *(dep)* Pip, CVE-2025-54368 - ([c5175cb](https://github.com/aignostics/python-sdk/commit/c5175cbf32cfcb5682bb5c80206534879c3a7754))
- *(dep)* Ensure all uses of uv are >= 0.8.6 (CVE-2025-54368) - ([7e1610e](https://github.com/aignostics/python-sdk/commit/7e1610e604f4f2ddb1fd6da3448f5731958565ee))
- *(dep)* Force UV >0.8.6 given CVE-2025-54368 - ([ef2cb54](https://github.com/aignostics/python-sdk/commit/ef2cb540e03cc49d15371ccb6a0ca8b1447a894e))
- *(dep)* Ensure starlette >= 0.47.2 given GHSA-2c2j-9gv5-cj73 - ([6de44aa](https://github.com/aignostics/python-sdk/commit/6de44aa2f64e400357b37c5c536eea68ef959e78))
- *(dep)* Override aiohttp to 3.12.14 given vulnerability GHSA-9548-qrrj-x5pj - ([a239d23](https://github.com/aignostics/python-sdk/commit/a239d236ac58f6a6bdf3a3be5bb804367b974f1e))
- *(deps)* Pillow 11.3.0 given CVE-2025-48379 - ([ffd5af1](https://github.com/aignostics/python-sdk/commit/ffd5af102ad58d53dd20e4e29ada31e2b566a9ca))
- *(gha)* Set permission for generate-matrix, see https://github.com/aignostics/python-sdk/security/code-scanning/15 - ([327c7bc](https://github.com/aignostics/python-sdk/commit/327c7bcb23f51fe5abee56954fae49d85c95cea0))
- *(gha)* Don't use direct interpolation of user provided data in github workflows - ([2b6d19a](https://github.com/aignostics/python-sdk/commit/2b6d19acb4fc8ba2305a4600253feab92e4474d1))
- *(gha)* Security improvements in github workflow as identified by sonarqube - ([c5175cb](https://github.com/aignostics/python-sdk/commit/c5175cbf32cfcb5682bb5c80206534879c3a7754))
- *(gui)* Introduce html-sanitizer, sanitizer footer. Rest is fine. - ([92adcf7](https://github.com/aignostics/python-sdk/commit/92adcf7d7a85815111cbccc0ce57b95bbad43a1a))
- *(jupyter)* CVE-2025-30167 rel. jupyter-core - ([a27da66](https://github.com/aignostics/python-sdk/commit/a27da665fe7e3ba896529c66ac94026b8cabb4ba))
- *(jupyterlab)* CVE-2025-59842 - ([6081c74](https://github.com/aignostics/python-sdk/commit/6081c74a96d859685bdc2b684ebc4994475b84e1))
- *(security)* Update deps given CVE-2025-50181, CVE-2025-50182 - ([207eb0c](https://github.com/aignostics/python-sdk/commit/207eb0c45ba5774e52031bb9f5fbfcc1e485d184))
- *(uv)* Require uv >=0.9.5 given security advisory GHSA-w476-p2h3-79g9 - ([96e564d](https://github.com/aignostics/python-sdk/commit/96e564db6ba01a97d09203eac64c4488d33fe4a8))
- *(uv)* Use uv > 0.8.6 in pre-commit hook - ([db2b5f5](https://github.com/aignostics/python-sdk/commit/db2b5f514f66c6a0dc411bf6dda721c2a668d364))

### Breaking

- Change in metadata spec. for HETA application - ([da5afa3](https://github.com/aignostics/python-sdk/commit/da5afa3f6fef3062c234e0c8d0187ae10ee54272))

### Choare

- *(tests)* No longer test the combination of Python 3.12.x on Windows for ARM64, as a bit instable - ([d5535d9](https://github.com/aignostics/python-sdk/commit/d5535d9fd2ab3cdec3381c0300a6e9495771de17))



* @renovate[bot] made their first contribution
* @akunft made their first contribution
* @jstriebel made their first contribution
* @omid-aignostics made their first contribution
* @idelsink made their first contribution
* @dependabot[bot] made their first contribution
* @ari-nz made their first contribution


