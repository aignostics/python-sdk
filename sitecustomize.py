"""Site customization module to enable test coverage computation in subprocesses."""

try:
    import coverage

    coverage.process_startup()
except ImportError:
    pass
