"""Nox configuration for development tasks."""

import json
import os
import re
from pathlib import Path

import nox
import tomli
from nox.command import CommandFailed

nox.options.reuse_existing_virtualenvs = True
nox.options.default_venv_backend = "uv"

NOT_SKIP_WITH_ACT = "not skip_with_act"
LATEXMK_VERSION_MIN = 4.86
LICENSES_JSON_PATH = "reports/licenses.json"
SBOM_CYCLONEDX_PATH = "reports/sbom.json"
SBOM_SPDX_PATH = "reports/sbom.spdx"
JUNIT_XML = "--junitxml=reports/junit.xml"
CLI_MODULE = "cli"
API_VERSIONS = ["v1"]
UTF8 = "utf-8"
PYTHON_VERSION = "3.13"
TEST_PYTHON_VERSIONS = ["3.11", "3.12", "3.13"]


def _setup_venv(session: nox.Session, all_extras: bool = True) -> None:
    """Install dependencies for the given session using uv."""
    args = ["uv", "sync", "--frozen"]
    if all_extras:
        args.append("--all-extras")
    session.run_install(
        *args,
        env={
            "UV_PROJECT_ENVIRONMENT": session.virtualenv.location,
            "UV_PYTHON": str(session.python),
        },
    )


def _is_act_environment() -> bool:
    """Check if running in GitHub ACT environment.

    Returns:
        bool: True if running in ACT environment, False otherwise.
    """
    return os.environ.get("GITHUB_WORKFLOW_RUNTIME") == "ACT"


def _format_json_with_jq(session: nox.Session, path: str) -> None:
    """Format JSON file using jq for better readability.

    Args:
        session: The nox session instance
        path: Path to the JSON file to format
    """
    with Path(f"{path}.tmp").open("w", encoding="utf-8") as outfile:
        session.run("jq", ".", path, stdout=outfile, external=True)
        session.run("mv", f"{path}.tmp", path, stdout=outfile, external=True)


@nox.session(python=[PYTHON_VERSION])
def lint(session: nox.Session) -> None:
    """Run code formatting checks, linting, and static type checking."""
    _setup_venv(session, True)
    session.run("ruff", "check", ".")
    session.run(
        "ruff",
        "format",
        "--check",
        ".",
    )
    session.run("mypy", "src")


@nox.session(python=[PYTHON_VERSION])
def audit(session: nox.Session) -> None:
    """Run security audit and license checks."""
    _setup_venv(session, True)

    # pip-audit to check for vulnerabilities
    session.run("pip-audit", "-f", "json", "-o", "reports/vulnerabilities.json")
    _format_json_with_jq(session, "reports/vulnerabilities.json")

    # pip-licenses to check for compliance
    pip_licenses_base_args = [
        "pip-licenses",
        "--with-system",
        "--with-authors",
        "--with-maintainer",
        "--with-url",
        "--with-description",
    ]

    # Filter by .license-types-allowed file if it exists
    allowed_licenses = []
    licenses_allow_file = Path(".license-types-allowed")
    if licenses_allow_file.exists():
        allowed_licenses = [
            line.strip()
            for line in licenses_allow_file.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.strip().startswith(("#", "//"))
        ]
        session.log(f"Found {len(allowed_licenses)} allowed licenses in .license-types-allowed")
    if allowed_licenses:
        allowed_licenses_str = ";".join(allowed_licenses)
        session.log(f"Using --allow-only with: {allowed_licenses_str}")
        pip_licenses_base_args.extend(["--partial-match", "--allow-only", allowed_licenses_str])

    # Generate CSV and JSON reports
    session.run(
        *pip_licenses_base_args,
        "--format=csv",
        "--order=license",
        "--output-file=reports/licenses.csv",
    )
    session.run(
        *pip_licenses_base_args,
        "--with-license-file",
        "--with-notice-file",
        "--format=json",
        "--output-file=" + LICENSES_JSON_PATH,
    )

    # Group by license type
    _format_json_with_jq(session, LICENSES_JSON_PATH)
    licenses_data = json.loads(Path(LICENSES_JSON_PATH).read_text(encoding="utf-8"))
    licenses_grouped: dict[str, list[dict[str, str]]] = {}
    licenses_grouped = {}
    for pkg in licenses_data:
        license_name = pkg["License"]
        package_info = {"Name": pkg["Name"], "Version": pkg["Version"]}
        if license_name not in licenses_grouped:
            licenses_grouped[license_name] = []
        licenses_grouped[license_name].append(package_info)
    Path("reports/licenses_grouped.json").write_text(
        json.dumps(licenses_grouped, indent=2),
        encoding="utf-8",
    )
    _format_json_with_jq(session, "reports/licenses_grouped.json")

    # SBOMs
    session.run("cyclonedx-py", "environment", "-o", SBOM_CYCLONEDX_PATH)
    _format_json_with_jq(session, SBOM_CYCLONEDX_PATH)

    # Generates an SPDX SBOM including vulnerability scanning
    session.run(
        "trivy",
        "fs",
        "uv.lock",
        "--include-dev-deps",
        "--scanners",
        "vuln",
        "--format",
        "spdx",
        "--output",
        SBOM_SPDX_PATH,
        external=True,
    )


