## Introduction

The **Aignostics Platform** runs computational pathology applications — such as [Atlas H&E-TME](https://www.aignostics.com/products/he-tme-profiling-product), which analyzes the tumor microenvironment in H&E-stained tissue — on your whole slide images. The **Aignostics Python SDK** is how you work with it, through the interfaces below.

## Choose your interface

Choose your preferred interface for working with the Aignostics Platform. Each interface is designed for different user roles and use cases:

### 🖥️ Launchpad (Desktop Application)

| | |
|---|---|
| **What it is** | Graphical application for analyzing slides and viewing results in QuPath or Python notebooks |
| **Best for** | Pathologists and researchers who want to analyze slides without writing code |
| **Use when** | Running analyses on individual cases or small cohorts (1-20 slides) and exploring results interactively |
| **Get started** | <a href="https://aignostics.readthedocs.io/en/latest/get_started_launchpad.html">Get started with Launchpad</a> |

### ⌨️ CLI (Command-Line Interface)

| | |
|---|---|
| **What it is** | Terminal tool for scripting and automation |
| **Best for** | Bioinformaticians and technical researchers who work with terminal-based workflows |
| **Use when** | Processing large cohorts (10s-100s of slides), automating repetitive analyses, or integrating with computational pipelines |
| **Get started** | <a href="https://aignostics.readthedocs.io/en/latest/get_started_cli.html">Get started with the CLI</a> |

### 📚 Python Library

| | |
|---|---|
| **What it is** | Python library for programmatic access in scripts, notebooks, and applications |
| **Best for** | Data scientists and developers who want to integrate the platform into Python-based workflows |
| **Use when** | Building custom analysis pipeline in Python for repeated usage and processing large datasets (10s-1000s of slides) |
| **Get started** | <a href="https://aignostics.readthedocs.io/en/latest/get_started_library.html">Get started with the Python Library</a> |

### 🔌 REST API (Direct HTTP)

| | |
|---|---|
| **What it is** | The Platform's REST API at `https://platform.aignostics.com/api/v1`, called directly over HTTPS |
| **Best for** | Developers integrating from another language or an existing pipeline, without depending on the Python SDK |
| **Use when** | Building a service or workflow outside Python, or generating your own client from the OpenAPI document |
| **Get started** | <a href="https://aignostics.readthedocs.io/en/latest/get_started_api.html">Get started with the API</a> |

### 🤖 MCP Server (AI Agent Integration)

| | |
|---|---|
| **What it is** | Model Context Protocol server that exposes SDK functionality to AI agents like Claude |
| **Best for** | Users who want AI assistants to help with platform operations |
| **Use when** | Working with Claude Desktop or other MCP-compatible AI tools to manage datasets, submit runs, or query results |
| **Get started** | <a href="https://aignostics.readthedocs.io/en/latest/get_started_mcp.html">Get started with the MCP Server</a> |

> 💡 Each interface has its own step-by-step guide (linked above) that includes installation. Launchpad and the CLI handle authentication for you; the Python Library guide covers credential setup.

## Next Steps

The best next step is to **run your first analysis** end to end.

New here? Start with the [Get started with Launchpad](https://aignostics.readthedocs.io/en/latest/get_started_launchpad.html) guide — it walks you through signing up, installing, and running [Atlas H&E-TME](https://www.aignostics.com/products/he-tme-profiling-product) on a public example slide, then viewing the results in QuPath, with no coding required. Prefer the terminal or Python? Use the [Get started with the CLI](https://aignostics.readthedocs.io/en/latest/get_started_cli.html) or [Get started with the Python Library](https://aignostics.readthedocs.io/en/latest/get_started_library.html) guide instead.

Once you've run your first analysis:

- **Understand the platform**: Read the [Aignostics Platform Overview](https://aignostics.readthedocs.io/en/latest/platform_overview.html) for architecture and core concepts.
- **Go deeper**: See the [CLI reference](https://aignostics.readthedocs.io/en/latest/cli_reference.html) and [Python Library reference](https://aignostics.readthedocs.io/en/latest/lib_reference.html).
- **Get support**: Contact [support@aignostics.com](mailto:support@aignostics.com) or browse the [full documentation](https://aignostics.readthedocs.io/en/latest/).

## We take quality and security seriously

We know you take **quality** and **security** as seriously as we do. That's why
the Aignostics Python SDK is built following best practices and with full
transparency. This includes (1) making the complete
[source code of the SDK
available on GitHub](https://github.com/aignostics/python-sdk/), maintaining a
(2)
[A-grade code quality](https://sonarcloud.io/summary/new_code?id=aignostics_python-sdk)
with [high test coverage](https://app.codecov.io/gh/aignostics/python-sdk) in
all releases, (3) achieving
[A-grade security](https://sonarcloud.io/summary/new_code?id=aignostics_python-sdk)
with
[active scanning of dependencies](https://github.com/aignostics/python-sdk/issues/4),
and (4) providing
[extensive documentation](https://aignostics.readthedocs.io/en/latest/). Read
more about how we achieve
[operational excellence](https://aignostics.readthedocs.io/en/latest/operational_excellence.html) and
[security](https://aignostics.readthedocs.io/en/latest/security.html).
