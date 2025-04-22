"""National Institute of Cancer (NIC) Image Data Commons (IDC) module."""

from importlib.util import find_spec

if find_spec("idc_index"):
    from ._cli import cli

    __all__ = [
        "cli",
    ]