def _generate_attributions(session: nox.Session, licenses_json_path: Path) -> None:
    """Generate ATTRIBUTIONS.md from licenses.json.

    Args:
        session: The nox session instance
        licenses_json_path: Path to the licenses.json file
    """
    attributions = "# Attributions\n\n"
    attributions += f"[//]: # (This file is generated by make docs from {LICENSES_JSON_PATH})\n\n"

    if not licenses_json_path.exists():
        attributions += "Please run `make audit` first to generate the necessary license information.\n"
        Path("ATTRIBUTIONS.md").write_text(attributions, encoding="utf-8")
        session.log("Generated placeholder ATTRIBUTIONS.md file - run 'make audit' to populate it properly")
        return

    licenses_data = json.loads(licenses_json_path.read_text(encoding="utf-8"))

    attributions += "We gratefully acknowledge the following open source projects and libraries "
    attributions += "that this project builds upon. Thank you to all these wonderful contributors!\n\n"

    attributions += """

## oe-python-template (0.17.10) - MIT License

🧠 Copier template to scaffold Python projects compliant with best practices and modern tooling.

* URL: https://github.com/helmut-hoffer-von-ankershoffen/oe-python-template
* Author(s): Helmut Hoffer von Ankershoffen <helmuthva@gmail.com>

### License Text

```
MIT License

Copyright (c) 2023 Imaging Data Commons

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## idc-index (0.9.0) - MIT License

Package to query and download data from an index of ImagingDataCommons.

* URL: https://github.com/ImagingDataCommons/idc-index
* Author(s): Andrey Fedorov <andrey.fedorov@gmail.com>, Vamsi Thiriveedhi<vthiriveedhi@mgh.harvard.edu>

### License Text

```
MIT License

Copyright (c) 2023 Imaging Data Commons

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
"""

    for pkg in licenses_data:
        attributions += _format_package_attribution(pkg)

    attributions = attributions.rstrip() + "\n"
    Path("ATTRIBUTIONS.md").write_text(attributions, encoding="utf-8")

    session.log("Generated ATTRIBUTIONS.md file")


def _format_package_attribution(pkg: dict) -> str:
    """Format attribution for a single package.

    Args:
        pkg: Package information dictionary

    Returns:
        str: Formatted attribution text for the package
    """
    name = pkg.get("Name", "Unknown")
    version = pkg.get("Version", "Unknown")
    license_name = pkg.get("License", "Unknown")
    authors = pkg.get("Author", "Unknown")
    maintainers = pkg.get("Maintainer", "")
    url = pkg.get("URL", "")
    description = pkg.get("Description", "")

    attribution = f"## {name} ({version}) - {license_name}\n\n"

    if description:
        attribution += f"{description}\n\n"

    if url:
        attribution += f"* URL: {url}\n"

    if authors and authors != "UNKNOWN":
        attribution += f"* Author(s): {authors}\n"

    if maintainers and maintainers != "UNKNOWN":
        attribution += f"* Maintainer(s): {maintainers}\n"

    attribution += "\n"

    license_text = pkg.get("LicenseText", "")
    if license_text and license_text != "UNKNOWN":
        attribution += "### License Text\n\n"
        # Sanitize backtick sequences to not escape the code block
        sanitized_license_text = license_text.replace("```", "~~~")
        attribution += f"```\n{sanitized_license_text}\n```\n\n"

    notice_text = pkg.get("NoticeText", "")
    if notice_text and notice_text != "UNKNOWN":
        attribution += "### Notice\n\n"
        # Sanitize backtick sequences to not escape the code block
        sanitized_notice_text = notice_text.replace("```", "~~~")
        attribution += f"```\n{sanitized_notice_text}\n```\n\n"

    return attribution


