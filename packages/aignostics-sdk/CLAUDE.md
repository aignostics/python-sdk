# CLAUDE.md - aignostics-sdk (Slim Package)

This is the **slim distribution** of the Aignostics SDK, published to PyPI as `aignostics-sdk`.
It contains only the platform API client and core utilities — no WSI processing, no GUI, no dataset
downloads, no cloud storage abstraction.

## What this package contains

| Module | Purpose |
|--------|---------|
| `aignostics_sdk.platform` | OAuth 2.0 authentication, API client, SDK metadata tracking, run/item resources |
| `aignostics_sdk.utils` | Core infrastructure: DI container, logging, settings, `BaseService`, health checks, user agent |
| `aignostics_sdk.constants` | Shared constants (e.g. `INTERNAL_ORGS`) |

## Python namespace

All public APIs are under the `aignostics_sdk.*` namespace:

```python
from aignostics_sdk.platform import Client
from aignostics_sdk.utils import BaseService, Health
from aignostics_sdk.constants import INTERNAL_ORGS
```

> This is a **breaking change** from v1, where these modules lived under `aignostics.platform`,
> `aignostics.utils`, and `aignostics.constants`.
> See the [v2 migration guide](../../docs/source/migration.md) for the full import mapping.

## CLI entry point

The slim package registers the `aignostics-sdk` CLI entry point (in addition to the `aignostics`
entry point provided by the full package):

```bash
# Slim install only
aignostics-sdk user login
aignostics-sdk user logout
aignostics-sdk user whoami
aignostics-sdk sdk run-metadata-schema
aignostics-sdk sdk item-metadata-schema
```

The `aignostics` CLI (full package) provides the same commands plus all heavy-module commands
(`application`, `wsi`, `dataset`, `bucket`, etc.).

## Source history

The source for this package was migrated from:

- `src/aignostics/platform/` → `packages/aignostics-sdk/src/aignostics_sdk/platform/`
- `src/aignostics/utils/` → `packages/aignostics-sdk/src/aignostics_sdk/utils/`
- `src/aignostics/constants.py` → `packages/aignostics-sdk/src/aignostics_sdk/constants.py`

## Dependencies

Minimal by design — no OpenSlide, wsidicom, boto3, google-cloud-storage, or other heavy libraries.
Runtime dependencies are limited to what the platform API client strictly needs (httpx/requests,
pydantic, tenacity, etc.).

## Module architecture

This package follows the same three-layer pattern as the rest of the SDK:

```text
aignostics_sdk/
├── platform/
│   ├── _service.py      # Business logic (API client, OAuth, caching, retry)
│   ├── _cli.py          # CLI: user login/logout/whoami, sdk metadata-schema
│   ├── _settings.py     # Pydantic settings
│   └── CLAUDE.md        # Platform module documentation
├── utils/
│   ├── _service.py      # BaseService, Health, DI container
│   ├── _cli.py          # CLI: mcp run/list-tools
│   ├── _settings.py     # Pydantic settings
│   └── CLAUDE.md        # Utils module documentation
└── constants.py         # Shared constants
```

## Testing

Tests for this package live alongside the source in the shared `tests/` tree at the repo root.
Run them with the standard test commands documented in the root `CLAUDE.md`.
