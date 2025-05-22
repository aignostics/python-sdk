# Security Policy

## Reporting Security Issues

If you discover a security vulnerability in Aignostics Python SDK, please [report it here](https://github.com/aignostics/python-sdk/security/advisories/new).

We take all security reports seriously. Upon receiving a security report, we will:
1. Confirm receipt of the vulnerability report
2. Investigate the issue
3. Work on a fix
4. Release a security update

## Supported Versions

We currently provide security updates for the latest minor version.

## Automated Security Analysis

Aignostics Python SDK employs several automated tools to continuously monitor and improve security:

### 1. Vulnerability Scanning

a. **[GitHub Dependabot](https://github.com/dependabot)**: Monitors dependencies for vulnerabilities pre and post release on GitHub. [Dependendabot alerts](https://github.com/aignostics/python-sdk/security/dependabot) published.
b. **[Renovate](https://www.mend.io/renovate/)**: Monitors dependencies for vulnerabilities pre and post release on GitHub. [Dependency Dashboard](https://github.com/aignostics/python-sdk/issues?q=is%3Aissue%20state%3Aopen%20Dependency%20Dashboard) published.
c. **[pip-audit](https://pypi.org/project/pip-audit/)**: Pre commit to GitHub scans Python dependencies for known vulnerabilities using data from the [Python Advisory Database](https://github.com/pypa/advisory-database). `vulnerabilities.json` published [per release](https://github.com/aignostics/python-sdk/releases).
d. **[trivy](https://trivy.dev/latest/)**: Pre commit to GitHub scans Python dependencies for known vulnerabilities using data from [GitHub Advisory Database](https://github.com/advisories?query=ecosystem%3Apip) and [OSV.dev](https://osv.dev/list?q=&ecosystem=PyPI). `sbom.spdx` published [per release](https://github.com/aignostics/python-sdk/releases).

### 2. License Compliance Checks and Software Bill of Materials (SBOM)

a. **[pip-licenses](https://pypi.org/project/pip-licenses/)**: Inspects and matches the licenses of all dependencies with allow list to ensure compliance with licensing requirements and avoid using components with problematic licenses. `licenses.csv`, `licenses.json` and `licenses_grouped.json` published [per release](https://github.com/aignostics/python-sdk/releases).
a. **[cyclonedx-py](https://github.com/CycloneDX/cyclonedx-python)**: Generates Software Bill of Materials (SBOM) in [CycloneDX](https://cyclonedx.org/) format, listing all components and dependencies used in the project. `sbom.json` published [per release](https://github.com/aignostics/python-sdk/releases).
d. **[trivy](https://trivy.dev/latest/)**: Generates Software Bill of Materials (SBOM) in [SPDX](https://spdx.dev/) format, listing all components and dependencies used in the project. `sbom.spdx` published [per release](https://github.com/aignostics/python-sdk/releases).

### 3. Static Code Analysis

a. **[GitHub CodeQL](https://codeql.github.com/)**: Analyzes code for common vulnerabilities and coding errors using GitHub's semantic code analysis engine. [Code scanning results](https://github.com/aignostics/python-sdk/security/code-scanning) published.
b. **[SonarQube](https://www.sonarsource.com/products/sonarcloud/)**: Performs comprehensive static code analysis to detect code quality issues, security vulnerabilities, and bugs. [Security hotspots](https://sonarcloud.io/project/security_hotspots?id=aignostics_python-sdk) published.

### 4. Secret Detection
a. **[GitHub Secret scanning](https://docs.github.com/en/code-security/secret-scanning/introduction/about-secret-scanning)**: Automatically scans for secrets in the codebase and alerts if any are found. [Secret scanning alerts](https://github.com/aignostics/python-sdk/security/secret-scanning) published.
b. **[Yelp/detect-secrets](https://github.com/Yelp/detect-secrets)**: Pre-commit hook and automated scanning to prevent accidental inclusion of secrets or sensitive information in commits. [Pre-Commit hook](https://github.com/aignostics/python-sdk/blob/main/.pre-commit-config.yaml) published.

## Security Best Practices

We follow these security best practices:
1. Regular dependency updates
2. Comprehensive test coverage
3. Code review process for changes by external contributors
4. Automated CI/CD pipelines including security checks
5. Adherence to Python security best practices

We promote security awareness among contributors and users:
1. We indicate security as a priority in our
   [code style guide](CODE_STYLE.md), to be followed by human and agentic
   contributors as mandatory
2. We publish our security posture in SECURITY.md (this document), encouraring
   users to report vulnerabilities.

## Security Compliance

For questions about security compliance or for more details about our security practices, please contact helmut@aignostics.com.