def _generate_readme(session: nox.Session) -> None:
    """Generate README.md from partials.

    Args:
        session: The nox session instance
    """
    preamble = "\n[//]: # (README.md generated from docs/partials/README_*.md)\n\n"
    header = Path("docs/partials/README_header.md").read_text(encoding="utf-8")
    main = Path("docs/partials/README_main.md").read_text(encoding="utf-8")
    platform = Path("docs/partials/README_platform.md").read_text(encoding="utf-8")
    glossary = Path("docs/partials/README_glossary.md").read_text(encoding="utf-8")
    footer = Path("docs/partials/README_footer.md").read_text(encoding="utf-8")
    readme_content = f"{preamble}{header}\n\n{main}\n\n{platform}\n\n{footer}\n\n{glossary}"
    Path("README.md").write_text(readme_content, encoding="utf-8")
    session.log("Generated README.md file from partials")


def _generate_openapi_schemas(session: nox.Session) -> None:
    """Generate OpenAPI schemas for different API versions in YAML and JSON formats.

    Args:
        session: The nox session instance
    """
    # Create directory if it doesn't exist
    Path("docs/source/_static").mkdir(parents=True, exist_ok=True)

    formats = {
        "yaml": {"ext": "yaml", "args": ["--output-format=yaml"]},
        "json": {"ext": "json", "args": ["--output-format=json"]},
    }

    for version in API_VERSIONS:
        for format_name, format_info in formats.items():
            output_path = Path(f"docs/source/_static/openapi_{version}.{format_info['ext']}")
            with output_path.open("w", encoding="utf-8") as f:
                cmd_args = [
                    "aignostics",
                    "system",
                    "openapi",
                    f"--api-version={version}",
                    *format_info["args"],
                ]
                session.run(*cmd_args, stdout=f, external=True)
            session.log(f"Generated API {version} OpenAPI schema in {format_name} format")


def _generate_cli_reference(session: nox.Session) -> None:
    """Generate CLI_REFERENCE.md.

    Args:
        session: The nox session instance
    """
    if CLI_MODULE:
        session.run(
            "typer",
            f"aignostics.{CLI_MODULE}",
            "utils",
            "docs",
            "--name",
            "aignostics",
            "--title",
            "CLI Reference",
            "--output",
            "CLI_REFERENCE.md",
            external=True,
        )


def _generate_api_reference(session: nox.Session) -> None:
    """Generate API_REFERENCE_v1.md and API_REFERENCE_v2.md.

    Args:
        session: The nox session instance

    Raises:
        FileNotFoundError: If the OpenAPI schema file for a version is not found
    """
    for version in API_VERSIONS:
        openapi_path = Path(f"docs/source/_static/openapi_{version}.yaml")

        if not openapi_path.exists():
            error_message = f"OpenAPI schema for {version} not found at {openapi_path}"
            raise FileNotFoundError(error_message)

        output_file = f"API_REFERENCE_{version}.md"
        session.run(
            "npx",
            "--yes",
            "widdershins",
            f"docs/source/_static/openapi_{version}.yaml",
            "--omitHeader",
            "--search",
            "false",
            "--language_tabs",
            "python:Python",
            "javascript:Javascript",
            "-o",
            f"API_REFERENCE_{version}.md",
            external=True,
        )
        session.log(f"Generated API_REFERENCE_{version}.md using widdershins")

        content = Path(output_file).read_text(encoding="utf-8")
        content = re.sub(r"<!--[\s\S]*?-->", "", content)
        content = re.sub(r"<h1 id=\"[^\"]+\">([\s\S]+?)</h1>", r"# \1", content)
        content = re.sub(r"<h2 id=\"[^\"]+\">([\s\S]+?)</h2>", r"## \1", content)
        content = re.sub(r"<h3 id=\"[^\"]+\">([\s\S]+?)</h3>", r"### \1", content)
        content = re.sub(r"<h4 id=\"[^\"]+\">([\s\S]+?)</h4>", r"#### \1", content)
        content = re.sub(r"<a href=\"([^\"]+)\">([\s\S]+?)</a>", r"[\2](\1)", content)
        content = re.sub(r"<a href=\"mailto:([^\"]+)\">([\s\S]+?)</a>", r"\2 (\1)", content)
        content = re.sub(r"<[^>]*>", "", content)
        content = re.sub(r"^\s*\n", "", content)
        Path(output_file).write_text(content, encoding="utf-8")
        session.log(f"Cleaned HTML from {output_file}")

        content = Path(output_file).read_text(encoding="utf-8")
        content = re.sub(r"^(#+)", r"\1#", content, flags=re.MULTILINE)
        content = content.rstrip() + "\n"
        Path(output_file).write_text(f"# API {version} Reference\n{content}", encoding="utf-8")
        session.log(f"Shifted headers in {output_file}")


