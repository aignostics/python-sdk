# 🔬Aignostics Python SDK

## ⚠️ Deprecated

> The Aignostics Python SDK is deprecated and gets only bug fixes and security fixes until April 30, 2027. After that date, the repository and the PyPI project are archived. Use the Aignostics Platform REST API (https://platform.aignostics.com/api/v1/docs) or the Console (https://platform.aignostics.com).

### Migration

| You use | Use this instead |
| --- | --- |
| Python Library | Aignostics Platform REST API: [https://platform.aignostics.com/api/v1/docs](https://platform.aignostics.com/api/v1/docs) |
| CLI | Aignostics Platform REST API: [https://platform.aignostics.com/api/v1/docs](https://platform.aignostics.com/api/v1/docs) |
| Launchpad | Console: [https://platform.aignostics.com](https://platform.aignostics.com) |
| SDK upload command for the Console | Console: [https://platform.aignostics.com](https://platform.aignostics.com) |

#### Sharing runs

In the Console, open the run and select **Share**. Only the run's owners see the button: the user who submitted the run and the admins of its organization. Every share gives read-only access.

| You use | Use this instead |
| --- | --- |
| `aignostics application run share organization grant RUN_ID` | **Share**, then **Share with my organization** |
| `aignostics application run share organization grant RUN_ID ORG_ID` | **Share**, then paste the ID under **Another organization** |
| `aignostics application run share token create RUN_ID` | **Share**, then **Create link** under **Link**. The link expires after 1, 7, 30 or 90 days, or never. The Console shows it once. |
| `aignostics application run share status RUN_ID`, `share organization list`, `share token list` | **Share** lists who can open the run: its owners, the organizations and the links |
| `aignostics application run share organization revoke`, `share token revoke` | **Revoke** next to the organization or link in that list |
| `--share-token` on `run describe`, `run dump-metadata`, `run dump-item-metadata` and `run result download` | Open the link in a browser. After login it shows the run, its items and metadata, with the results to download and the slides in the viewer. |

[![License](https://img.shields.io/github/license/aignostics/python-sdk?logo=opensourceinitiative&logoColor=3DA639&labelColor=414042&color=A41831)](https://github.com/aignostics/python-sdk/blob/main/LICENSE)
[![Python Version](https://img.shields.io/pypi/pyversions/aignostics.svg?logo=python&color=204361&labelColor=1E2933)](https://pypi.org/project/aignostics/)
[![CI/CD](https://github.com/aignostics/python-sdk/actions/workflows/ci-cd.yml/badge.svg?branch=main)](https://github.com/aignostics/python-sdk/actions/workflows/ci-cd.yml)
[![Docs](https://img.shields.io/readthedocs/aignostics)](https://aignostics.readthedocs.io/en/latest/)
[![Quality Gate](https://sonarcloud.io/api/project_badges/measure?project=aignostics_python-sdk&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=aignostics_python-sdk)
[![Security](https://sonarcloud.io/api/project_badges/measure?project=aignostics_python-sdk&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=aignostics_python-sdk)
[![Maintainability](https://sonarcloud.io/api/project_badges/measure?project=aignostics_python-sdk&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=aignostics_python-sdk)
[![Coverage](https://codecov.io/gh/aignostics/python-sdk/graph/badge.svg?token=SX34YRP30E)](https://codecov.io/gh/aignostics/python-sdk)
[![Uptime](https://uptime.betterstack.com/status-badges/v2/monitor/1wbqa.svg)](https://aignostics.betteruptime.com)
