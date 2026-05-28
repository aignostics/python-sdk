# Migrating from v1 to v2

v2 of the Aignostics Python SDK introduces `aignostics-sdk`, a slim distribution that contains
only the platform API client and core utilities. The full `aignostics` package now depends on
`aignostics-sdk` and delegates platform/utils functionality to it.

This is a **breaking change** for anyone importing `aignostics.platform` or `aignostics.utils`
directly.

## What changed

The `platform` and `utils` modules (and `constants`) have moved to a separate PyPI package called
`aignostics-sdk`. Their Python namespace has changed from `aignostics.*` to `aignostics_sdk.*`.

| v1 (Python namespace) | v2 (Python namespace) |
|-----------------------|-----------------------|
| `aignostics.platform` | `aignostics_sdk.platform` |
| `aignostics.utils` | `aignostics_sdk.utils` |
| `aignostics.constants` | `aignostics_sdk.constants` |

All other modules (`application`, `wsi`, `dataset`, `bucket`, `qupath`, `notebook`, `gui`,
`system`) remain under the `aignostics.*` namespace and are only available in the full package.

## Import path changes

Update your Python imports as follows:

| v1 import | v2 import |
|-----------|-----------|
| `from aignostics.platform import Client` | `from aignostics_sdk.platform import Client` |
| `from aignostics.platform import InputItem, InputArtifact` | `from aignostics_sdk.platform import InputItem, InputArtifact` |
| `from aignostics.utils import BaseService` | `from aignostics_sdk.utils import BaseService` |
| `from aignostics.utils import Health` | `from aignostics_sdk.utils import Health` |
| `from aignostics.utils import locate_implementations` | `from aignostics_sdk.utils import locate_implementations` |
| `from aignostics.constants import INTERNAL_ORGS` | `from aignostics_sdk.constants import INTERNAL_ORGS` |
| `from aignostics import platform` | `from aignostics_sdk import platform` |

## Installation changes

### If you only use the API client

Replace the full package with the slim package for a significantly smaller install footprint:

```bash
# v1
pip install aignostics

# v2 — slim install
pip install aignostics-sdk
```

The slim `aignostics-sdk` package includes only `platform`, `utils`, and `constants`.
It has no dependency on OpenSlide, wsidicom, boto3, Google Cloud Storage, or other heavy
libraries required by the WSI and dataset modules.

### If you use the full SDK

The install command is **unchanged**:

```bash
pip install aignostics
```

The full package automatically pulls in `aignostics-sdk` as a dependency, so all
`aignostics_sdk.*` imports work after installing `aignostics`.

## CLI changes

The `aignostics` CLI command is **unchanged**. A new `aignostics-sdk` CLI entry point is
registered when the slim package is installed:

```bash
# Slim install — available commands
aignostics-sdk user login
aignostics-sdk user logout
aignostics-sdk user whoami
aignostics-sdk sdk run-metadata-schema
aignostics-sdk sdk item-metadata-schema

# Full install — unchanged command, full feature set
aignostics user login
aignostics application list
aignostics wsi inspect slide.svs
```

## Health checks using the full SDK

In v1, the health check import was:

```python
# v1
from aignostics.system import Service as SystemService

health = SystemService().health()
```

This is **unchanged** in v2 — `system` remains in the `aignostics` namespace:

```python
# v2 — same as v1
from aignostics.system import Service as SystemService

health = SystemService().health()
```

## Quick migration checklist

1. Update `from aignostics.platform import ...` to `from aignostics_sdk.platform import ...`
2. Update `from aignostics.utils import ...` to `from aignostics_sdk.utils import ...`
3. Update `from aignostics.constants import ...` to `from aignostics_sdk.constants import ...`
4. If you only need the API client, switch `pip install aignostics` to `pip install aignostics-sdk`
5. If you use the full SDK, keep `pip install aignostics` — no pip change needed