def _generate_pdf_docs(session: nox.Session) -> None:
    """Generate PDF documentation using latexmk.

    Args:
        session: The nox session instance

    Raises:
        CommandFailed: If latexmk is not installed or not in PATH
        ValueError: If the installed latexmk version is outdated
        AttributeError: If parsing the latexmk version information fails
    """
    try:
        out = session.run("latexmk", "--version", external=True, silent=True)

        version_match = re.search(r"Version (\d+\.\d+\w*)", str(out))
        if not version_match:
            session.error("Could not determine latexmk version")

        version_str = version_match.group(1)

        # Parse version (handle cases like "4.86a")
        match = re.match(r"(\d+\.\d+)", version_str)
        if not match:
            session.error(f"Could not parse version number from '{version_str}'")
        base_version = match.group(1)

        if float(base_version) < LATEXMK_VERSION_MIN:
            message = f"latexmk version {version_str} is outdated. Please run 'brew upgrade mactex' to upgrade."
            raise ValueError(message)  # noqa: TRY301
        session.log(f"latexmk version {version_str} is sufficient")
        session.run("make", "-C", "docs", "latexpdf", external=True)
        session.log("PDF documentation generated and available at: docs/build/latex/aignostics.pdf")

    except CommandFailed as e:
        session.error(f"latexmk is not installed or not in PATH: {e}. Please run 'brew install mactex' to install")
    except (ValueError, AttributeError) as e:
        session.error(f"Failed to parse latexmk version information: {e}")


@nox.session(python=[PYTHON_VERSION])
def docs(session: nox.Session) -> None:
    """Build documentation and concatenate README.

    This function performs several documentation-related tasks:
    1. Concatenates partial README files into a single README.md
    2. Dumps OpenAPI schemas (v1 and v2) in both YAML and JSON formats
    3. Builds HTML, single HTML, and LaTeX documentation
    4. Optionally builds PDF documentation if "pdf" is in session arguments

    Args:
        session: The nox session instance

    Raises:
        CommandFailed: If latexmk is not installed or not in PATH
        ValueError: If the installed latexmk version is outdated
        AttributeError: If parsing the latexmk version information fails
    """
    _setup_venv(session, True)

    _generate_readme(session)
    _generate_cli_reference(session)
    _generate_openapi_schemas(session)
    _generate_api_reference(session)
    _generate_attributions(session, Path(LICENSES_JSON_PATH))

    # Build HTML docs
    session.run("make", "-C", "docs", "clean", external=True)
    session.run("make", "-C", "docs", "html", external=True)
    session.run("make", "-C", "docs", "singlehtml", external=True)
    session.run("make", "-C", "docs", "latex", external=True)

    if "pdf" in session.posargs:
        _generate_pdf_docs(session)


@nox.session(python=[PYTHON_VERSION], default=False)
def docs_pdf(session: nox.Session) -> None:
    """Setup dev environment post project creation."""  # noqa: DOC501
    _setup_venv(session, True)
    try:
        out = session.run("latexmk", "--version", external=True, silent=True)

        version_match = re.search(r"Version (\d+\.\d+\w*)", str(out))
        if not version_match:
            session.error("Could not determine latexmk version")

        version_str = version_match.group(1)

        # Parse version (handle cases like "4.86a")
        match = re.match(r"(\d+\.\d+)", version_str)
        if not match:
            session.error(f"Could not parse version number from '{version_str}'")
        base_version = match.group(1)

        if float(base_version) < LATEXMK_VERSION_MIN:
            message = f"latexmk version {version_str} is outdated. Please run 'brew upgrade mactex' to upgrade."
            raise ValueError(message)  # noqa: TRY301
        session.log(f"latexmk version {version_str} is sufficient")
        session.run("make", "-C", "docs", "latexpdf", external=True)

    except CommandFailed as e:
        session.error(f"latexmk is not installed or not in PATH: {e}. Please run 'brew install mactex' to install")
    except (ValueError, AttributeError) as e:
        session.error(f"Failed to parse latexmk version information: {e}")


