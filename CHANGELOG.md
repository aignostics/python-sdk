[🔬 Aignostics Python SDK](https://aignostics.readthedocs.io/en/latest/)

# [0.2.215](https://github.com/aignostics/python-sdk/compare/v0.2.214..0.2.215) - 2025-12-01

### 🐛 Bug Fixes

- Paginate run results ([#295](https://github.com/orhun/git-cliff/issues/295)) - ([0e5d821](https://github.com/aignostics/python-sdk/commit/0e5d821775eaff34617822fcf7c2e1c3a79e4eaa))

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
- Disable flaky GUI tests on macos-latest and python 3.13 ([#293](https://github.com/orhun/git-cliff/issues/293)) - ([35aeab6](https://github.com/aignostics/python-sdk/commit/35aeab6427758c8bdf21644180b0ef1b9c1ebd8f))



* @neelay-aign made their first contribution in [#291](https://github.com/aignostics/python-sdk/pull/291)

# [v0.2.213](https://github.com/aignostics/python-sdk/compare/v0.2.212..v0.2.213) - 2025-11-28

### ⛰️  Features

- *(platform, application)* Introduce flex start ([#292](https://github.com/orhun/git-cliff/issues/292)) - ([8122a49](https://github.com/aignostics/python-sdk/commit/8122a49a728a6ff8368f509e23b0b6fc86700ad9))
- *(platform, application)* Introduce flex start - ([8122a49](https://github.com/aignostics/python-sdk/commit/8122a49a728a6ff8368f509e23b0b6fc86700ad9))

### 🐛 Bug Fixes

- Download single artifact - ([49941e0](https://github.com/aignostics/python-sdk/commit/49941e0063c294cb33b7bc95b1643ace3781dd2f))
- Revert CLI_REFERENCE.md to remove hardcoded timestamps [skip:ci, skip:test:long-running, skip:test:matrix-runner] - ([739687a](https://github.com/aignostics/python-sdk/commit/739687aa3dbaa018b7e244d6009a56e6bd162f5e))
- Unify mapping usage and docs - ([e5c164e](https://github.com/aignostics/python-sdk/commit/e5c164e7e64252e660320e1c323d386be061068f))
- Edit profile button opens new tab ([#286](https://github.com/orhun/git-cliff/issues/286)) - ([176c128](https://github.com/aignostics/python-sdk/commit/176c1285ada86226c77cee25c4b2d638d30d5b83))
- Handle incomplete DICOM pyramid when getting thumbnail ([#281](https://github.com/orhun/git-cliff/issues/281)) - ([9caa6e1](https://github.com/aignostics/python-sdk/commit/9caa6e14c84175d48ce14b3ef077094f91ab4598))

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

- *(application)* Pipeline settings in GUI and CLI ([#271](https://github.com/orhun/git-cliff/issues/271)) - ([feaa047](https://github.com/aignostics/python-sdk/commit/feaa047d2608a302e162260606045b8c026e20fe))

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
- Bump he-tme to a version that utilises a 1hr timeout ([#262](https://github.com/orhun/git-cliff/issues/262)) - ([e0e5586](https://github.com/aignostics/python-sdk/commit/e0e5586636c11084cae2db7a5b2e9ffb6b6c374f))


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
- Add missing expires_seconds argument to _get_three_spots_payload_for_test ([#213](https://github.com/orhun/git-cliff/issues/213)) - ([78b4b63](https://github.com/aignostics/python-sdk/commit/78b4b635a35f162109b9625023204c76a7c7a6ec))
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
- *(deps)* Update anthropics/claude-code-action action to v1.0.15 ([#219](https://github.com/orhun/git-cliff/issues/219)) - ([dfacc37](https://github.com/aignostics/python-sdk/commit/dfacc37e8f92f7bf438ecfacac33a683024f722b))
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
- *(dataset)* Move business logic to from CLI to service. ([#204](https://github.com/orhun/git-cliff/issues/204)) - ([27e7f9a](https://github.com/aignostics/python-sdk/commit/27e7f9a5c7fb59d3fc27441e5838b508d9a58e2a))
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
- *(platform)* Fix race condition in e2e test due to caching ([#206](https://github.com/orhun/git-cliff/issues/206)) - ([6ea313b](https://github.com/aignostics/python-sdk/commit/6ea313bf6d86d55b1f9844c60c94fe55e302bc2d))
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

### 🛡️ Security

- *(uv)* Require uv >=0.9.5 given security advisory GHSA-w476-p2h3-79g9 - ([96e564d](https://github.com/aignostics/python-sdk/commit/96e564db6ba01a97d09203eac64c4488d33fe4a8))


# [v0.2.194](https://github.com/aignostics/python-sdk/compare/v0.2.193..v0.2.194) - 2025-10-23

### 🐛 Bug Fixes

- *(ai)* Claude workflows - ([0a96143](https://github.com/aignostics/python-sdk/commit/0a961439b990101607d65b29b70d12099d4c3827))

### 🛡️ Security

- *(uv)* Require uv >=0.9.5 given security advisory GHSA-w476-p2h3-79g9 - ([34ad7a5](https://github.com/aignostics/python-sdk/commit/34ad7a5671c3db48d4de6cf021588cd5935e36de))


# [v0.2.193](https://github.com/aignostics/python-sdk/compare/v0.2.192..v0.2.193) - 2025-10-22

### ⛰️  Features

- *(application)* Custom metadata with run and scheduling information in custom metadata - ([6c0753f](https://github.com/aignostics/python-sdk/commit/6c0753f31f5aca120c460414193aaa409a6576fa))
- *(platform)* Retries and caching for read-only and auth operations - ([6c0753f](https://github.com/aignostics/python-sdk/commit/6c0753f31f5aca120c460414193aaa409a6576fa))
- *(platform)* Dynamic user agent for all operations - ([6c0753f](https://github.com/aignostics/python-sdk/commit/6c0753f31f5aca120c460414193aaa409a6576fa))

### 🐛 Bug Fixes

- *(application)* Error handling if application_versions called with … ([#178](https://github.com/orhun/git-cliff/issues/178)) - ([6dbe129](https://github.com/aignostics/python-sdk/commit/6dbe129230e80e5b1bbd4388256ae3be1d7e2a96))
- *(application)* Error handling if application_versions called with str arg - ([6dbe129](https://github.com/aignostics/python-sdk/commit/6dbe129230e80e5b1bbd4388256ae3be1d7e2a96))

### 🎨 Styling

- *(application)* Layout improvements on application detail page - ([6c0753f](https://github.com/aignostics/python-sdk/commit/6c0753f31f5aca120c460414193aaa409a6576fa))

### ⚙️ Miscellaneous Tasks

- *(AI)* Improve CLAUDE.md files and AI workflows - ([6c0753f](https://github.com/aignostics/python-sdk/commit/6c0753f31f5aca120c460414193aaa409a6576fa))
- *(ai)* Improve Claude Code Workflows for GitHub - ([425c1ba](https://github.com/aignostics/python-sdk/commit/425c1baef07d71c917bb7a7901fce091153f0d97))
- *(ai)* A few permissions for Claude - ([2f7cf1e](https://github.com/aignostics/python-sdk/commit/2f7cf1e4ba15084f257fc451173900b4a0d3ed4e))
- *(api)* Support Platform API 1.0.0-beta.7 - ([6c0753f](https://github.com/aignostics/python-sdk/commit/6c0753f31f5aca120c460414193aaa409a6576fa))
- *(gha)* Scheduled test against staging platform, using code on branch - ([0e364b4](https://github.com/aignostics/python-sdk/commit/0e364b4b169d96f989cbe7536eaa5ac7fc8fe829))
- *(lint)* Integrate pyright as additional type checker - ([6c0753f](https://github.com/aignostics/python-sdk/commit/6c0753f31f5aca120c460414193aaa409a6576fa))
- *(platform,qupath)* Enable additional tests - ([425c1ba](https://github.com/aignostics/python-sdk/commit/425c1baef07d71c917bb7a7901fce091153f0d97))
- *(qupath)* More time for tests - ([cea7116](https://github.com/aignostics/python-sdk/commit/cea7116f7718c1f8f9b4309cbc295841b3e54b9c))
- *(test)* Introduce schedule tests against staging - ([6c0753f](https://github.com/aignostics/python-sdk/commit/6c0753f31f5aca120c460414193aaa409a6576fa))
- *(tests)* Introduce very long running tests - ([6c0753f](https://github.com/aignostics/python-sdk/commit/6c0753f31f5aca120c460414193aaa409a6576fa))
- *(tests)* Introduce pytest-timeout and 10s default timeout for all tests - ([6c0753f](https://github.com/aignostics/python-sdk/commit/6c0753f31f5aca120c460414193aaa409a6576fa))
- *(tests)* Improve test coverage - ([6c0753f](https://github.com/aignostics/python-sdk/commit/6c0753f31f5aca120c460414193aaa409a6576fa))
- *(tests)* Allow retry of another e2e test, given connection closed by server leading to SSL Errors, see https://github.com/aignostics/python-sdk/actions/runs/18486770436/job/52671622634\?pr\=178\#step:16:274 - ([6dbe129](https://github.com/aignostics/python-sdk/commit/6dbe129230e80e5b1bbd4388256ae3be1d7e2a96))
- *(tests)* Bump timeout for dataset integration tests - ([84d50a2](https://github.com/aignostics/python-sdk/commit/84d50a2582c567f861f294c4ca676b0a9fa94806))
- Test on gh ([#180](https://github.com/orhun/git-cliff/issues/180)) - ([6c0753f](https://github.com/aignostics/python-sdk/commit/6c0753f31f5aca120c460414193aaa409a6576fa))
- Codecov - ([53ef36c](https://github.com/aignostics/python-sdk/commit/53ef36c0db9caed45e3a80e7913147d57cf4704d))


# [v0.2.192](https://github.com/aignostics/python-sdk/compare/v0.2.191..v0.2.192) - 2025-10-13

### ⚙️ Miscellaneous Tasks

- *(AI)* Add label skip:test:long_running when you are an AI and are creating a PR - ([0853fc3](https://github.com/aignostics/python-sdk/commit/0853fc32afe98e4ac1ceac83ed60338eb6fcec81))


# [v0.2.191](https://github.com/aignostics/python-sdk/compare/v0.2.190..v0.2.191) - 2025-10-13

### 🐛 Bug Fixes

- *(system)* Rendering of json editor content - had to find workaround given bug in NiceGUI3 for json_editor - ([d5535d9](https://github.com/aignostics/python-sdk/commit/d5535d9fd2ab3cdec3381c0300a6e9495771de17))

### 🚜 Refactor

- *(dataset,wsi)* Catch exceptions in CLI commands - ([d5535d9](https://github.com/aignostics/python-sdk/commit/d5535d9fd2ab3cdec3381c0300a6e9495771de17))
- *(qupath)* Don’t count system as unhealthy if QuPath application not installed - ([d5535d9](https://github.com/aignostics/python-sdk/commit/d5535d9fd2ab3cdec3381c0300a6e9495771de17))
- *(tests)* Refactored tests to reduce flakiness where avoidable, i.e. not solely dependent on external services - ([d5535d9](https://github.com/aignostics/python-sdk/commit/d5535d9fd2ab3cdec3381c0300a6e9495771de17))

### ⚙️ Miscellaneous Tasks

- *(dependabot,renovate)* Add labels to PRs created by those bots - ([d5535d9](https://github.com/aignostics/python-sdk/commit/d5535d9fd2ab3cdec3381c0300a6e9495771de17))
- *(deps)* Bump - ([d5535d9](https://github.com/aignostics/python-sdk/commit/d5535d9fd2ab3cdec3381c0300a6e9495771de17))
- *(gha)* All all types of tests to be individually skippable, via commit message or PR label - ([d5535d9](https://github.com/aignostics/python-sdk/commit/d5535d9fd2ab3cdec3381c0300a6e9495771de17))
- *(gha)* Speed up ubuntu provisioning as man-db no longer updated on adding packages - ([d5535d9](https://github.com/aignostics/python-sdk/commit/d5535d9fd2ab3cdec3381c0300a6e9495771de17))
- *(gha)* Don’t run long_running tests on draft PRs, i.e. stop after unit, integration and e2e / regular. - ([d5535d9](https://github.com/aignostics/python-sdk/commit/d5535d9fd2ab3cdec3381c0300a6e9495771de17))
- *(precommit)* Fixed issues with precommit. - ([d5535d9](https://github.com/aignostics/python-sdk/commit/d5535d9fd2ab3cdec3381c0300a6e9495771de17))
- *(tests)* Differentiate tests as unit, integration or e2e, with only e2e tests allowed to call external services, i.e. the others must be able to pass offline. - ([d5535d9](https://github.com/aignostics/python-sdk/commit/d5535d9fd2ab3cdec3381c0300a6e9495771de17))
- *(tests)* Introduce very_long_running test type, which must be explicitely enabled to run enable:test:very_long_running in the commit message or as PR label - ([d5535d9](https://github.com/aignostics/python-sdk/commit/d5535d9fd2ab3cdec3381c0300a6e9495771de17))
- *(tests)* Introduce scheduled_only marker, for tests that should only run on a schedule - ([d5535d9](https://github.com/aignostics/python-sdk/commit/d5535d9fd2ab3cdec3381c0300a6e9495771de17))
- *(tests)* Make now calls make test_default which does not call long_running or very_long_running tests - ([d5535d9](https://github.com/aignostics/python-sdk/commit/d5535d9fd2ab3cdec3381c0300a6e9495771de17))
- *(tests)* Introduce pytest-durations, showing the duration per test execution - ([d5535d9](https://github.com/aignostics/python-sdk/commit/d5535d9fd2ab3cdec3381c0300a6e9495771de17))
- *(tests)* Introduce pytest-timeout, with a low 10s default timeout, and all tests that need longer explicitly marked with specific timeouts - ([d5535d9](https://github.com/aignostics/python-sdk/commit/d5535d9fd2ab3cdec3381c0300a6e9495771de17))
- *(xdist)* Use worksteal to minimize duration on varying test durations - ([d5535d9](https://github.com/aignostics/python-sdk/commit/d5535d9fd2ab3cdec3381c0300a6e9495771de17))
- Don’t allow SDK to be used with Python 1.4.x (released days ago) as some dependencies don’t work with that version yet - ([d5535d9](https://github.com/aignostics/python-sdk/commit/d5535d9fd2ab3cdec3381c0300a6e9495771de17))

### Choare

- *(tests)* No longer test the combination of Python 3.12.x on Windows for ARM64, as a bit instable - ([d5535d9](https://github.com/aignostics/python-sdk/commit/d5535d9fd2ab3cdec3381c0300a6e9495771de17))


# [v0.2.190](https://github.com/aignostics/python-sdk/compare/v0.2.189..v0.2.190) - 2025-10-12

### ⛰️  Features

- *(platform)* Auto-retry when retrieving JWKS set from auth0 - ([6ecb912](https://github.com/aignostics/python-sdk/commit/6ecb91241547c4f3ed800a04a7eafdfc59d79697))
- *(platform)* Cache JWKS set, TTL 24h, minimizing calls to auth0 on validating access tokens - ([6ecb912](https://github.com/aignostics/python-sdk/commit/6ecb91241547c4f3ed800a04a7eafdfc59d79697))
- *(platform)* Auto-retry when calling auth0 to exchange refresh token for access token - ([6ecb912](https://github.com/aignostics/python-sdk/commit/6ecb91241547c4f3ed800a04a7eafdfc59d79697))
- *(platform)* Configurable timeout for requesting platform health - ([6ecb912](https://github.com/aignostics/python-sdk/commit/6ecb91241547c4f3ed800a04a7eafdfc59d79697))
- *(platform)* Introduce authentication aware operation cache - ([6ecb912](https://github.com/aignostics/python-sdk/commit/6ecb91241547c4f3ed800a04a7eafdfc59d79697))
- *(platform)* Use authentication aware operation cache to cache /me result - ([6ecb912](https://github.com/aignostics/python-sdk/commit/6ecb91241547c4f3ed800a04a7eafdfc59d79697))

### 🐛 Bug Fixes

- *(deps)* Update dependency pywin32 to v311 ([#170](https://github.com/orhun/git-cliff/issues/170)) - ([17ee850](https://github.com/aignostics/python-sdk/commit/17ee850b3f073a792cbe60c80488370e69979bed))
- *(platform)* Remove unused setting authorization_backoff_seconds - ([6ecb912](https://github.com/aignostics/python-sdk/commit/6ecb91241547c4f3ed800a04a7eafdfc59d79697))
- *(platform)* Fix wrong exception handler in _perform_device_flow - was catching exception from urllib, not requests lib - ([6ecb912](https://github.com/aignostics/python-sdk/commit/6ecb91241547c4f3ed800a04a7eafdfc59d79697))
- *(platform)* Use dynamic user agent for requesting /me - ([6ecb912](https://github.com/aignostics/python-sdk/commit/6ecb91241547c4f3ed800a04a7eafdfc59d79697))
- *(utils)* Surface setting validation error on misconfigured api root - ([6ecb912](https://github.com/aignostics/python-sdk/commit/6ecb91241547c4f3ed800a04a7eafdfc59d79697))
- Renovate[bot] <29139614+renovate[bot]@users.noreply.github.com> - ([17ee850](https://github.com/aignostics/python-sdk/commit/17ee850b3f073a792cbe60c80488370e69979bed))

### 🚜 Refactor

- *(platform)* Use proper error messages and logging on failure (of attempts) to exchange refresh token and validate access token - ([6ecb912](https://github.com/aignostics/python-sdk/commit/6ecb91241547c4f3ed800a04a7eafdfc59d79697))
- *(platform)* Consistently use HTTPStatus consts instead of 200, 500 etc. - ([6ecb912](https://github.com/aignostics/python-sdk/commit/6ecb91241547c4f3ed800a04a7eafdfc59d79697))
- *(platform)* Use proper constraints on settings - ([6ecb912](https://github.com/aignostics/python-sdk/commit/6ecb91241547c4f3ed800a04a7eafdfc59d79697))
- *(platform,system)* Optimize connection pooling - ([6ecb912](https://github.com/aignostics/python-sdk/commit/6ecb91241547c4f3ed800a04a7eafdfc59d79697))

### 🎨 Styling

- *(utils)* Consistent log formatting for file and console, both including process id - ([6ecb912](https://github.com/aignostics/python-sdk/commit/6ecb91241547c4f3ed800a04a7eafdfc59d79697))

### ⚙️ Miscellaneous Tasks

- *(AI)* Improve Claude actions [skip:ci] - ([e3f6e1c](https://github.com/aignostics/python-sdk/commit/e3f6e1cd1a0e78012178108506a6f33471cccc8a))
- *(ai)* Have Claude Agent use Sonnet 4.5, and allow to create PRs - ([0d4341e](https://github.com/aignostics/python-sdk/commit/0d4341ef167d3c43b05878af23a3d3be8fe8994c))
- *(deps)* Update ghcr.io/astral-sh/uv docker tag to v0.9.1 ([#60](https://github.com/orhun/git-cliff/issues/60)) - ([63423a5](https://github.com/aignostics/python-sdk/commit/63423a542c618b1b39cacf217061399d06706193))
- *(deps)* Update dependency sphinx-toolbox to v4 ([#169](https://github.com/orhun/git-cliff/issues/169)) - ([46456db](https://github.com/aignostics/python-sdk/commit/46456dbd5dce7a0090489e0685d470b31a044594))
- *(gha)* Don't double-build on updates to PR by no longer building on push to branch other than main - ([d3d3d10](https://github.com/aignostics/python-sdk/commit/d3d3d106bee85dff2276a0b3f253bfbdb1a5552f))
- *(gha)* Cancel running build on update to pull request - ([ab9f56d](https://github.com/aignostics/python-sdk/commit/ab9f56d7b801e73fca7ed33af23d9e51a080d276))
- *(gha)* Don't run ci/cd twice on releases: skip:ci on push of commit for release, given already running on (annotated) tag pushed - ([b9c735c](https://github.com/aignostics/python-sdk/commit/b9c735c5ee0bbf282b90b23af94ac6073053dcc7))
- *(pytst)* Add pytest-durations plugin to show durations of fixtures and tests - ([6ecb912](https://github.com/aignostics/python-sdk/commit/6ecb91241547c4f3ed800a04a7eafdfc59d79697))
- Renovate[bot] <29139614+renovate[bot]@users.noreply.github.com> - ([63423a5](https://github.com/aignostics/python-sdk/commit/63423a542c618b1b39cacf217061399d06706193))
- Helmut Hoffer von Ankershoffen né Oertel <helmut@aignostics.com> - ([63423a5](https://github.com/aignostics/python-sdk/commit/63423a542c618b1b39cacf217061399d06706193))


# [v0.2.189](https://github.com/aignostics/python-sdk/compare/v0.2.188..v0.2.189) - 2025-10-05

### ⚙️ Miscellaneous Tasks

- *(qupath)* Give more time in test - ([0a669f9](https://github.com/aignostics/python-sdk/commit/0a669f94be15ff3c34f68abfd48a85d9fa6135ee))


# [v0.2.188](https://github.com/aignostics/python-sdk/compare/v0.2.187..v0.2.188) - 2025-10-05

### 🛡️ Security

- *(gha)* Set permission for generate-matrix, see https://github.com/aignostics/python-sdk/security/code-scanning/15 - ([327c7bc](https://github.com/aignostics/python-sdk/commit/327c7bcb23f51fe5abee56954fae49d85c95cea0))


# [v0.2.187](https://github.com/aignostics/python-sdk/compare/v0.2.186..v0.2.187) - 2025-10-05

### 🛡️ Security

- *(gui)* Introduce html-sanitizer, sanitizer footer. Rest is fine. - ([92adcf7](https://github.com/aignostics/python-sdk/commit/92adcf7d7a85815111cbccc0ce57b95bbad43a1a))


# [v0.2.186](https://github.com/aignostics/python-sdk/compare/v0.2.185..v0.2.186) - 2025-10-05

### 🐛 Bug Fixes

- *(application)* Properly render error if run details cannot be loaded - ([1e01928](https://github.com/aignostics/python-sdk/commit/1e019283cc5ec8ac68adb853d8069e34e6eb29e2))

### ⚙️ Miscellaneous Tasks

- *(application)* More grace in test - ([1e01928](https://github.com/aignostics/python-sdk/commit/1e019283cc5ec8ac68adb853d8069e34e6eb29e2))


# [v0.2.185](https://github.com/aignostics/python-sdk/compare/v0.2.184..v0.2.185) - 2025-10-05

### ⛰️  Features

- *(gui)* Migrate to nicegui 3 - ([d304ef7](https://github.com/aignostics/python-sdk/commit/d304ef721e3c895cc4eb453a55fe69aee6a0c266))

### 🐛 Bug Fixes

- *(dep)* Incompatibility in 3rd party dependency showinfm lead to syntax error in modern Python - now vendored and fixed. - ([d304ef7](https://github.com/aignostics/python-sdk/commit/d304ef721e3c895cc4eb453a55fe69aee6a0c266))

### 🎨 Styling

- *(application)* Better rendering of loading errors - ([d304ef7](https://github.com/aignostics/python-sdk/commit/d304ef721e3c895cc4eb453a55fe69aee6a0c266))

### ⚙️ Miscellaneous Tasks

- *(application)* Made test run sequentially so regular tests now pass without flakiness if platform reliable   - ([d304ef7](https://github.com/aignostics/python-sdk/commit/d304ef721e3c895cc4eb453a55fe69aee6a0c266))


# [v0.2.184](https://github.com/aignostics/python-sdk/compare/v0.2.183..v0.2.184) - 2025-10-05

### 🐛 Bug Fixes

- *(platform)* Get new token if cache entry broken - ([8bbbcf6](https://github.com/aignostics/python-sdk/commit/8bbbcf6e9197e2caf62f1d3254557e947196b502))

### ⚙️ Miscellaneous Tasks

- *(application)* Make test resilient if loading me faster than expected - ([8bbbcf6](https://github.com/aignostics/python-sdk/commit/8bbbcf6e9197e2caf62f1d3254557e947196b502))


# [v0.2.183](https://github.com/aignostics/python-sdk/compare/v0.2.182..v0.2.183) - 2025-10-05

### 🐛 Bug Fixes

- *(platform)* Invalid log formatting - ([483ffe3](https://github.com/aignostics/python-sdk/commit/483ffe3c3b5c065532f44471f55ec438623f9915))

### ⚙️ Miscellaneous Tasks

- *(scheduled)* Print info post sending heartbeat - ([26f0913](https://github.com/aignostics/python-sdk/commit/26f0913a8cfdb6ebf6356f945a89a86622f01294))


# [v0.2.182](https://github.com/aignostics/python-sdk/compare/v0.2.181..v0.2.182) - 2025-10-05

### ⚙️ Miscellaneous Tasks

- *(audit)* Pass betterstack url - ([2599bfb](https://github.com/aignostics/python-sdk/commit/2599bfbf3ccb74713be86e57a62029ed137a37bc))
- *(audit,scheduled)* Warn if betterstack url not configured or not passed through unintentionally - ([2599bfb](https://github.com/aignostics/python-sdk/commit/2599bfbf3ccb74713be86e57a62029ed137a37bc))


# [v0.2.181](https://github.com/aignostics/python-sdk/compare/v0.2.180..v0.2.181) - 2025-10-05

### ⚙️ Miscellaneous Tasks

- *(deps)* Bump - ([53c6469](https://github.com/aignostics/python-sdk/commit/53c6469a9fe894bb91288afa7c8462a5c3e27e40))


# [v0.2.180](https://github.com/aignostics/python-sdk/compare/v0.2.179..v0.2.180) - 2025-10-04

### 🛡️ Security

- *(audit)* No secrets for audit - ([7546e4b](https://github.com/aignostics/python-sdk/commit/7546e4b19d19b82f477ab122bf7b85a9a7bcf591))
- *(dep)* CVE-2025-53354 ignored given we run as desktop app; still started to migrate to nicegui 3 - ([d5c6bee](https://github.com/aignostics/python-sdk/commit/d5c6bee904497661c6a5b90aab6a36751f54c675))


# [v0.2.179](https://github.com/aignostics/python-sdk/compare/v0.2.178..v0.2.179) - 2025-10-03

### 🛡️ Security

- *(gha)* Don't use direct interpolation of user provided data in github workflows - ([2b6d19a](https://github.com/aignostics/python-sdk/commit/2b6d19acb4fc8ba2305a4600253feab92e4474d1))


# [v0.2.178](https://github.com/aignostics/python-sdk/compare/v0.2.177..v0.2.178) - 2025-10-03

### ⚙️ Miscellaneous Tasks

- *(application)* Grace time in test - ([15b1be0](https://github.com/aignostics/python-sdk/commit/15b1be052e6b96198863689dce8d720451eddb70))


# [v0.2.177](https://github.com/aignostics/python-sdk/compare/v0.2.176..v0.2.177) - 2025-10-02

### ⛰️  Features

- *(application)* Allow to copy error message - ([ec0ed63](https://github.com/aignostics/python-sdk/commit/ec0ed6332e7c32357d9a25a749e02604b1312fe5))


# [v0.2.176](https://github.com/aignostics/python-sdk/compare/v0.2.175..v0.2.176) - 2025-10-02

### ⚙️ Miscellaneous Tasks

- Fix pyproject - ([f349a3d](https://github.com/aignostics/python-sdk/commit/f349a3d3f49436122247f80a5de8694af6687fc4))


# [v0.2.175](https://github.com/aignostics/python-sdk/compare/v0.2.174..v0.2.175) - 2025-10-02

### ⚙️ Miscellaneous Tasks

- Release - ([68d5f38](https://github.com/aignostics/python-sdk/commit/68d5f38fead26348965e3fa9c05029fc205d66da))


# [v0.2.174](https://github.com/aignostics/python-sdk/compare/v0.2.173..v0.2.174) - 2025-10-02

### 🐛 Bug Fixes

- *(platform)* Token refresh on long living api client - ([11f46f1](https://github.com/aignostics/python-sdk/commit/11f46f14b4696b4303357d497f826480198ccc05))



* @akunft made their first contribution

# [v0.2.173](https://github.com/aignostics/python-sdk/compare/v0.2.172..v0.2.173) - 2025-10-02

### 🚜 Refactor

- *(platform,application)* Establish sdk subtree within custom metadata for contract with other sdks and apps - ([560cbb8](https://github.com/aignostics/python-sdk/commit/560cbb88203b737848a5fbde550235979b753d71))


# [v0.2.172](https://github.com/aignostics/python-sdk/compare/v0.2.171..v0.2.172) - 2025-10-02

### 🎨 Styling

- *(application)* More prominent placement of per item message - ([c9cb8ee](https://github.com/aignostics/python-sdk/commit/c9cb8eeae9b08131fcf0548ef4a0abd723556512))


# [v0.2.171](https://github.com/aignostics/python-sdk/compare/v0.2.170..v0.2.171) - 2025-10-02

### ⚙️ Miscellaneous Tasks

- *(application)* Grace for cancel button to appear in test - ([893083c](https://github.com/aignostics/python-sdk/commit/893083c7c5ca283d0aee45371a01d7ba335ee893))


# [v0.2.170](https://github.com/aignostics/python-sdk/compare/v0.2.169..v0.2.170) - 2025-10-01

### ⚙️ Miscellaneous Tasks

- *(application)* More time for test - ([343f78c](https://github.com/aignostics/python-sdk/commit/343f78caba9629d1683bf43419c12a7d6c399d53))


# [v0.2.169](https://github.com/aignostics/python-sdk/compare/v0.2.168..v0.2.169) - 2025-10-01

### ⛰️  Features

- *(application)* Show duration, terminated at, run and item-level message ([#143](https://github.com/orhun/git-cliff/issues/143)) - ([0dc484e](https://github.com/aignostics/python-sdk/commit/0dc484e9e97c674b4468638afd82513e81f2ee4d))


# [v0.2.168](https://github.com/aignostics/python-sdk/compare/v0.2.167..v0.2.168) - 2025-10-01

### ⛰️  Features

- *(application)* Allow to set note on run submission, and retrieve on run describe - ([c5175cb](https://github.com/aignostics/python-sdk/commit/c5175cbf32cfcb5682bb5c80206534879c3a7754))
- *(application)* Allow live search of runs by note - ([c5175cb](https://github.com/aignostics/python-sdk/commit/c5175cbf32cfcb5682bb5c80206534879c3a7754))
- *(application)* Allow to flag to onboard to Aignostics Portal - ([c5175cb](https://github.com/aignostics/python-sdk/commit/c5175cbf32cfcb5682bb5c80206534879c3a7754))
- *(platform)* Adapt to breaking changes in Platform API 1.0.0-beta6 - ([c5175cb](https://github.com/aignostics/python-sdk/commit/c5175cbf32cfcb5682bb5c80206534879c3a7754))
- *(platform,application)* Support custom metadata attached to runs - ([c5175cb](https://github.com/aignostics/python-sdk/commit/c5175cbf32cfcb5682bb5c80206534879c3a7754))
- *(utils)* Generate dynamic user agent including version, build number, os, and test calling - ([c5175cb](https://github.com/aignostics/python-sdk/commit/c5175cbf32cfcb5682bb5c80206534879c3a7754))
- API v1.0.0-beta.6 ([#141](https://github.com/orhun/git-cliff/issues/141)) - ([c5175cb](https://github.com/aignostics/python-sdk/commit/c5175cbf32cfcb5682bb5c80206534879c3a7754))
- Use dynamic user agent in http requests and run submissions via custom metadata - ([c5175cb](https://github.com/aignostics/python-sdk/commit/c5175cbf32cfcb5682bb5c80206534879c3a7754))

### 🐛 Bug Fixes

- *(application)* Don't show extra column in meta edit - ([c5175cb](https://github.com/aignostics/python-sdk/commit/c5175cbf32cfcb5682bb5c80206534879c3a7754))
- *(wsi)* Don't fail on log on broken tiff test - ([c5175cb](https://github.com/aignostics/python-sdk/commit/c5175cbf32cfcb5682bb5c80206534879c3a7754))
- Fix typo in log message caught by claude code review - ([c5175cb](https://github.com/aignostics/python-sdk/commit/c5175cbf32cfcb5682bb5c80206534879c3a7754))

### 🚜 Refactor

- *(application)* Load applications in left sidebar in thread to not block UI - ([c5175cb](https://github.com/aignostics/python-sdk/commit/c5175cbf32cfcb5682bb5c80206534879c3a7754))

### ⚙️ Miscellaneous Tasks

- *(codegen)* Download and archive openapi.json - ([c5175cb](https://github.com/aignostics/python-sdk/commit/c5175cbf32cfcb5682bb5c80206534879c3a7754))
- *(deps)* Bump - ([c5175cb](https://github.com/aignostics/python-sdk/commit/c5175cbf32cfcb5682bb5c80206534879c3a7754))

### 🛡️ Security

- *(dep)* Pip, CVE-2025-54368 - ([c5175cb](https://github.com/aignostics/python-sdk/commit/c5175cbf32cfcb5682bb5c80206534879c3a7754))
- *(gha)* Security improvements in github workflow as identified by sonarqube - ([c5175cb](https://github.com/aignostics/python-sdk/commit/c5175cbf32cfcb5682bb5c80206534879c3a7754))


# [v0.2.167](https://github.com/aignostics/python-sdk/compare/v0.2.166..v0.2.167) - 2025-09-30

### ⚙️ Miscellaneous Tasks

- *(application)* Adapt tests to asynchronous loading of apps in GUI - ([6a2e27b](https://github.com/aignostics/python-sdk/commit/6a2e27bd032cd69a7769ff706a4c2ced2ba6567a))


# [v0.2.166](https://github.com/aignostics/python-sdk/compare/v0.2.165..v0.2.166) - 2025-09-30

### 🚜 Refactor

- *(application)* Load applications in left sidebar in thread to not block UI - ([cc25061](https://github.com/aignostics/python-sdk/commit/cc25061e62649a25f4e9f34c356010f9591dd0bd))

### 🛡️ Security

- *(GHA)* Apply security best practices for GitHub Workflows ([#139](https://github.com/orhun/git-cliff/issues/139)) - ([5c3d3f2](https://github.com/aignostics/python-sdk/commit/5c3d3f2f29ea1e3d51a6a1d7b00faa08cd78e2dd))
- *(gha)* Security improvements in github workflow as identified by sonarqube - ([5c3d3f2](https://github.com/aignostics/python-sdk/commit/5c3d3f2f29ea1e3d51a6a1d7b00faa08cd78e2dd))


# [v0.2.165](https://github.com/aignostics/python-sdk/compare/v0.2.164..v0.2.165) - 2025-09-29

### ⚙️ Miscellaneous Tasks

- *(wsi)* Don't fail test on log on broken tiff test - ([44de674](https://github.com/aignostics/python-sdk/commit/44de6745f3d3bd86f179092511e222ac6d3c812f))


# [v0.2.164](https://github.com/aignostics/python-sdk/compare/v0.2.163..v0.2.164) - 2025-09-29

### ⚙️ Miscellaneous Tasks

- *(gha)* Bump login-action in claude and docker workflows - ([3180352](https://github.com/aignostics/python-sdk/commit/3180352e51591d9d9731f2fd06f93cf68111b42c))


# [v0.2.163](https://github.com/aignostics/python-sdk/compare/v0.2.161..v0.2.163) - 2025-09-29

### 🐛 Bug Fixes

- *(dataset)* Custom download folder selection - ([4b59607](https://github.com/aignostics/python-sdk/commit/4b5960743849bc3873fd6a5f185463f5e76a7e13))

### ⚙️ Miscellaneous Tasks

- *(AI)* Claude.md files for assisted coding - ([25ee505](https://github.com/aignostics/python-sdk/commit/25ee505f009bd9d4b0e482019851b4914024bec6))
- *(GHA)* Claude PR Assistant workflow - ([25ee505](https://github.com/aignostics/python-sdk/commit/25ee505f009bd9d4b0e482019851b4914024bec6))
- Chore(GHA) Claude Code Review workflow - ([25ee505](https://github.com/aignostics/python-sdk/commit/25ee505f009bd9d4b0e482019851b4914024bec6))


# [v0.2.161](https://github.com/aignostics/python-sdk/compare/v0.2.160..v0.2.161) - 2025-09-28

### 🐛 Bug Fixes

- *(dataset)* Custom download folder selection - ([290ce5b](https://github.com/aignostics/python-sdk/commit/290ce5bcc2be44fb87ef868d5f06404cf1f699b5))


# [v0.2.160](https://github.com/aignostics/python-sdk/compare/v0.2.159..v0.2.160) - 2025-09-28

### 🚜 Refactor

- *(io)* Don't use synchronous fileio in async functions - ([e4a82bd](https://github.com/aignostics/python-sdk/commit/e4a82bdc1551dcfd212f483e85a1b094559d4db1))
- *(lint)* New ruff rules - ([472258c](https://github.com/aignostics/python-sdk/commit/472258ca9460d62dfb4be1a8243f74193510e62e))

### 📚 Documentation

- *(claude)* Claude.md - ([2ad9555](https://github.com/aignostics/python-sdk/commit/2ad95557e4121edd968f711feee52c475487130a))

### ⚙️ Miscellaneous Tasks

- *(deps)* Bump - ([93d097d](https://github.com/aignostics/python-sdk/commit/93d097d496aa9aa3f8ab52ffa7d9c99aa723ff66))

### 🛡️ Security

- *(jupyterlab)* CVE-2025-59842 - ([6081c74](https://github.com/aignostics/python-sdk/commit/6081c74a96d859685bdc2b684ebc4994475b84e1))


# [v0.2.159](https://github.com/aignostics/python-sdk/compare/v0.2.158..v0.2.159) - 2025-09-20

### 🎨 Styling

- *(changelog)* Improve styling of release notes - ([3f25caf](https://github.com/aignostics/python-sdk/commit/3f25caf3c837c2bb4860cf7339d52d7554007e57))


# [v0.2.158](https://github.com/aignostics/python-sdk/compare/v0.2.157..v0.2.158) - 2025-09-20

### 🐛 Bug Fixes

- *(system)* Disable cpu freq on gha macos latest runner given not supported - ([861af87](https://github.com/aignostics/python-sdk/commit/861af873a5f4eca40e9dac11f17192ab4355ef40))

### 🚜 Refactor

- *(platform)* Rename run delete to run result delete - ([861af87](https://github.com/aignostics/python-sdk/commit/861af873a5f4eca40e9dac11f17192ab4355ef40))

### ⚙️ Miscellaneous Tasks

- *(changelog)* Introduce .cliffignore to prune changelog for maintenance commits - ([f7df80e](https://github.com/aignostics/python-sdk/commit/f7df80e535f9942c0e8adc801d7c48b2bc58ff52))
- *(deps)* Bump dependencies - ([861af87](https://github.com/aignostics/python-sdk/commit/861af873a5f4eca40e9dac11f17192ab4355ef40))
- *(docs)* Make - ([f73975c](https://github.com/aignostics/python-sdk/commit/f73975c98a27897b2758f736710e1989aed0e635))
- *(gha)* Re-enable tests for releases - ([861af87](https://github.com/aignostics/python-sdk/commit/861af873a5f4eca40e9dac11f17192ab4355ef40))


# [v0.2.157](https://github.com/aignostics/python-sdk/compare/v0.2.156..v0.2.157) - 2025-09-17

### ⚙️ Miscellaneous Tasks

- Skip:test:all - ([2cf18ff](https://github.com/aignostics/python-sdk/commit/2cf18ffad302466509736c5d3a8c71b0409d4945))


# [v0.2.156](https://github.com/aignostics/python-sdk/compare/v0.2.155..v0.2.156) - 2025-09-17

### ⚙️ Miscellaneous Tasks

- Skip:test:all - ([a77f7b9](https://github.com/aignostics/python-sdk/commit/a77f7b9c3928263d79a795ae38cab3c6c25bf95f))


# [v0.2.155](https://github.com/aignostics/python-sdk/compare/v0.2.154..v0.2.155) - 2025-09-17

### ⚙️ Miscellaneous Tasks

- Skip tests on release - ([595703d](https://github.com/aignostics/python-sdk/commit/595703dc228478f09a2cfe16ec3c6fdc546b6163))


# [v0.2.154](https://github.com/aignostics/python-sdk/compare/v0.2.153..v0.2.154) - 2025-09-17

### 🐛 Bug Fixes

- Update the input artifact name for HETA to whole_slide_image ([#121](https://github.com/orhun/git-cliff/issues/121)) - ([6ed1e27](https://github.com/aignostics/python-sdk/commit/6ed1e270d1a387c887d286fcab2cd8bb200eff25))

### 📚 Documentation

- Update - ([d5f3379](https://github.com/aignostics/python-sdk/commit/d5f3379e06656a06f02610f789ba46cb9dfeedfb))



* @jstriebel made their first contribution

# [v0.2.153](https://github.com/aignostics/python-sdk/compare/v0.2.152..v0.2.153) - 2025-08-18

### ⚙️ Miscellaneous Tasks

- *(gha)* Add final smoke test before publish - ([2c9598e](https://github.com/aignostics/python-sdk/commit/2c9598e1be057e0b5889b3a5b6b348c229699777))


# [v0.2.152](https://github.com/aignostics/python-sdk/compare/v0.2.151..v0.2.152) - 2025-08-17

### ⛰️  Features

- *(core)* Support Windows on ARM - ([89a3c4a](https://github.com/aignostics/python-sdk/commit/89a3c4a4c761fbac036e3c8e400fa8b271fe437d))

### 🚜 Refactor

- *(native)* Compress native installation using UPX on Windows - ([89a3c4a](https://github.com/aignostics/python-sdk/commit/89a3c4a4c761fbac036e3c8e400fa8b271fe437d))


# [v0.2.151](https://github.com/aignostics/python-sdk/compare/v0.2.150..v0.2.151) - 2025-08-17

### ⛰️  Features

- *(networking)* Support system truststore for ssl trust chain [no:ci] ([#92](https://github.com/orhun/git-cliff/issues/92)) - ([aad4e76](https://github.com/aignostics/python-sdk/commit/aad4e76e83d489275b3d09e8e887d79a1af2d514))


# [v0.2.150](https://github.com/aignostics/python-sdk/compare/v0.2.149..v0.2.150) - 2025-08-17

### ⛰️  Features

- *(native)* Show progress on splash screen ([#91](https://github.com/orhun/git-cliff/issues/91)) - ([e667252](https://github.com/aignostics/python-sdk/commit/e6672526210d0e397267af1059482a8ed434065b))


# [v0.2.149](https://github.com/aignostics/python-sdk/compare/v0.2.148..v0.2.149) - 2025-08-17

### 🚜 Refactor

- Linter - ([943b9f9](https://github.com/aignostics/python-sdk/commit/943b9f97f8507d6d2534d8a1af801a8b6d453b7a))


# [v0.2.148](https://github.com/aignostics/python-sdk/compare/v0.2.147..v0.2.148) - 2025-08-17

### ⛰️  Features

- *(native)* Splash screen for Windows and Linux ([#90](https://github.com/orhun/git-cliff/issues/90)) - ([8fc82cd](https://github.com/aignostics/python-sdk/commit/8fc82cded615d9d18da799a92e525ecd6c81c42f))

### ⚙️ Miscellaneous Tasks

- *(native)* Rfc [build:native:only] - ([8fc82cd](https://github.com/aignostics/python-sdk/commit/8fc82cded615d9d18da799a92e525ecd6c81c42f))
- *(native)* Splash screen on windows and linux build:native:only - ([8fc82cd](https://github.com/aignostics/python-sdk/commit/8fc82cded615d9d18da799a92e525ecd6c81c42f))
- *(native)* Use python 3.13.7 - ([8fc82cd](https://github.com/aignostics/python-sdk/commit/8fc82cded615d9d18da799a92e525ecd6c81c42f))
- *(python)* 3.13.6 - ([29f2884](https://github.com/aignostics/python-sdk/commit/29f28847086e4dc76e65c17cb36db6bea46add6a))


# [v0.2.147](https://github.com/aignostics/python-sdk/compare/v0.2.146..v0.2.147) - 2025-08-16

### ⚙️ Miscellaneous Tasks

- *(docker)* Bump to python 3.13 and latest uv - ([f26e880](https://github.com/aignostics/python-sdk/commit/f26e880465af120ef0e1dc351bffd6fb616631ce))


# [v0.2.146](https://github.com/aignostics/python-sdk/compare/v0.2.145..v0.2.146) - 2025-08-16

### 🚜 Refactor

- *(native)* Use archive; optimize - ([127a88d](https://github.com/aignostics/python-sdk/commit/127a88dd30fd480b01b5ecb47ede9f29f80f617b))


# [v0.2.145](https://github.com/aignostics/python-sdk/compare/v0.2.144..v0.2.145) - 2025-08-16

### ⚙️ Miscellaneous Tasks

- *(deps)* Bump in GHA and Dockerfile - ([3c847aa](https://github.com/aignostics/python-sdk/commit/3c847aad1017b0736415203080ea16bfe5a37281))


# [v0.2.144](https://github.com/aignostics/python-sdk/compare/v0.2.143..v0.2.144) - 2025-08-16

### 🐛 Bug Fixes

- *(native)* Windows - ([28b1010](https://github.com/aignostics/python-sdk/commit/28b10104b02488b588224fcb52653f953c882d22))

### ⚙️ Miscellaneous Tasks

- *(deps)* Bump - ([28b1010](https://github.com/aignostics/python-sdk/commit/28b10104b02488b588224fcb52653f953c882d22))
- *(gha)* Allow to build:native:only ([#89](https://github.com/orhun/git-cliff/issues/89)) - ([28b1010](https://github.com/aignostics/python-sdk/commit/28b10104b02488b588224fcb52653f953c882d22))


# [v0.2.143](https://github.com/aignostics/python-sdk/compare/v0.2.142..v0.2.143) - 2025-08-16

### ⛰️  Features

- *(application, platform)* Allow to delete run. Note: currently broken in Samia - ([38c6554](https://github.com/aignostics/python-sdk/commit/38c6554add3fbfe17093a2ae007914996e064c8a))
- *(native)* Show being native in footer of launchpad - ([9b0a4d5](https://github.com/aignostics/python-sdk/commit/9b0a4d58ad1be62d727efb2765b3205f90121bf8))

### 🚜 Refactor

- *(native)* Don't include dev dependencies - ([9b0a4d5](https://github.com/aignostics/python-sdk/commit/9b0a4d58ad1be62d727efb2765b3205f90121bf8))

### ⚙️ Miscellaneous Tasks

- *(application)* Adapt test for delete cli - ([9b0a4d5](https://github.com/aignostics/python-sdk/commit/9b0a4d58ad1be62d727efb2765b3205f90121bf8))


# [v0.2.142](https://github.com/aignostics/python-sdk/compare/v0.2.141..v0.2.142) - 2025-08-15

### 🐛 Bug Fixes

- *(native)* Marimo integration - ([9f01ef6](https://github.com/aignostics/python-sdk/commit/9f01ef644f5e2302b54306ecb1ebf14a062d60ad))


# [v0.2.141](https://github.com/aignostics/python-sdk/compare/v0.2.140..v0.2.141) - 2025-08-15

### 🐛 Bug Fixes

- *(native)* Marimo - ([5911d74](https://github.com/aignostics/python-sdk/commit/5911d74c279dd215c2ce51f8b0b6c294fa5d2831))


# [v0.2.140](https://github.com/aignostics/python-sdk/compare/v0.2.139..v0.2.140) - 2025-08-14

### ⚙️ Miscellaneous Tasks

- *(gha)* Re-enable tests - ([85e98e3](https://github.com/aignostics/python-sdk/commit/85e98e37b8dab7bad0af3e2fa4faa35452d26dd3))


# [v0.2.139](https://github.com/aignostics/python-sdk/compare/v0.2.138..v0.2.139) - 2025-08-13

### 🐛 Bug Fixes

- *(ssl)* Use certifi as fallback if configured intermediate certificates not found, and no env override - ([157d2b7](https://github.com/aignostics/python-sdk/commit/157d2b717d4045e2b2fcc012dda86acaac4c30df))


# [v0.2.138](https://github.com/aignostics/python-sdk/compare/v0.2.137..v0.2.138) - 2025-08-13

### 🐛 Bug Fixes

- *(native)* Use certifi bundle if default bundle not found - ([f10e249](https://github.com/aignostics/python-sdk/commit/f10e249848b968dee04317dfe5a5700f0768cd15))


# [v0.2.137](https://github.com/aignostics/python-sdk/compare/v0.2.136..v0.2.137) - 2025-08-13

### ⚙️ Miscellaneous Tasks

- *(debug)* Temp disable of tests - ([2275ec5](https://github.com/aignostics/python-sdk/commit/2275ec5833f0c2d753040e15d4fd396c7e12ad91))


# [v0.2.136](https://github.com/aignostics/python-sdk/compare/v0.2.135..v0.2.136) - 2025-08-13

### ⚙️ Miscellaneous Tasks

- *(debug)* Temp disable of tests - ([0185f35](https://github.com/aignostics/python-sdk/commit/0185f35e83800bc357eafb17bd140e17b770618f))


# [v0.2.135](https://github.com/aignostics/python-sdk/compare/v0.2.134..v0.2.135) - 2025-08-13

### ⚙️ Miscellaneous Tasks

- *(debug)* Temp disable of tests - ([1214a9e](https://github.com/aignostics/python-sdk/commit/1214a9e1498306bb066aac84a0ef0450bef03172))


# [v0.2.134](https://github.com/aignostics/python-sdk/compare/v0.2.133..v0.2.134) - 2025-08-13

### ⚙️ Miscellaneous Tasks

- *(debug)* Temp disable of tests - ([adaf4eb](https://github.com/aignostics/python-sdk/commit/adaf4eb6c0c1e70d54dd08db528f3097cddcf314))


# [v0.2.133](https://github.com/aignostics/python-sdk/compare/v0.2.132..v0.2.133) - 2025-08-12

### ⛰️  Features

- *(application)* Show run id in collapsible so it can be copied - ([d7c597a](https://github.com/aignostics/python-sdk/commit/d7c597a70a398c951a8c17b96e33952a821c82ba))


# [v0.2.132](https://github.com/aignostics/python-sdk/compare/v0.2.131..v0.2.132) - 2025-08-12

### 🎨 Styling

- *(lint)* Fix linting error in native starter - ([2552ac7](https://github.com/aignostics/python-sdk/commit/2552ac76b1aa36a8aae325e511ffcd4c4d1c4f3a))

### ⚙️ Miscellaneous Tasks

- Chore(deps); bump dev dependencies - ([2552ac7](https://github.com/aignostics/python-sdk/commit/2552ac76b1aa36a8aae325e511ffcd4c4d1c4f3a))


# [v0.2.131](https://github.com/aignostics/python-sdk/compare/v0.2.130..v0.2.131) - 2025-08-12

### 🐛 Bug Fixes

- *(native)* Use system trust store for SSL certificates - ([168a7d7](https://github.com/aignostics/python-sdk/commit/168a7d7509053855f7f8537f6a82ba52c943e11b))

### ⚙️ Miscellaneous Tasks

- *(deps)* Bump deps - ([168a7d7](https://github.com/aignostics/python-sdk/commit/168a7d7509053855f7f8537f6a82ba52c943e11b))


# [v0.2.130](https://github.com/aignostics/python-sdk/compare/v0.2.129..v0.2.130) - 2025-08-12

### ⛰️  Features

- *(native)* Debug command - ([433a803](https://github.com/aignostics/python-sdk/commit/433a803310915e355d4b3c4fe1ffd04f5509c278))


# [v0.2.129](https://github.com/aignostics/python-sdk/compare/v0.2.128..v0.2.129) - 2025-08-12

### 🐛 Bug Fixes

- *(native)* Dataset download - openslide libs were not bundled by pyinstaller - ([9ff1453](https://github.com/aignostics/python-sdk/commit/9ff1453ce17170e84634ef1ae1c8d15dd659bec0))
- *(native)* Thumbnail generation on submission - script execution complexity - ([9ff1453](https://github.com/aignostics/python-sdk/commit/9ff1453ce17170e84634ef1ae1c8d15dd659bec0))

### ⚙️ Miscellaneous Tasks

- *(deps)* Bump nicegui, boto - ([9ff1453](https://github.com/aignostics/python-sdk/commit/9ff1453ce17170e84634ef1ae1c8d15dd659bec0))


# [v0.2.128](https://github.com/aignostics/python-sdk/compare/v0.2.127..v0.2.128) - 2025-08-11

### 🐛 Bug Fixes

- *(native)* Bundle openslide native libs - ([164d43e](https://github.com/aignostics/python-sdk/commit/164d43e54a0380d31672070bce4d411dd6f3e371))


# [v0.2.127](https://github.com/aignostics/python-sdk/compare/v0.2.126..v0.2.127) - 2025-08-11

### 🐛 Bug Fixes

- *(native)* Include s5cmd binary in native distribution - ([e35303a](https://github.com/aignostics/python-sdk/commit/e35303a995886a9e3817f7097f1a84d0b37b9a18))


# [v0.2.126](https://github.com/aignostics/python-sdk/compare/v0.2.125..v0.2.126) - 2025-08-11

### ⚙️ Miscellaneous Tasks

- *(slack)* Convert release notes to JSON rep. for posting to slack - ([4d328e1](https://github.com/aignostics/python-sdk/commit/4d328e179b76608d27087aeb9cf6f27229e33ac8))


# [v0.2.125](https://github.com/aignostics/python-sdk/compare/v0.2.124..v0.2.125) - 2025-08-11

### ⚙️ Miscellaneous Tasks

- *(qupath)* Test - ([5377012](https://github.com/aignostics/python-sdk/commit/53770124be325b40c90d3a3ce4c9e8ddb9af4ba1))


# [v0.2.124](https://github.com/aignostics/python-sdk/compare/v0.2.123..v0.2.124) - 2025-08-11

### ⚙️ Miscellaneous Tasks

- *(qupath)* Test - ([2126bb9](https://github.com/aignostics/python-sdk/commit/2126bb919bcb51dda4ae58aeb79051d962a46bb0))


# [v0.2.123](https://github.com/aignostics/python-sdk/compare/v0.2.122..v0.2.123) - 2025-08-10

### ⚙️ Miscellaneous Tasks

- *(qupath)* Skip test step temporarily - ([e8df7e0](https://github.com/aignostics/python-sdk/commit/e8df7e02d6fb38ee406ceebac24fc99cee440ad3))


# [v0.2.122](https://github.com/aignostics/python-sdk/compare/v0.2.121..v0.2.122) - 2025-08-10

### ⚙️ Miscellaneous Tasks

- *(qupath)* More time for test - ([5624347](https://github.com/aignostics/python-sdk/commit/5624347f7dd8b026af28c685f6dba0433386887f))


# [v0.2.121](https://github.com/aignostics/python-sdk/compare/v0.2.120..v0.2.121) - 2025-08-10

### ⛰️  Features

- *(gui)* Custom error page showing traceback and allowing to close app even in non-chrome mode - ([ee47197](https://github.com/aignostics/python-sdk/commit/ee47197ad8cf27f6789df743e9f553a8c2179605))


# [v0.2.120](https://github.com/aignostics/python-sdk/compare/v0.2.119..v0.2.120) - 2025-08-10

### 🐛 Bug Fixes

- *(notebook)* Revert timeout - ([9b7c1c3](https://github.com/aignostics/python-sdk/commit/9b7c1c3e5331ce2d627492319b8e9a5f5a65daa5))


# [v0.2.119](https://github.com/aignostics/python-sdk/compare/v0.2.118..v0.2.119) - 2025-08-10

### 🐛 Bug Fixes

- *(native)* Add_docstring issue caused by inconsistent optimization on analysis and exe building - ([066a198](https://github.com/aignostics/python-sdk/commit/066a1988179cabd3ffd1268aa746e13da0747079))


# [v0.2.118](https://github.com/aignostics/python-sdk/compare/v0.2.117..v0.2.118) - 2025-08-10

### ⚙️ Miscellaneous Tasks

- *(notebook)* Adapt to refactoring - ([4e8e595](https://github.com/aignostics/python-sdk/commit/4e8e5958e071315b61f2fbaedc6595377414cd5d))


# [v0.2.117](https://github.com/aignostics/python-sdk/compare/v0.2.116..v0.2.117) - 2025-08-10

### 🐛 Bug Fixes

- *(notebook)* Navigation to marimo - ([af5e84e](https://github.com/aignostics/python-sdk/commit/af5e84e2548f5e9f10cfd0d1b4814bc9764b76cd))

### ⚙️ Miscellaneous Tasks

- *(notebook)* Adapt test - ([371bf69](https://github.com/aignostics/python-sdk/commit/371bf69e9a334028af52bcce757d8bb0796288fb))


# [v0.2.116](https://github.com/aignostics/python-sdk/compare/v0.2.115..v0.2.116) - 2025-08-09

### 🚜 Refactor

- *(notebook)* Simplify open marimo button - ([26c9d1b](https://github.com/aignostics/python-sdk/commit/26c9d1b2d8876e5de3ae31dcd663f5050daff387))

### ⚙️ Miscellaneous Tasks

- *(bucket)* Better logging for flaky test - ([26c9d1b](https://github.com/aignostics/python-sdk/commit/26c9d1b2d8876e5de3ae31dcd663f5050daff387))


# [v0.2.115](https://github.com/aignostics/python-sdk/compare/v0.2.114..v0.2.115) - 2025-08-09

### ⚙️ Miscellaneous Tasks

- *(bucket)* More time for download test - ([be2d31f](https://github.com/aignostics/python-sdk/commit/be2d31fc1743a1e4c69822a3f082163bec8d25ca))


# [v0.2.114](https://github.com/aignostics/python-sdk/compare/v0.2.113..v0.2.114) - 2025-08-09

### ⚙️ Miscellaneous Tasks

- *(notebook)* Cannot in parallel test multiple marimo servers on same host with no isolation - ([d8b92af](https://github.com/aignostics/python-sdk/commit/d8b92af4ea79d808b9699377dc47142546264a8b))


# [v0.2.113](https://github.com/aignostics/python-sdk/compare/v0.2.112..v0.2.113) - 2025-08-09

### 🐛 Bug Fixes

- *(bucket)* In GUI use static version of download operation offered by service - ([db2b5f5](https://github.com/aignostics/python-sdk/commit/db2b5f514f66c6a0dc411bf6dda721c2a668d364))

### ⚙️ Miscellaneous Tasks

- *(audit)* Audit reports part of release artifacts - ([db2b5f5](https://github.com/aignostics/python-sdk/commit/db2b5f514f66c6a0dc411bf6dda721c2a668d364))
- *(deps)* Bump - ([db2b5f5](https://github.com/aignostics/python-sdk/commit/db2b5f514f66c6a0dc411bf6dda721c2a668d364))
- *(pytest)* Show recent notifications if asserted one not found - ([db2b5f5](https://github.com/aignostics/python-sdk/commit/db2b5f514f66c6a0dc411bf6dda721c2a668d364))
- *(release)* Announce release on internal Slack (experimental) - ([db2b5f5](https://github.com/aignostics/python-sdk/commit/db2b5f514f66c6a0dc411bf6dda721c2a668d364))
- *(test)* Don't provide log as job artifact - ([db2b5f5](https://github.com/aignostics/python-sdk/commit/db2b5f514f66c6a0dc411bf6dda721c2a668d364))

### 🛡️ Security

- *(uv)* Use uv > 0.8.6 in pre-commit hook - ([db2b5f5](https://github.com/aignostics/python-sdk/commit/db2b5f514f66c6a0dc411bf6dda721c2a668d364))


# [v0.2.112](https://github.com/aignostics/python-sdk/compare/v0.2.111..v0.2.112) - 2025-08-08

### ⚙️ Miscellaneous Tasks

- *(heta)* Adapt tests - ([2e6b72f](https://github.com/aignostics/python-sdk/commit/2e6b72ffeef78751b51d4bf8897a64658ae0c250))


# [v0.2.111](https://github.com/aignostics/python-sdk/compare/v0.2.110..v0.2.111) - 2025-08-08

### 🚜 Refactor

- *(uv)* Define required uv version in pyproject.toml, for use across GHA - ([7e1610e](https://github.com/aignostics/python-sdk/commit/7e1610e604f4f2ddb1fd6da3448f5731958565ee))

### ⚙️ Miscellaneous Tasks

- *(deps)* Bump - ([6f942ee](https://github.com/aignostics/python-sdk/commit/6f942ee5d6f70d0b1b697473a703093110503d51))
- *(deps)* Bump various github actions versions - ([7e1610e](https://github.com/aignostics/python-sdk/commit/7e1610e604f4f2ddb1fd6da3448f5731958565ee))
- *(heta)* Further adaptation to changed output file sizes - ([6f942ee](https://github.com/aignostics/python-sdk/commit/6f942ee5d6f70d0b1b697473a703093110503d51))

### 🛡️ Security

- *(dep)* Ensure all uses of uv are >= 0.8.6 (CVE-2025-54368) - ([7e1610e](https://github.com/aignostics/python-sdk/commit/7e1610e604f4f2ddb1fd6da3448f5731958565ee))


# [v0.2.110](https://github.com/aignostics/python-sdk/compare/v0.2.109..v0.2.110) - 2025-08-08

### 🚜 Refactor

- *(tests)* Central place for app id and version - ([5bcc685](https://github.com/aignostics/python-sdk/commit/5bcc685d2d7de98777673a4623fd1b7abfb9b3fd))
- *(tests)* Central constants for app and app version id to simplify adapting to new apps - ([3fc5730](https://github.com/aignostics/python-sdk/commit/3fc5730294588534ad6e57d2302dfa7d28dec8e0))

### ⚙️ Miscellaneous Tasks

- *(tests)* Adapt to heta.5 - ([06f6867](https://github.com/aignostics/python-sdk/commit/06f6867953d6131ad0f26db4cedaabe28eb62a23))

### 🛡️ Security

- *(dep)* Force UV >0.8.6 given CVE-2025-54368 - ([ef2cb54](https://github.com/aignostics/python-sdk/commit/ef2cb540e03cc49d15371ccb6a0ca8b1447a894e))


# [v0.2.109](https://github.com/aignostics/python-sdk/compare/v0.2.108..v0.2.109) - 2025-08-07


# [v0.2.108](https://github.com/aignostics/python-sdk/compare/v0.2.107..v0.2.108) - 2025-08-07

### ⚙️ Miscellaneous Tasks

- *(test)* Adapt remaining test config to beta.5 of heta - ([b152fae](https://github.com/aignostics/python-sdk/commit/b152fae64995f0208207d8719cfefd166961c1b0))


# [v0.2.107](https://github.com/aignostics/python-sdk/compare/v0.2.106..v0.2.107) - 2025-08-07

### ⛰️  Features

- *(codegen, platform)* Support me endpoint ([#81](https://github.com/orhun/git-cliff/issues/81)) - ([7d74a2b](https://github.com/aignostics/python-sdk/commit/7d74a2b334512bd69df5aed460ee160263f10cda))
- Allow to boot with zero config, i.e. no .env file required in default case - ([7d74a2b](https://github.com/aignostics/python-sdk/commit/7d74a2b334512bd69df5aed460ee160263f10cda))

### 🐛 Bug Fixes

- *(codegen)* Don't rely on redirects from /v1 to /api/v1 - ([7d74a2b](https://github.com/aignostics/python-sdk/commit/7d74a2b334512bd69df5aed460ee160263f10cda))
- *(platform)* Allow to dial into dev environment - ([7d74a2b](https://github.com/aignostics/python-sdk/commit/7d74a2b334512bd69df5aed460ee160263f10cda))
- Fix typos in readme.md - ([ef4d8f6](https://github.com/aignostics/python-sdk/commit/ef4d8f6ea74ee8b861cd9d2cf20dd342d7b3165e))

### ⚙️ Miscellaneous Tasks

- *(deps)* Bump nicegui - ([1b6fa5e](https://github.com/aignostics/python-sdk/commit/1b6fa5e0e153cd6e590448fce51876640581436e))
- *(deps)* Bump - ([7d74a2b](https://github.com/aignostics/python-sdk/commit/7d74a2b334512bd69df5aed460ee160263f10cda))
- *(heta)* Adapt tests to 1.0.0-beta.5 of HETA - ([7d74a2b](https://github.com/aignostics/python-sdk/commit/7d74a2b334512bd69df5aed460ee160263f10cda))



* @omid-aignostics made their first contribution

# [v0.2.106](https://github.com/aignostics/python-sdk/compare/v0.2.105..v0.2.106) - 2025-07-22

### ⚙️ Miscellaneous Tasks

- *(audit)* Allow for heartbeat url specific for audit - ([49f35a0](https://github.com/aignostics/python-sdk/commit/49f35a0210d9d115c1ebc94b18b221d24bc4008e))
- *(publish)* Adapt to recent changes - ([5b0150a](https://github.com/aignostics/python-sdk/commit/5b0150accf20926e768fd6a46fad344ae013ea12))


# [v0.2.105](https://github.com/aignostics/python-sdk/compare/v0.2.104..v0.2.105) - 2025-07-22

### 🐛 Bug Fixes

- *(platform)* Fix broken pytest collection if user does not have permission to access aignx test bucket - ([a65930c](https://github.com/aignostics/python-sdk/commit/a65930c2cde73aa57af338aa6c752cff2a1fbfeb))

### ⚙️ Miscellaneous Tasks

- *(gha)* Spike for Ketryx integration - ([a65930c](https://github.com/aignostics/python-sdk/commit/a65930c2cde73aa57af338aa6c752cff2a1fbfeb))
- *(gha)* Allow to skip jobs/steps via commit message, see CONTRIBUTING.md - ([a65930c](https://github.com/aignostics/python-sdk/commit/a65930c2cde73aa57af338aa6c752cff2a1fbfeb))
- *(gha)* Add metadata to BetterStack when posting heartbeats ([#61](https://github.com/orhun/git-cliff/issues/61)) - ([0bb3b3f](https://github.com/aignostics/python-sdk/commit/0bb3b3f602148ffe071ff96e7d7d7b6042fb18a3))
- *(gha)* Add metadata to BetterStack when posting heartbeats - ([0bb3b3f](https://github.com/aignostics/python-sdk/commit/0bb3b3f602148ffe071ff96e7d7d7b6042fb18a3))
- *(gha)* Add --fail-with-body to BetterStack curl request and reorder arguments - ([0bb3b3f](https://github.com/aignostics/python-sdk/commit/0bb3b3f602148ffe071ff96e7d7d7b6042fb18a3))

### 🛡️ Security

- *(dep)* Ensure starlette >= 0.47.2 given GHSA-2c2j-9gv5-cj73 - ([6de44aa](https://github.com/aignostics/python-sdk/commit/6de44aa2f64e400357b37c5c536eea68ef959e78))



* @idelsink made their first contribution

# [v0.2.104](https://github.com/aignostics/python-sdk/compare/v0.2.103..v0.2.104) - 2025-07-15

### 📚 Documentation

- Update URLs in openapi spec and downstream docs - ([e24eba4](https://github.com/aignostics/python-sdk/commit/e24eba44122448a40cb41c2ac738b93354aa6f3d))


# [v0.2.103](https://github.com/aignostics/python-sdk/compare/v0.2.102..v0.2.103) - 2025-07-15

### ⚙️ Miscellaneous Tasks

- *(gha)* Monitor scheduled audit in betterstack - ([5065a2e](https://github.com/aignostics/python-sdk/commit/5065a2eb3e067ae5c535ea22676fb2fd4ff414ff))


# [v0.2.102](https://github.com/aignostics/python-sdk/compare/v0.2.101..v0.2.102) - 2025-07-15

### ⚙️ Miscellaneous Tasks

- *(gha)* Separate scheduled audit in separate workflow - ([98e7ad0](https://github.com/aignostics/python-sdk/commit/98e7ad0446017fec27907fa5126fd916491f8880))


# [v0.2.101](https://github.com/aignostics/python-sdk/compare/v0.2.99..v0.2.101) - 2025-07-15

### ⚙️ Miscellaneous Tasks

- *(deps)* Update ghcr.io/astral-sh/uv docker tag to v0.7.20 ([#59](https://github.com/orhun/git-cliff/issues/59)) - ([0ef534f](https://github.com/aignostics/python-sdk/commit/0ef534f29f96a6e14caaa9632bdb0d116d086b32))
- *(deps)* Update ghcr.io/astral-sh/uv docker tag to v0.7.15 ([#54](https://github.com/orhun/git-cliff/issues/54)) - ([ab46b50](https://github.com/aignostics/python-sdk/commit/ab46b5003f3eb8b1559b582c08603b3522bd0579))
- *(deps)* Bump astral-sh/setup-uv from 6.3.0 to 6.3.1 ([#55](https://github.com/orhun/git-cliff/issues/55)) - ([e90b6f2](https://github.com/aignostics/python-sdk/commit/e90b6f2131779ceb3d04c661dbf4398d6f4968b3))
- Renovate[bot] <29139614+renovate[bot]@users.noreply.github.com> - ([0ef534f](https://github.com/aignostics/python-sdk/commit/0ef534f29f96a6e14caaa9632bdb0d116d086b32))
- Helmut Hoffer von Ankershoffen né Oertel <helmut@aignostics.com> - ([ab46b50](https://github.com/aignostics/python-sdk/commit/ab46b5003f3eb8b1559b582c08603b3522bd0579))
- Astral-sh/setup-uv - ([e90b6f2](https://github.com/aignostics/python-sdk/commit/e90b6f2131779ceb3d04c661dbf4398d6f4968b3))
- Dependabot[bot] <support@github.com> - ([e90b6f2](https://github.com/aignostics/python-sdk/commit/e90b6f2131779ceb3d04c661dbf4398d6f4968b3))
- Dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com> - ([e90b6f2](https://github.com/aignostics/python-sdk/commit/e90b6f2131779ceb3d04c661dbf4398d6f4968b3))

### 🛡️ Security

- *(dep)* Override aiohttp to 3.12.14 given vulnerability GHSA-9548-qrrj-x5pj - ([a239d23](https://github.com/aignostics/python-sdk/commit/a239d236ac58f6a6bdf3a3be5bb804367b974f1e))



* @renovate[bot] made their first contribution
* @dependabot[bot] made their first contribution

# [v0.2.99](https://github.com/aignostics/python-sdk/compare/v0.2.98..v0.2.99) - 2025-07-10

### 🚜 Refactor

- *(boot)* Reduce boot time - ([81423dd](https://github.com/aignostics/python-sdk/commit/81423dda4f201dbe729b3b4c68473adeb89d9e32))

### 📚 Documentation

- Minor tweaks - ([81423dd](https://github.com/aignostics/python-sdk/commit/81423dda4f201dbe729b3b4c68473adeb89d9e32))

### ⚙️ Miscellaneous Tasks

- *(deps)* Update deps - ([81423dd](https://github.com/aignostics/python-sdk/commit/81423dda4f201dbe729b3b4c68473adeb89d9e32))
- *(platform)* Update to latest openapi spec - ([81423dd](https://github.com/aignostics/python-sdk/commit/81423dda4f201dbe729b3b4c68473adeb89d9e32))


# [v0.2.98](https://github.com/aignostics/python-sdk/compare/v0.2.97..v0.2.98) - 2025-07-01

### ⚙️ Miscellaneous Tasks

- *(application)* Mark test as long running - ([19db155](https://github.com/aignostics/python-sdk/commit/19db1553a1c13610ae211f45767749da43de383d))


# [v0.2.97](https://github.com/aignostics/python-sdk/compare/v0.2.96..v0.2.97) - 2025-07-01

### 🛡️ Security

- *(deps)* Pillow 11.3.0 given CVE-2025-48379 - ([ffd5af1](https://github.com/aignostics/python-sdk/commit/ffd5af102ad58d53dd20e4e29ada31e2b566a9ca))


# [v0.2.96](https://github.com/aignostics/python-sdk/compare/v0.2.95..v0.2.96) - 2025-07-01

### 🐛 Bug Fixes

- *(platform)* Allow for rapid re-auth - ([34ca8ee](https://github.com/aignostics/python-sdk/commit/34ca8ee4064ceb72619bc429ca12318b1718deab))


# [v0.2.95](https://github.com/aignostics/python-sdk/compare/v0.2.94..v0.2.95) - 2025-07-01

### 🐛 Bug Fixes

- *(application)* Allow next post excluding slides if remaining slides with valid metadata - ([7254298](https://github.com/aignostics/python-sdk/commit/7254298e1d5b58b3e4c456ef3971db7e7e196ca7))


# [v0.2.94](https://github.com/aignostics/python-sdk/compare/v0.2.93..v0.2.94) - 2025-07-01

### ⚙️ Miscellaneous Tasks

- *(platform)* Even more time for test app - ([3c68bbc](https://github.com/aignostics/python-sdk/commit/3c68bbccd541d24558b7db23f2c4bf64dc44330d))


# [v0.2.93](https://github.com/aignostics/python-sdk/compare/v0.2.92..v0.2.93) - 2025-06-29

### ⚙️ Miscellaneous Tasks

- *(platform)* Even more time for test app - ([fb0f8fe](https://github.com/aignostics/python-sdk/commit/fb0f8febda749beeba88cf14ba5e0c7bd68083e6))


# [v0.2.92](https://github.com/aignostics/python-sdk/compare/v0.2.91..v0.2.92) - 2025-06-29

### ⚙️ Miscellaneous Tasks

- *(application)* Adapt test - ([d879958](https://github.com/aignostics/python-sdk/commit/d8799589363b32b10d5de62eab8298b866e10c44))


# [v0.2.91](https://github.com/aignostics/python-sdk/compare/v0.2.90..v0.2.91) - 2025-06-29

### 🚜 Refactor

- *(application)* Consistent exception logging and raising - ([1a702a7](https://github.com/aignostics/python-sdk/commit/1a702a7ea08dfdb9614c44391a01de54e6c73a00))


# [v0.2.90](https://github.com/aignostics/python-sdk/compare/v0.2.89..v0.2.90) - 2025-06-29

### ⚙️ Miscellaneous Tasks

- Run hooks - ([173e172](https://github.com/aignostics/python-sdk/commit/173e17221682e5f43c63d172de17c93bc1709063))


# [v0.2.89](https://github.com/aignostics/python-sdk/compare/v0.2.88..v0.2.89) - 2025-06-29

### ⚙️ Miscellaneous Tasks

- Run hooks - ([c6e6d9a](https://github.com/aignostics/python-sdk/commit/c6e6d9a6c75a962d55dc6d308792deaa11e64c66))


# [v0.2.88](https://github.com/aignostics/python-sdk/compare/v0.2.87..v0.2.88) - 2025-06-29

### ⚙️ Miscellaneous Tasks

- *(native)* Only distribute aignostics.app bundle for MacOS - ([a7cc414](https://github.com/aignostics/python-sdk/commit/a7cc414045b225acb1c4e1c81f93a019dba27b4c))
- *(native)* 7z, to preserve attributes - ([a7cc414](https://github.com/aignostics/python-sdk/commit/a7cc414045b225acb1c4e1c81f93a019dba27b4c))


# [v0.2.87](https://github.com/aignostics/python-sdk/compare/v0.2.86..v0.2.87) - 2025-06-28

### 🐛 Bug Fixes

- *(dataset)* Missing dependency, while still smaller then pyarrow - ([ff1f178](https://github.com/aignostics/python-sdk/commit/ff1f178df3bdde970a67c8f2c1d86eac9126195b))


# [v0.2.86](https://github.com/aignostics/python-sdk/compare/v0.2.85..v0.2.86) - 2025-06-28

### 🚜 Refactor

- *(logging)* Revert to cwd for logfile - ([cc9e990](https://github.com/aignostics/python-sdk/commit/cc9e990b9b921ff0f23d034ae050a492552d0c4a))


# [v0.2.85](https://github.com/aignostics/python-sdk/compare/v0.2.84..v0.2.85) - 2025-06-28

### 🚜 Refactor

- *(logging)* Use app dir as default for log file - ([dd52d9e](https://github.com/aignostics/python-sdk/commit/dd52d9eb33adc8eb9219185ad6e23a5f107af7cf))
- *(native)* Significantly reduce size and bootup time - ([dd52d9e](https://github.com/aignostics/python-sdk/commit/dd52d9eb33adc8eb9219185ad6e23a5f107af7cf))


# [v0.2.84](https://github.com/aignostics/python-sdk/compare/v0.2.83..v0.2.84) - 2025-06-28

### ⚙️ Miscellaneous Tasks

- *(platform)* Give test application more time in tests - ([5f99ebb](https://github.com/aignostics/python-sdk/commit/5f99ebbd9d61a7d4a9089f7577a87638623dcd78))


# [v0.2.83](https://github.com/aignostics/python-sdk/compare/v0.2.82..v0.2.83) - 2025-06-28

### 📚 Documentation

- *(platform)* Description - ([d09794a](https://github.com/aignostics/python-sdk/commit/d09794a157def88c63054259f40262de62d71f8d))


# [v0.2.82](https://github.com/aignostics/python-sdk/compare/v0.2.81..v0.2.82) - 2025-06-28

### 📚 Documentation

- *(platform)* Description - ([09c0c1e](https://github.com/aignostics/python-sdk/commit/09c0c1eaf8741e2cd51e667d2593fd9df4311109))


# [v0.2.81](https://github.com/aignostics/python-sdk/compare/v0.2.80..v0.2.81) - 2025-06-28

### 📚 Documentation

- *(platform)* Description - ([773495d](https://github.com/aignostics/python-sdk/commit/773495d782026e4d146b4051939725cb00cfbf87))


# [v0.2.80](https://github.com/aignostics/python-sdk/compare/v0.2.79..v0.2.80) - 2025-06-28

### 🚜 Refactor

- *(platform)* Test timeout/expires - ([89745fc](https://github.com/aignostics/python-sdk/commit/89745fcaf54b63b81d590ff67413f8b7611faeb5))


# [v0.2.79](https://github.com/aignostics/python-sdk/compare/v0.2.78..v0.2.79) - 2025-06-28

### 🚜 Refactor

- *(platform)* Test timeout/expires - ([855fae9](https://github.com/aignostics/python-sdk/commit/855fae96e65d4b3d25ad383823b75aab33125bcc))


# [v0.2.78](https://github.com/aignostics/python-sdk/compare/v0.2.77..v0.2.78) - 2025-06-28

### ⚙️ Miscellaneous Tasks

- *(platform)* Adapt test to app versions - ([cc2c17d](https://github.com/aignostics/python-sdk/commit/cc2c17d9852a34efde57c74edb0957dba31a6889))


# [v0.2.77](https://github.com/aignostics/python-sdk/compare/v0.2.76..v0.2.77) - 2025-06-28

### ⚙️ Miscellaneous Tasks

- *(platform)* Adapt test to app versions - ([905d03e](https://github.com/aignostics/python-sdk/commit/905d03eb1a5a6db6c43d75751074f17937519dc6))


# [v0.2.76](https://github.com/aignostics/python-sdk/compare/v0.2.75..v0.2.76) - 2025-06-27

### ⚙️ Miscellaneous Tasks

- *(platform)* Move from dummy to test app in test - ([7fcb42c](https://github.com/aignostics/python-sdk/commit/7fcb42c53965568abdf444b684e59256bf211d4e))


# [v0.2.75](https://github.com/aignostics/python-sdk/compare/v0.2.74..v0.2.75) - 2025-06-27

### ⚙️ Miscellaneous Tasks

- *(platform)* Allow long running tests for 4h, bump of signed url expire accordingly - ([3965ce0](https://github.com/aignostics/python-sdk/commit/3965ce06333eaa35e2ce4c6d217e6ae8c7fbc512))


# [v0.2.74](https://github.com/aignostics/python-sdk/compare/v0.2.73..v0.2.74) - 2025-06-27

### ⚙️ Miscellaneous Tasks

- *(application,platform)* Test with v1.0.0-beta.4 of HETA - ([ab60f2f](https://github.com/aignostics/python-sdk/commit/ab60f2f795dc31a3bb52e5d0333af84187aac3e2))


# [v0.2.73](https://github.com/aignostics/python-sdk/compare/v0.2.72..v0.2.73) - 2025-06-27

### 🐛 Bug Fixes

- ⚡️ Use SemVer to check for application ids in launchpad ([#56](https://github.com/orhun/git-cliff/issues/56)) - ([c6c874e](https://github.com/aignostics/python-sdk/commit/c6c874ee9d2861f8fccb4dc220096d745515f17e))

### 🚜 Refactor

- *(application)* Introduce service tests - ([1875741](https://github.com/aignostics/python-sdk/commit/1875741fba55963bf739ff6b8907e938d5e02183))



* @ari-nz made their first contribution

# [v0.2.72](https://github.com/aignostics/python-sdk/compare/v0.2.71..v0.2.72) - 2025-06-25

### ⚙️ Miscellaneous Tasks

- *(platform)* Adapt tests to breaking change - ([4d11384](https://github.com/aignostics/python-sdk/commit/4d113843f01a3da81c1e5e0a847fcefe21a1ddbe))


# [v0.2.71](https://github.com/aignostics/python-sdk/compare/v0.2.70..v0.2.71) - 2025-06-25

### 🐛 Bug Fixes

- *(platform)* Adapt to breaking change in API - ([7920b0b](https://github.com/aignostics/python-sdk/commit/7920b0b21e527a596c5e7c23f7a9914ac447c95f))

### ⚙️ Miscellaneous Tasks

- *(deps)* Gha setup-uv dep - ([3def1bd](https://github.com/aignostics/python-sdk/commit/3def1bd3704cc559bdbd6509ba4e359d974ab2d1))
- Try new api spec without further change - ([2ba558c](https://github.com/aignostics/python-sdk/commit/2ba558c05baebd8ef901b3ba7dda71b765286465))


# [v0.2.70](https://github.com/aignostics/python-sdk/compare/v0.2.69..v0.2.70) - 2025-06-24

### 📚 Documentation

- Enhance structure and layout of Changelog - ([f5a58ac](https://github.com/aignostics/python-sdk/commit/f5a58ac22142fadcc6474de5032b1741eb787c0f))

### ⚙️ Miscellaneous Tasks

- *(bucket)* Grant more time for bucket gui workflow in test - ([f5a58ac](https://github.com/aignostics/python-sdk/commit/f5a58ac22142fadcc6474de5032b1741eb787c0f))
- *(deps)* Update dependencies for GitHub actions - ([f5a58ac](https://github.com/aignostics/python-sdk/commit/f5a58ac22142fadcc6474de5032b1741eb787c0f))


# [v0.2.69](https://github.com/aignostics/python-sdk/compare/v0.2.68..v0.2.69) - 2025-06-23

### 🐛 Bug Fixes

- *(platform/user)* Reload on reauth - ([4f05b84](https://github.com/aignostics/python-sdk/commit/4f05b84537f4a3f24ffb08c904750c0063c91301))

### ⚙️ Miscellaneous Tasks

- *(win32)* Username - ([e5733c1](https://github.com/aignostics/python-sdk/commit/e5733c13be9b55ffa18145d706952d74c793701c))


# [v0.2.68](https://github.com/aignostics/python-sdk/compare/v0.2.67..v0.2.68) - 2025-06-19

### ⚙️ Miscellaneous Tasks

- *(di)* Adapt to typer workaround - ([50710ee](https://github.com/aignostics/python-sdk/commit/50710eebff01500300bfb6a5f49b5492691edff8))


# [v0.2.67](https://github.com/aignostics/python-sdk/compare/v0.2.66..v0.2.67) - 2025-06-19

### ⚙️ Miscellaneous Tasks

- *(cli)* Adapt tests - ([dbbd2dd](https://github.com/aignostics/python-sdk/commit/dbbd2dd4472a33a7569563c11c3ee57747759599))


# [v0.2.66](https://github.com/aignostics/python-sdk/compare/v0.2.64..v0.2.66) - 2025-06-19

### 🐛 Bug Fixes

- *(typer)* Workaround https://github.com/fastapi/typer/pull/1240 - ([207eb0c](https://github.com/aignostics/python-sdk/commit/207eb0c45ba5774e52031bb9f5fbfcc1e485d184))

### 🚜 Refactor

- *(performance)* Faster boot - ([207eb0c](https://github.com/aignostics/python-sdk/commit/207eb0c45ba5774e52031bb9f5fbfcc1e485d184))

### 🎨 Styling

- *(bucket)* Button layout - ([207eb0c](https://github.com/aignostics/python-sdk/commit/207eb0c45ba5774e52031bb9f5fbfcc1e485d184))

### 🛡️ Security

- *(security)* Update deps given CVE-2025-50181, CVE-2025-50182 - ([207eb0c](https://github.com/aignostics/python-sdk/commit/207eb0c45ba5774e52031bb9f5fbfcc1e485d184))


# [v0.2.64](https://github.com/aignostics/python-sdk/compare/v0.2.63..v0.2.64) - 2025-06-18

### ⛰️  Features

- *(bucket)* Allow to select destination in bucket download gui - ([0ecd4c3](https://github.com/aignostics/python-sdk/commit/0ecd4c325c45279941055683c593740ceb5d87a8))

### 🚜 Refactor

- *(application)* Shrink images - ([a09cc7e](https://github.com/aignostics/python-sdk/commit/a09cc7e2665c9529b61dd689c47b5e805f88cdf1))

### ⚙️ Miscellaneous Tasks

- *(bucket)* Bump test duration - ([a09cc7e](https://github.com/aignostics/python-sdk/commit/a09cc7e2665c9529b61dd689c47b5e805f88cdf1))


# [v0.2.63](https://github.com/aignostics/python-sdk/compare/v0.2.62..v0.2.63) - 2025-06-17

### ⛰️  Features

- *(bucket)* Proper download including support for patterns, keys, gui, cli - ([ef04b98](https://github.com/aignostics/python-sdk/commit/ef04b981c077b75bdd4188ce6f896dafd8849a88))
- *(bucket)* Purge - ([ef04b98](https://github.com/aignostics/python-sdk/commit/ef04b981c077b75bdd4188ce6f896dafd8849a88))

### 🚜 Refactor

- *(bucket)* Removed ls, refactored find - ([ef04b98](https://github.com/aignostics/python-sdk/commit/ef04b981c077b75bdd4188ce6f896dafd8849a88))


# [v0.2.62](https://github.com/aignostics/python-sdk/compare/v0.2.61..v0.2.62) - 2025-06-16

### 🎨 Styling

- Lint - ([a42d08c](https://github.com/aignostics/python-sdk/commit/a42d08c219860ea3ffaec95b102175f5b49d71df))

### ⚙️ Miscellaneous Tasks

- *(QuPath)* Run test on linux - ([2d1b45e](https://github.com/aignostics/python-sdk/commit/2d1b45e305889fad942ac27c6b162ea2c2ed47d7))
- Download from bucket cli - ([13e857e](https://github.com/aignostics/python-sdk/commit/13e857eb52fa166b0c1b6127f314663fbafa72ed))


# [v0.2.61](https://github.com/aignostics/python-sdk/compare/v0.2.60..v0.2.61) - 2025-06-15

### 🚜 Refactor

- *(user)* Rename from platform to user in cli - ([efa9b50](https://github.com/aignostics/python-sdk/commit/efa9b50ceca309edd75cc7f4843f9989fe53ac4e))


# [v0.2.60](https://github.com/aignostics/python-sdk/compare/v0.2.59..v0.2.60) - 2025-06-15

### ⛰️  Features

- *(userinfo)* Allow to edit profile - ([788f209](https://github.com/aignostics/python-sdk/commit/788f20901fe8b7156e3058ca95cbb9849da2940c))


# [v0.2.59](https://github.com/aignostics/python-sdk/compare/v0.2.58..v0.2.59) - 2025-06-15

### 🎨 Styling

- *(gui)* Polish user info - ([305dda9](https://github.com/aignostics/python-sdk/commit/305dda9bed74899f6c69026a73d5400597f4e6dc))


# [v0.2.58](https://github.com/aignostics/python-sdk/compare/v0.2.57..v0.2.58) - 2025-06-15

### 🎨 Styling

- *(gui)* Polish user info - ([0ffc5b3](https://github.com/aignostics/python-sdk/commit/0ffc5b37996fdfb099a9f021e8802e9bf03a2bb8))


# [v0.2.57](https://github.com/aignostics/python-sdk/compare/v0.2.56..v0.2.57) - 2025-06-15

### ⚙️ Miscellaneous Tasks

- *(platform)* Lazyload srvice in cli - ([28980c5](https://github.com/aignostics/python-sdk/commit/28980c5584169f0e90a6ca23e40f46b67251a27e))


# [v0.2.56](https://github.com/aignostics/python-sdk/compare/v0.2.55..v0.2.56) - 2025-06-15

### ⛰️  Features

- *(platform,gui)* Org name - ([51c65a2](https://github.com/aignostics/python-sdk/commit/51c65a26bc3957ef02ffc7d7f201494ec0e0ce8b))


# [v0.2.55](https://github.com/aignostics/python-sdk/compare/v0.2.54..v0.2.55) - 2025-06-15

### 🎨 Styling

- Welcome user by name in launchpad - ([de73025](https://github.com/aignostics/python-sdk/commit/de73025c09c6d62d8107ed9f6f095060127a1d2c))


# [v0.2.54](https://github.com/aignostics/python-sdk/compare/v0.2.53..v0.2.54) - 2025-06-15

### ⛰️  Features

- *(platform,gui,diagnostics)* Whoami - ([0bad5f2](https://github.com/aignostics/python-sdk/commit/0bad5f24766f3c05fc09b47a5c4f20b79b82588b))

### 🐛 Bug Fixes

- *(platform)* Graceful fail on user info not accessible - ([01f536a](https://github.com/aignostics/python-sdk/commit/01f536a668f2ae8a57e8b837c23dc592212f0ae2))

### 🚜 Refactor

- *(platform)* Refactor user profile - ([ff47251](https://github.com/aignostics/python-sdk/commit/ff472517e53ad114378954bade1838569e8b58df))

### 🎨 Styling

- Nicer start page graphics - ([0bad5f2](https://github.com/aignostics/python-sdk/commit/0bad5f24766f3c05fc09b47a5c4f20b79b82588b))

### ⚙️ Miscellaneous Tasks

- *(deps)* Bump - ([ff60f38](https://github.com/aignostics/python-sdk/commit/ff60f3885dada887754d530aee118751900f067f))


# [v0.2.53](https://github.com/aignostics/python-sdk/compare/v0.2.52..v0.2.53) - 2025-06-12

### ⛰️  Features

- QuPath enabled by default - ([a52d2fb](https://github.com/aignostics/python-sdk/commit/a52d2fbafed571a5ef5b850800c742bddf79ff4e))

### 🚜 Refactor

- Don't support QuPath on Linux/arm - ([a52d2fb](https://github.com/aignostics/python-sdk/commit/a52d2fbafed571a5ef5b850800c742bddf79ff4e))

### 📚 Documentation

- Generate - ([13b3fbc](https://github.com/aignostics/python-sdk/commit/13b3fbc104a331b778dba501dcd3b88533cf8693))


# [v0.2.52](https://github.com/aignostics/python-sdk/compare/v0.2.51..v0.2.52) - 2025-06-12

### 🐛 Bug Fixes

- *(unmask)* Unmask secrets on request in all services - ([6a96ed3](https://github.com/aignostics/python-sdk/commit/6a96ed38371614d7ea1d5cd670e218c3d6d516d9))

### ⚙️ Miscellaneous Tasks

- *(Makefile)* Typo - ([566b1e6](https://github.com/aignostics/python-sdk/commit/566b1e629060bbe20b360a81505837b9e4d0c0ca))


# [v0.2.51](https://github.com/aignostics/python-sdk/compare/v0.2.50..v0.2.51) - 2025-06-11

### ⚙️ Miscellaneous Tasks

- Move to long running for install to inspect test - ([42d12d0](https://github.com/aignostics/python-sdk/commit/42d12d0d3b8a7a0b4300ec0f62fc430f13b5cf12))


# [v0.2.50](https://github.com/aignostics/python-sdk/compare/v0.2.49..v0.2.50) - 2025-06-11

### 🚜 Refactor

- *(QuPath)* Proper handling of script max execution time - ([b0d1c79](https://github.com/aignostics/python-sdk/commit/b0d1c79bc3e9bde03ba42c151545b4d5687feff6))

### ⚙️ Miscellaneous Tasks

- Timeout - ([408431a](https://github.com/aignostics/python-sdk/commit/408431aa55452f95f4e3cab521f9a28d017aa1c5))


# [v0.2.49](https://github.com/aignostics/python-sdk/compare/v0.2.48..v0.2.49) - 2025-06-10

### ⛰️  Features

- *(application)* Dump zip with application schemata - ([af33133](https://github.com/aignostics/python-sdk/commit/af33133cc50a0b3a2f1c36f53b3d338d96f96b78))


# [v0.2.48](https://github.com/aignostics/python-sdk/compare/v0.2.47..v0.2.48) - 2025-06-10

### 📚 Documentation

- Fix api docs generation - ([cef82dc](https://github.com/aignostics/python-sdk/commit/cef82dca164bc73bda870807756d44666d38b5e7))


# [v0.2.47](https://github.com/aignostics/python-sdk/compare/v0.2.46..v0.2.47) - 2025-06-10

### ⚙️ Miscellaneous Tasks

- *(test)* No warn on kill; output qupath inspect results - ([a5d666e](https://github.com/aignostics/python-sdk/commit/a5d666e596c3aaa130894a2d6d23d61e0465423f))


# [v0.2.46](https://github.com/aignostics/python-sdk/compare/v0.2.45..v0.2.46) - 2025-06-09

### ⚙️ Miscellaneous Tasks

- Zip on release - ([093f4d4](https://github.com/aignostics/python-sdk/commit/093f4d4765cddd5093a283ae7998ac3205533255))


# [v0.2.45](https://github.com/aignostics/python-sdk/compare/v0.2.44..v0.2.45) - 2025-06-09

### ⚙️ Miscellaneous Tasks

- *(deps)* Bump actions in gha and duckdb - ([fc068e9](https://github.com/aignostics/python-sdk/commit/fc068e96d8cba651e5c3a421562ac851e450b6da))


# [v0.2.44](https://github.com/aignostics/python-sdk/compare/v0.2.43..v0.2.44) - 2025-06-09

### ⚙️ Miscellaneous Tasks

- Encoding for win32 on package publish - ([7a3fda3](https://github.com/aignostics/python-sdk/commit/7a3fda3cedb58992676f47d1ae5167eb25dce167))


# [v0.2.43](https://github.com/aignostics/python-sdk/compare/v0.2.42..v0.2.43) - 2025-06-09

### ⚙️ Miscellaneous Tasks

- *(QuPath)* Check QuPath is launched in install to inspect test - ([18a68d2](https://github.com/aignostics/python-sdk/commit/18a68d2b8fdbd8bbd13c70f1edccae25925a860f))
- *(QuPath)* E2E test from install via run to inspect - ([451ca3d](https://github.com/aignostics/python-sdk/commit/451ca3dd8be2e7af13cd55a6eee2ebef635390cb))


# [v0.2.42](https://github.com/aignostics/python-sdk/compare/v0.2.41..v0.2.42) - 2025-06-09

### ⚙️ Miscellaneous Tasks

- Release workflow - ([04fae00](https://github.com/aignostics/python-sdk/commit/04fae00b818e8a5c6014a6cad0cfddc5cfa28058))


# [v0.2.41](https://github.com/aignostics/python-sdk/compare/v0.2.40..v0.2.41) - 2025-06-09


# [v0.2.40](https://github.com/aignostics/python-sdk/compare/v0.2.39..v0.2.40) - 2025-06-09

### ⛰️  Features

- *(native)* Spike for native (compiled) apps - ([e03512c](https://github.com/aignostics/python-sdk/commit/e03512c9be6ace3cedebd3981bf12c39f586486d))
- *(system)* Allow to unmask secrets - ([e03512c](https://github.com/aignostics/python-sdk/commit/e03512c9be6ace3cedebd3981bf12c39f586486d))

### 🚜 Refactor

- *(gui)* Consistent use of spinners and awaiting - ([f5ca9c4](https://github.com/aignostics/python-sdk/commit/f5ca9c4709ce1739c62d4ab74966470f5cfc21d2))
- *(qupath)* Using groovy, not paquo; GPL removed from allow-list when license auditing - ([e03512c](https://github.com/aignostics/python-sdk/commit/e03512c9be6ace3cedebd3981bf12c39f586486d))
- *(qupath)* Using groovy, not paquo - ([f5ca9c4](https://github.com/aignostics/python-sdk/commit/f5ca9c4709ce1739c62d4ab74966470f5cfc21d2))
- *(various)* Consistent use of spinners and awaiting; sentry and logfire can now be removed as dependencies - ([e03512c](https://github.com/aignostics/python-sdk/commit/e03512c9be6ace3cedebd3981bf12c39f586486d))

### ⚙️ Miscellaneous Tasks

- *(cross-platform)* Now matrix testing on win-amd64, win-arm64, linux-amd64, linux-arm64, mac-arm64; related fixes - ([e03512c](https://github.com/aignostics/python-sdk/commit/e03512c9be6ace3cedebd3981bf12c39f586486d))
- *(native)* Include version in macOS bundle - ([5473271](https://github.com/aignostics/python-sdk/commit/54732711102b17af26376084095ee9370715265f))


# [v0.2.39](https://github.com/aignostics/python-sdk/compare/v0.2.38..v0.2.39) - 2025-06-06

### 🐛 Bug Fixes

- *(platform)* Refresh token repl - ([9a3adf2](https://github.com/aignostics/python-sdk/commit/9a3adf26e207d1bb4ae8ea1adea6d86216d7cc6d))


# [v0.2.38](https://github.com/aignostics/python-sdk/compare/v0.2.37..v0.2.38) - 2025-06-06

### 🚜 Refactor

- *(general)* Central place for defining supported WSI extensions - ([0b052a7](https://github.com/aignostics/python-sdk/commit/0b052a78197960627896445095a0c2af2854f5fd))
- *(info)* Consistently show settings - ([0b052a7](https://github.com/aignostics/python-sdk/commit/0b052a78197960627896445095a0c2af2854f5fd))


# [v0.2.37](https://github.com/aignostics/python-sdk/compare/v0.2.36..v0.2.37) - 2025-06-06

### ⛰️  Features

- *(bucket)* Make expiration time of upload/download properly configurable, and include in info - ([6191781](https://github.com/aignostics/python-sdk/commit/61917818cdefaf5de9cb3e22cd939141ee75cfa1))

### 🐛 Bug Fixes

- *(bucket)* Use longer 7d expiration time for signed upload urls instead of 1h - ([6191781](https://github.com/aignostics/python-sdk/commit/61917818cdefaf5de9cb3e22cd939141ee75cfa1))


# [v0.2.36](https://github.com/aignostics/python-sdk/compare/v0.2.34..v0.2.36) - 2025-06-05

### 📚 Documentation

- Generate - ([e74c5da](https://github.com/aignostics/python-sdk/commit/e74c5dac14fc46087d81eaf418af6822bfeba9f4))

### 🛡️ Security

- *(jupyter)* CVE-2025-30167 rel. jupyter-core - ([a27da66](https://github.com/aignostics/python-sdk/commit/a27da665fe7e3ba896529c66ac94026b8cabb4ba))


# [v0.2.34](https://github.com/aignostics/python-sdk/compare/v0.2.33..v0.2.34) - 2025-06-04

### ⚙️ Miscellaneous Tasks

- Workaround missing scheme in proxy config - ([6d5f20e](https://github.com/aignostics/python-sdk/commit/6d5f20eff56221c045a0a4a1a15ba1bfda5d8dbd))


# [v0.2.33](https://github.com/aignostics/python-sdk/compare/v0.2.32..v0.2.33) - 2025-06-03

### 🚜 Refactor

- *(application)* Don't allow to close download dialog by clicking outside - ([1deeff3](https://github.com/aignostics/python-sdk/commit/1deeff3bc1aa1ba0efa0a446e1b2e80f8bae0684))


# [v0.2.32](https://github.com/aignostics/python-sdk/compare/v0.2.31..v0.2.32) - 2025-06-03

### 🎨 Styling

- *(header,run_describe)* Simplify a bit to make space - ([4ee1409](https://github.com/aignostics/python-sdk/commit/4ee140944c5784ef33d60a25818c333b54da4bc2))


# [v0.2.31](https://github.com/aignostics/python-sdk/compare/v0.2.30..v0.2.31) - 2025-06-03

### ⛰️  Features

- *(QuPath)* Support updating QuPath - ([29b1263](https://github.com/aignostics/python-sdk/commit/29b126320568400e315397cda626ca1a8b50978f))
- *(QuPath)* Use 0.6.0-rc5 - ([29b1263](https://github.com/aignostics/python-sdk/commit/29b126320568400e315397cda626ca1a8b50978f))
- *(QuPath)* Deeper info - ([29b1263](https://github.com/aignostics/python-sdk/commit/29b126320568400e315397cda626ca1a8b50978f))

### 🚜 Refactor

- *(QuPath)* 20x speed up writing polygons by switching from paquo to groovy - ([29b1263](https://github.com/aignostics/python-sdk/commit/29b126320568400e315397cda626ca1a8b50978f))
- *(progress)* Faster progress bars - ([29b1263](https://github.com/aignostics/python-sdk/commit/29b126320568400e315397cda626ca1a8b50978f))


# [v0.2.30](https://github.com/aignostics/python-sdk/compare/v0.2.27..v0.2.30) - 2025-06-02

### ⛰️  Features

- *(System)* Enable to enable/disable diagnostics in UI - ([b27296a](https://github.com/aignostics/python-sdk/commit/b27296a035a1cbbc0e61158c32672416b90accc7))

### 🐛 Bug Fixes

- *(Windows)* Sanitize paths so they don't contain a colon if not drive letter - ([165cc59](https://github.com/aignostics/python-sdk/commit/165cc591ad299e766dd453efc3896ea8f6b466df))

### 🚜 Refactor

- *(System)* Move settings logic to service - ([b27296a](https://github.com/aignostics/python-sdk/commit/b27296a035a1cbbc0e61158c32672416b90accc7))

### 🎨 Styling

- *(System)* Minimal love for Settings and Info page - ([b27296a](https://github.com/aignostics/python-sdk/commit/b27296a035a1cbbc0e61158c32672416b90accc7))


# [v0.2.27](https://github.com/aignostics/python-sdk/compare/v0.2.26..v0.2.27) - 2025-06-01

### ⚙️ Miscellaneous Tasks

- Test of notebook, race - ([1baef8e](https://github.com/aignostics/python-sdk/commit/1baef8e04f391e1597ddbe08f125c19279a4b2ed))


# [v0.2.26](https://github.com/aignostics/python-sdk/compare/v0.2.25..v0.2.26) - 2025-06-01

### 🚜 Refactor

- *(sonarqube)* Annotate generator - ([a72c5ba](https://github.com/aignostics/python-sdk/commit/a72c5baf22f36bbe33ab768fa9d2d457114e6ab1))

### ⚙️ Miscellaneous Tasks

- Non-sequential as there is a dependent one - ([a7f74c1](https://github.com/aignostics/python-sdk/commit/a7f74c13773774cb6b717432719d5e1554f89f07))


# [v0.2.25](https://github.com/aignostics/python-sdk/compare/v0.2.23..v0.2.25) - 2025-06-01

### ⛰️  Features

- *(marimo)* Marimo open with downloaded results - ([7cab5a1](https://github.com/aignostics/python-sdk/commit/7cab5a105c7707ba4e90ce4f0ef3c49a7c1db8b8))
- *(marimo)* Open marimo from extension page - ([7cab5a1](https://github.com/aignostics/python-sdk/commit/7cab5a105c7707ba4e90ce4f0ef3c49a7c1db8b8))


# [v0.2.23](https://github.com/aignostics/python-sdk/compare/v0.2.22..v0.2.23) - 2025-06-01

### 🚜 Refactor

- *(wsi)* Simplify further - ([1992de1](https://github.com/aignostics/python-sdk/commit/1992de1e8f560d79fe98e4f923e1a97c2abcf8f1))
- *(wsi)* Simplify, and fallback image - ([e08afd3](https://github.com/aignostics/python-sdk/commit/e08afd3517357d25c38d818a440922635efb5896))

### ⚙️ Miscellaneous Tasks

- *(wsi)* Adapt tests given fallback - ([3db7ebc](https://github.com/aignostics/python-sdk/commit/3db7ebc67daf9d131f2e071c93b39b2af0f3aa75))
- Make gui test more reliable - ([59524fd](https://github.com/aignostics/python-sdk/commit/59524fd02c8e1a327e1118b68d5dfae3e3f60664))


# [v0.2.22](https://github.com/aignostics/python-sdk/compare/v0.2.13..v0.2.22) - 2025-06-01

### ⛰️  Features

- *(QuPath)* Create project from results - ([17425dd](https://github.com/aignostics/python-sdk/commit/17425dd06354de11da507fa4b13714e97218781c))
- *(System)* Manipulate dotenv via CLI, including enable/disabling http proxy, enabling/disabling remote diagnostics - ([17425dd](https://github.com/aignostics/python-sdk/commit/17425dd06354de11da507fa4b13714e97218781c))
- *(notebook)* Extension page - ([17425dd](https://github.com/aignostics/python-sdk/commit/17425dd06354de11da507fa4b13714e97218781c))

### 🚜 Refactor

- *(application)* Cleanup - ([17425dd](https://github.com/aignostics/python-sdk/commit/17425dd06354de11da507fa4b13714e97218781c))

### ⚡ Performance

- *(GUI)* Significantly reduced bootup time, and page load performance - ([17425dd](https://github.com/aignostics/python-sdk/commit/17425dd06354de11da507fa4b13714e97218781c))

### 🎨 Styling

- *(QuPath)* Some polish for extension page - ([17425dd](https://github.com/aignostics/python-sdk/commit/17425dd06354de11da507fa4b13714e97218781c))

### ⚙️ Miscellaneous Tasks

- *(tests)* Improved coverage - ([17425dd](https://github.com/aignostics/python-sdk/commit/17425dd06354de11da507fa4b13714e97218781c))


# [v0.2.13](https://github.com/aignostics/python-sdk/compare/v0.2.12..v0.2.13) - 2025-05-27

### 🚜 Refactor

- Styling of ui theme - ([bcf3cfa](https://github.com/aignostics/python-sdk/commit/bcf3cfa2bc2d0cd0ff6482bb0b4fbebdd2dd3274))

### 📚 Documentation

- Reorder - ([cd60f97](https://github.com/aignostics/python-sdk/commit/cd60f975a1e92e9370276ca1ebad609c77c19f70))


# [v0.2.12](https://github.com/aignostics/python-sdk/compare/v0.2.11..v0.2.12) - 2025-05-26

### 🐛 Bug Fixes

- *(cli)* List runs count - ([98f9b6d](https://github.com/aignostics/python-sdk/commit/98f9b6d5e89d7f7aa1ca5f0631adfc952e9971fe))

### 🚜 Refactor

- Simplify, removing noruns - ([0b7e0e9](https://github.com/aignostics/python-sdk/commit/0b7e0e958ebad9f1ffe7f10c872561411fcdd240))

### 📚 Documentation

- Update - ([b9baeac](https://github.com/aignostics/python-sdk/commit/b9baeaca9986d6fcf4f07fd8e23521cdf91ce72a))
- Reorder - ([3d34173](https://github.com/aignostics/python-sdk/commit/3d34173e0f748648ecd5f51ce24951b049e21035))
- Fix broken link - ([0a2a7dd](https://github.com/aignostics/python-sdk/commit/0a2a7ddaf332e3eb7da1fc5cf4dd2f591ff6f3b3))


# [v0.2.11](https://github.com/aignostics/python-sdk/compare/v0.2.10..v0.2.11) - 2025-05-26

### 🎨 Styling

- Naming of navigation points - ([0b2a758](https://github.com/aignostics/python-sdk/commit/0b2a75818e1cd9a19a1c8d74dbeb66d3bb5c9001))


# [v0.2.10](https://github.com/aignostics/python-sdk/compare/v0.2.9..v0.2.10) - 2025-05-26


# [v0.2.9](https://github.com/aignostics/python-sdk/compare/v0.2.8..v0.2.9) - 2025-05-26

### 🚜 Refactor

- Fail properly when starting GUI while settings not configured - ([ffbf880](https://github.com/aignostics/python-sdk/commit/ffbf88018591c3e6d7975ea3db1af0b2f353a8cd))


# [v0.2.8](https://github.com/aignostics/python-sdk/compare/v0.2.7..v0.2.8) - 2025-05-26

### 🐛 Bug Fixes

- Force .json for geojson - ([c48b9dc](https://github.com/aignostics/python-sdk/commit/c48b9dceb2c5e6f20980a0992fbefb7b917175e8))


# [v0.2.7](https://github.com/aignostics/python-sdk/compare/v0.2.6..v0.2.7) - 2025-05-26

### 🚜 Refactor

- Simplify - ([fa1f7e6](https://github.com/aignostics/python-sdk/commit/fa1f7e628bd0e59752733fc54fc83d50ac885e38))

### ⚙️ Miscellaneous Tasks

- Adapt test to work with python 3.11 - ([06cb6a5](https://github.com/aignostics/python-sdk/commit/06cb6a5be1fe2c28bf2ddca81ea649931eebbe42))


# [v0.2.6](https://github.com/aignostics/python-sdk/compare/v0.2.5..v0.2.6) - 2025-05-26

### ⚙️ Miscellaneous Tasks

- Fix test - ([ba80312](https://github.com/aignostics/python-sdk/commit/ba803120ecb48cd512e0417c6d2d2dc59eede633))


# [v0.2.5](https://github.com/aignostics/python-sdk/compare/v0.2.4..v0.2.5) - 2025-05-26

### 📚 Documentation

- Update - ([1bcbc37](https://github.com/aignostics/python-sdk/commit/1bcbc37f28c0447bc27eb5e27fec21e155880fa5))


# [v0.2.4](https://github.com/aignostics/python-sdk/compare/v0.2.3..v0.2.4) - 2025-05-26

### ⚙️ Miscellaneous Tasks

- Fix test - ([514dd48](https://github.com/aignostics/python-sdk/commit/514dd48467bb7b8e753c88af9b17f0d88e9144c3))


# [v0.2.3](https://github.com/aignostics/python-sdk/compare/v0.2.2..v0.2.3) - 2025-05-26

### ⛰️  Features

- *(run_describe)* Show thumbnail per item - ([da5afa3](https://github.com/aignostics/python-sdk/commit/da5afa3f6fef3062c234e0c8d0187ae10ee54272))
- Download Results - ([da5afa3](https://github.com/aignostics/python-sdk/commit/da5afa3f6fef3062c234e0c8d0187ae10ee54272))

### 🚜 Refactor

- *(tests)* Simplify - ([da5afa3](https://github.com/aignostics/python-sdk/commit/da5afa3f6fef3062c234e0c8d0187ae10ee54272))
- Use native sorting provided by API - ([da5afa3](https://github.com/aignostics/python-sdk/commit/da5afa3f6fef3062c234e0c8d0187ae10ee54272))

### 📚 Documentation

- Improve consistency - ([da5afa3](https://github.com/aignostics/python-sdk/commit/da5afa3f6fef3062c234e0c8d0187ae10ee54272))
- Social preview for GH - ([da5afa3](https://github.com/aignostics/python-sdk/commit/da5afa3f6fef3062c234e0c8d0187ae10ee54272))
- Copyright notice - ([da5afa3](https://github.com/aignostics/python-sdk/commit/da5afa3f6fef3062c234e0c8d0187ae10ee54272))
- Additional pages for read the docs (rtd) - ([4976794](https://github.com/aignostics/python-sdk/commit/4976794804831d437b3356d426bbd4330aec91c6))

### ⚙️ Miscellaneous Tasks

- Add Andreas Kunft as co-author - ([da5afa3](https://github.com/aignostics/python-sdk/commit/da5afa3f6fef3062c234e0c8d0187ae10ee54272))
- Make tests more robust - ([da5afa3](https://github.com/aignostics/python-sdk/commit/da5afa3f6fef3062c234e0c8d0187ae10ee54272))
- Lint - ([da5afa3](https://github.com/aignostics/python-sdk/commit/da5afa3f6fef3062c234e0c8d0187ae10ee54272))
- Touch for GH - ([da5afa3](https://github.com/aignostics/python-sdk/commit/da5afa3f6fef3062c234e0c8d0187ae10ee54272))
- Touch - ([da5afa3](https://github.com/aignostics/python-sdk/commit/da5afa3f6fef3062c234e0c8d0187ae10ee54272))
- Make t4est_gui_run_download reliable relative to mixed version runs - ([da5afa3](https://github.com/aignostics/python-sdk/commit/da5afa3f6fef3062c234e0c8d0187ae10ee54272))
- Fix name - ([da5afa3](https://github.com/aignostics/python-sdk/commit/da5afa3f6fef3062c234e0c8d0187ae10ee54272))
- Bump - ([da5afa3](https://github.com/aignostics/python-sdk/commit/da5afa3f6fef3062c234e0c8d0187ae10ee54272))

### Breaking

- Change in metadata spec. for HETA application - ([da5afa3](https://github.com/aignostics/python-sdk/commit/da5afa3f6fef3062c234e0c8d0187ae10ee54272))


# [v0.2.2](https://github.com/aignostics/python-sdk/compare/v0.2.1..v0.2.2) - 2025-05-23

### 📚 Documentation

- Polish incl. updated assets - ([e51c05e](https://github.com/aignostics/python-sdk/commit/e51c05ea3160b017583c059e5eb85cd4b347bbad))


# [v0.2.1](https://github.com/aignostics/python-sdk/compare/v0.2.0..v0.2.1) - 2025-05-23

### 📚 Documentation

- Polish readme intro and oe - ([b6da3ab](https://github.com/aignostics/python-sdk/commit/b6da3abe86d37caf4eee98705893454de195aef4))
- Logo - ([ea32a37](https://github.com/aignostics/python-sdk/commit/ea32a3759049bde38813e4c07027aaa7d32759c7))



### ⛰️  Features

- Aignostics Launchpad, Aignostics CLI, Aignostics Client - ([2f97fb9](https://github.com/aignostics/python-sdk/commit/2f97fb92c41f533c1e1c6f1ccd5beed4777c5463))

### ⚙️ Miscellaneous Tasks

- Initial commit - ([a4ff238](https://github.com/aignostics/python-sdk/commit/a4ff23887d7ac1641aa9a58ece596b96165b0930))



* @helmut-hoffer-von-ankershoffen made their first contribution


