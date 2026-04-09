from __future__ import annotations

import argparse
from pathlib import Path

from am_bridge.config import derive_default_output_paths, load_cli_config, resolve_input_path
from am_bridge.generators import generate_page_conversion_spec
from am_bridge.pipeline import analyze_file


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze a legacy XML page file.")
    parser.add_argument("input", help="Path, relative path, or file name of a legacy XML page file")
    parser.add_argument(
        "--config",
        help="Optional CLI config path. Defaults to am-bridge.config.json in the current workspace.",
    )
    parser.add_argument("-o", "--output", help="Optional output path for JSON result")
    parser.add_argument(
        "--page-spec-output",
        help="Optional output path for generated page conversion spec markdown",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    config = load_cli_config(args.config)
    input_path = resolve_input_path(args.input, config)
    default_json_path, default_spec_path = derive_default_output_paths(input_path, config)

    model = analyze_file(input_path)
    output_text = model.to_json()

    json_output_path = Path(args.output).resolve() if args.output else (
        default_json_path if config.configPath is not None else None
    )
    page_spec_output_path = Path(args.page_spec_output).resolve() if args.page_spec_output else (
        default_spec_path if config.configPath is not None else None
    )

    if json_output_path is not None:
        json_output_path.parent.mkdir(parents=True, exist_ok=True)
        json_output_path.write_text(output_text, encoding="utf-8")
        print(f"JSON saved to: {json_output_path}")
    else:
        print(output_text)

    if page_spec_output_path is not None:
        page_spec_output_path.parent.mkdir(parents=True, exist_ok=True)
        page_spec_output_path.write_text(
            generate_page_conversion_spec(model),
            encoding="utf-8",
        )
        print(f"Page spec saved to: {page_spec_output_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