def _prepare_coverage(session: nox.Session) -> None:
    """Clean coverage data unless keep-coverage flag is specified.

    Args:
        session: The nox session
    """
    if "--cov-append" not in session.posargs:
        session.run("rm", "-rf", ".coverage", external=True)


def _extract_custom_marker(posargs: list[str]) -> tuple[str | None, list[str]]:
    """Extract custom marker from pytest arguments.

    Args:
        posargs: Command line arguments

    Returns:
        Tuple of (custom_marker, filtered_posargs)
    """
    custom_marker = None
    new_posargs = []
    skip_next = False

    for i, arg in enumerate(posargs):
        if skip_next:
            skip_next = False
            continue

        if arg == "-m" and i + 1 < len(posargs):
            custom_marker = posargs[i + 1]
            skip_next = True
        elif arg != "-m" or i == 0 or posargs[i - 1] != "-m":
            new_posargs.append(arg)

    return custom_marker, new_posargs


def _get_report_type(session: nox.Session, custom_marker: str | None) -> str:
    """Generate report type string based on marker and Python version.

    Args:
        session: The nox session
        custom_marker: Optional pytest marker

    Returns:
        Report type string
    """
    # Create a report type based on marker
    report_type = "regular"
    if custom_marker:
        # Replace spaces and special chars with underscores
        report_type = re.sub(r"[\s\(\)]", "_", custom_marker).strip("_")

    # Add Python version to the report type
    if isinstance(session.python, str):
        python_version = f"py{session.python.replace('.', '')}"
    else:
        # Handle case where session.python is a list, bool, or None
        python_version = f"py{session.python!s}"

    return f"{python_version}_{report_type}"


def _inject_headline(headline: str, file_name: str) -> None:
    """Inject headline into file.

    - Checks if report file actually exists
    - If so, injects headline
    - If not, does nothing

    Args:
        headline: Headline to inject as first line
        file_name: Name of the report file
    """
    file = Path(file_name)
    if file.is_file():
        header = f"{headline}\n"
        content = file.read_text(encoding=UTF8)
        content = header + content
        file.write_text(content, encoding=UTF8)


def _run_pytest(
    session: nox.Session, test_type: str, custom_marker: str | None, posargs: list[str], report_type: str
) -> None:
    """Run pytest with specified arguments.

    Args:
        session: The nox session
        test_type: Type of test ('sequential' or 'not sequential')
        custom_marker: Optional pytest marker
        posargs: Additional pytest arguments
        report_type: Report type string for output files
    """
    is_sequential = test_type == "sequential"

    # Build base pytest arguments
    pytest_args = ["pytest", "--disable-warnings", JUNIT_XML]

    # Distribute tests across available CPUs if not sequential
    if not is_sequential:
        pytest_args.extend(["-n", "logical", "--dist", "loadgroup"])

    # Add act environment filter if needed
    if _is_act_environment():
        pytest_args.extend(["-k", NOT_SKIP_WITH_ACT])

    # Apply the appropriate marker
    marker_value = f"{test_type}"
    if custom_marker:
        marker_value += f" and ({custom_marker})"
    pytest_args.extend(["-m", marker_value])

    # Add additional arguments
    pytest_args.extend(posargs)

    # Report output as markdown for GitHub step summaries
    report_file_name = f"reports/pytest_{report_type}_{'sequential' if is_sequential else 'parallel'}.md"
    pytest_args.extend(["--md-report-output", report_file_name])

    # Remove report file if it exists,
    # as it's only generated for failing tests on the pytest run below
    report_file = Path(report_file_name)
    if report_file.is_file():
        report_file.unlink()

    # Run pytest with the constructed arguments
    session.run(*pytest_args)

    # Inject headline into the report file indicating the report type
    _inject_headline(f"# Failing tests with for test execution with {report_type}\n", report_file_name)


def _generate_coverage_report(session: nox.Session) -> None:
    """Generate coverage report in markdown format.

    Args:
        session: The nox session
    """
    coverage_report_file_name = "reports/coverage.md"
    with Path(coverage_report_file_name).open("w", encoding=UTF8) as outfile:
        session.run("coverage", "report", "--format=markdown", stdout=outfile)
        _inject_headline("# Coverage report", coverage_report_file_name)


