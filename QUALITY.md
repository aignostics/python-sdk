# Quality Management

TODO (Helmut): Provide more details on OE:

1. [Transparent test coverage](https://app.codecov.io/gh/aignostics/python-sdk)
   including unit and E2E tests (reported on Codecov)
2. Matrix tested with
   [multiple python versions](https://github.com/aignostics/python-sdk/blob/main/noxfile.py)
   to ensure compatibility (powered by [Nox](https://nox.thea.codes/en/stable/))
3. Compliant with modern linting and formatting standards (powered by
   [Ruff](https://github.com/astral-sh/ruff))
4. Up-to-date dependencies (monitored by
   [Renovate](https://github.com/renovatebot/renovate) and
   [Dependabot](https://github.com/aignostics/python-sdk/security/dependabot))
5. [A-grade code quality](https://sonarcloud.io/summary/new_code?id=aignostics_python-sdk)
   in security, maintainability, and reliability with low technical debt and
   codesmell (verified by SonarQube)
6. Additional code security checks using
   [CodeQL](https://github.com/aignostics/python-sdk/security/code-scanning)
7. Documented [Security Policy](SECURITY.md)
