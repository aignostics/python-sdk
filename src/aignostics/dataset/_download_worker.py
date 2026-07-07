"""IDC download worker — runs as a subprocess, invoked via --run-module or -m."""

import json
import sys
from pathlib import Path
from typing import cast

MIN_ARGS = 2  # program name + config file path


def main() -> None:
    """Read a JSON config file and run IDC download_from_selection."""
    if len(sys.argv) < MIN_ARGS:
        print("Usage: _download_worker <config_json_path>", file=sys.stderr)
        sys.exit(1)

    config_path = Path(sys.argv[1])
    if config_path.suffix != ".json" or not config_path.is_file() or not config_path.is_absolute():
        print(f"Invalid config file path: {config_path}", file=sys.stderr)
        sys.exit(1)

    config: dict[str, object] = json.loads(config_path.read_text())

    from aignostics.third_party.idc_index import IDCClient  # noqa: PLC0415

    client = IDCClient.client()
    client.fetch_index("sm_instance_index")
    kwarg_name = str(config["kwarg_name"])
    matched_ids = cast("list[str]", config["matched_ids"])
    client.download_from_selection(  # type: ignore[no-untyped-call]  # pyright: ignore[reportArgumentType]
        **{kwarg_name: matched_ids},  # pyright: ignore[reportArgumentType]
        downloadDir=str(config["download_dir"]),
        dirTemplate=str(config["dir_template"]),
        quiet=False,
        show_progress_bar=True,
        use_s5cmd_sync=True,
        dry_run=bool(config["dry_run"]),
    )


if __name__ == "__main__":
    main()
