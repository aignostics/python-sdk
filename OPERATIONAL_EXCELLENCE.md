# Operational Excellence

> 🧠 This project was scaffolded using the template [oe-python-template](https://github.com/helmut-hoffer-von-ankershoffen/oe-python-template) with [copier](https://copier.readthedocs.io/), thereby applying the following toolchain:

1. Linting with [Ruff](https://github.com/astral-sh/ruff)
2. Static type checking with [mypy](https://mypy.readthedocs.io/en/stable/)
3. Complete set of [pre-commit](https://pre-commit.com/) hooks including [detect-secrets](https://github.com/Yelp/detect-secrets) and [pygrep](https://github.com/pre-commit/pygrep-hooks)
4. Unit and E2E testing with [pytest](https://docs.pytest.org/en/stable/) including parallel test execution
5. Matrix testing in multiple environments with [nox](https://nox.thea.codes/en/stable/)
6. Test coverage reported with [Codecov](https://codecov.io/) and published as release artifact
7. CI/CD pipeline automated with [GitHub Actions](https://github.com/features/actions) with parallel and reusable workflows, including scheduled testing, release automation, and multiple reporting channels and formats
8. CI/CD pipeline can be run locally with [act](https://github.com/nektos/act)
9. Code quality and security checks with [SonarQube](https://www.sonarsource.com/products/sonarcloud) and [GitHub CodeQL](https://codeql.github.com/)
10. Dependency monitoring and vulnerability scanning with [pip-audit](https://pypi.org/project/pip-audit/), [trivy](https://trivy.dev/latest/), [Renovate](https://github.com/renovatebot/renovate), and [GitHub Dependabot](https://docs.github.com/en/code-security/getting-started/dependabot-quickstart-guide)
11. Error monitoring and profiling with [Sentry](https://sentry.io/)  (optional)
12. Logging and metrics with [Logfire](https://logfire.dev/) (optional)
13. Prepared for uptime monitoring and scheduled tests with [betterstack](https://betterstack.com/) or alternatives
14. Licenses of dependencies extracted with [pip-licenses](https://pypi.org/project/pip-licenses/), matched with allow list, and published as release artifacts in CSV and JSON format for further compliance checks
15. Generation of attributions from extracted licenses
16. Software Bill of Materials (SBOM) generated in [CycloneDX](https://cyclonedx.org/) and [SPDX](https://spdx.dev/) formats with [cyclonedx-python](https://github.com/CycloneDX/cyclonedx-python) resp. [trivy](https://trivy.dev/latest/), published as release artifacts
17. Version and release management with [bump-my-version](https://callowayproject.github.io/bump-my-version/)
18. Changelog and release notes generated with [git-cliff](https://git-cliff.org/)
19. Documentation generated with [Sphinx](https://www.sphinx-doc.org/en/master/) including reference documentation for the library, CLI, and API
20. Documentation published to [Read The Docs](https://readthedocs.org/) including generation of PDF and single page HTML versions
21. Documentation including dynamic badges, setup instructions, contribution guide and security policy
22. Interactive OpenAPI specification with [Swagger](https://swagger.io/)
23. Python package published to [PyPI](https://pypi.org/)
24. Multi-stage build of fat (all extras) and slim (no extras) multi-arch (arm64 and amd64) Docker images, running non-root within immutable container
25. Docker images published to [Docker.io](https://hub.docker.com/) and [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry) with [artifact attestations](https://docs.github.com/en/actions/security-for-github-actions/using-artifact-attestations/using-artifact-attestations-to-establish-provenance-for-builds)
26. One-click development environments with [Dev Containers](https://code.visualstudio.com/docs/devcontainers/containers) and [GitHub Codespaces](https://github.com/features/codespaces)
27. Settings for use with [VSCode](https://code.visualstudio.com/)
28. Settings and custom instructions for use with [GitHub Copilot](https://docs.github.com/en/copilot/customizing-copilot/adding-repository-custom-instructions-for-github-copilot)