def _cleanup_test_execution(session: nox.Session) -> None:
    """Clean up post test execution.

    - Docker containers created by pytest-docker removed

    Args:
        session: The nox session instance
    """
    session.run(
        "bash",
        "-c",
        (
            "docker compose ls --format json | jq -r '.[].Name' | "
            "grep ^pytest | xargs -I {} docker compose -p {} down --remove-orphans"
        ),
        external=True,
    )


@nox.session(python=TEST_PYTHON_VERSIONS)
def test(session: nox.Session) -> None:
    """Run tests with pytest."""
    _setup_venv(session)

    # Conditionally clean coverage data
    # Will remove .coverage file if --cov-append is not specified
    _prepare_coverage(session)

    # Extract custom markers from posargs if present
    custom_marker, filtered_posargs = _extract_custom_marker(session.posargs)

    # Determine report type from python version and custom marker
    report_type = _get_report_type(session, custom_marker)

    # Run parallel tests
    _run_pytest(session, "not sequential", custom_marker, filtered_posargs, report_type)

    # Run sequential tests
    if "--cov-append" not in filtered_posargs:
        filtered_posargs.extend(["--cov-append"])
    _run_pytest(session, "sequential", custom_marker, filtered_posargs, report_type)

    # Generate coverage report in markdown
    _generate_coverage_report(session)

    # Clean up post test execution
    _cleanup_test_execution(session)


@nox.session(python=["3.13"], default=False)
def setup(session: nox.Session) -> None:
    """Setup dev environment post project creation."""
    _setup_venv(session)
    session.run("ruff", "format", ".", external=True)
    git_dir = Path(".git")
    if git_dir.is_dir():
        session.run("echo", "found .git directory", external=True)
        session.run("touch", ".act-env-secret", external=True)
        session.run("pre-commit", "install", external=True)
        with Path(".secrets.baseline").open("w", encoding="utf-8") as out:
            session.run("detect-secrets", "scan", stdout=out, external=True)
        session.run("git", "add", ".", external=True)
        try:
            session.run("pre-commit", external=True)
        except Exception:  # noqa: BLE001
            session.log("pre-commit run failed, continuing anyway")
        session.run("git", "add", ".", external=True)


@nox.session(default=False)
def update_from_template(session: nox.Session) -> None:
    """Update from copier template."""
    if Path("copier.yaml").is_file() or Path("copier.yml").is_file():
        # Read the current version from pyproject.toml
        with Path("pyproject.toml").open("rb") as f:
            pyproject = tomli.load(f)
            current_version = pyproject["tool"]["bumpversion"]["current_version"]
            # In this case the project itself is the template
            session.run("copier", "copy", "-r", "HEAD", ".", ".", "--force", "--trust", "--skip-tasks", external=True)
            # Bump the version using the current version from pyproject.toml
            session.run("bump-my-version", "replace", "--new-version", current_version, "--allow-dirty", external=True)
    else:
        # In this case the template has been generated from a template
        session.run("copier", "update", "--trust", "--skip-answered", "--skip-tasks", external=True)

        # Schedule the lint session to run after this session completes
        session.notify("audit")
        session.notify("docs")
        session.notify("lint")


@nox.session(default=False)
def act(session: nox.Session) -> None:
    """Run GitHub Actions workflow locally with act."""
    session.run(
        "act",
        "-j",
        "test",
        "--env-file",
        ".act-env-public",
        "--secret-file",
        ".act-env-secret",
        "--container-architecture",
        "linux/amd64",
        "-P",
        "ubuntu-latest=catthehacker/ubuntu:act-latest",
        "--action-offline-mode",
        "--container-daemon-socket",
        "-",
        external=True,
    )


@nox.session(default=False)
def bump(session: nox.Session) -> None:
    """Bump version and push changes to git."""
    version_part = session.posargs[0] if session.posargs else "patch"

    # Check if the version_part is a specific version (e.g., 1.2.3)
    if re.match(r"^\d+\.\d+\.\d+$", version_part):
        session.run("bump-my-version", "bump", "--new-version", version_part, external=True)
    else:
        session.run("bump-my-version", "bump", version_part, external=True)

    # Push changes to git including tag created
    session.run("git", "push", "--follow-tags", external=True)


@nox.session()
def dist(session: nox.Session) -> None:
    """Build wheel and put in dist/."""
    session.run("uv", "build", external=True)
