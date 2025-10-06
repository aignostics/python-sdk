Always conform to the coding styles defined in CODE_STYLE.md in the root
directory of this repository when generating code.

Learn about tools to use in CONTRIBUTING.md in the root directory of this
repository.

For comprehensive agent guidance including architecture, common tasks, and
troubleshooting, read AGENTS.md in the root directory of this repository. This
is the primary reference for all AI coding agents working with this codebase.

For detailed module architecture and patterns, refer to CLAUDE.md files:
- Root CLAUDE.md for SDK overview
- src/aignostics/CLAUDE.md for module architecture
- Module-specific CLAUDE.md files for implementation details
- tests/CLAUDE.md for testing patterns

Key constraints:
- Python 3.11, 3.12, 3.13 support required
- Use uv package manager (not pip/poetry)
- Minimum 85% test coverage required
- MyPy strict mode enforced
- Conventional commit format: feat(module): description
- 120 character line length maximum
