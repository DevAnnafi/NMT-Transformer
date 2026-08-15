import argparse
import sys

from src.data.download import (
    count_lines,
    download_corpus,
    extract_corpus,
    load_config,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Download and extract WMT14 corpora.",
    )
    parser.add_argument(
        "--config",
        default="configs/base.yaml",
        help="Path to the YAML config file",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--corpus",
        metavar="NAME",
        help="Name of a single corpus to download",
    )
    group.add_argument(
        "--all",
        action="store_true",
        help="Download every corpus in the config",
    )
    return parser


def select_entries(cfg, args) -> list[dict]:
    corpora = cfg["data"]["corpora"]
    if args.all:
        return corpora

    matches = [e for e in corpora if e["name"] == args.corpus]
    if matches:
        return matches

    names = ", ".join(e["name"] for e in corpora)
    print(f"error: unknown corpus '{args.corpus}'", file=sys.stderr)
    print(f"available: {names}", file=sys.stderr)
    sys.exit(1)


def main():
    args = build_parser().parse_args()
    cfg = load_config(args.config)
    entries = select_entries(cfg, args)

    for entry in entries:
        name = entry["name"]

        path, fetched = download_corpus(entry, cfg)
        if fetched:
            print(f"{name}: fetched {path.stat().st_size} bytes")
        else:
            print(f"{name}: already present")

        if entry.get("format") == "sgml":
            print(f"{name}: sgml, extraction deferred to Day 2")
            continue

        src_file, tgt_file = extract_corpus(entry, cfg)
        src_count = count_lines(src_file)
        tgt_count = count_lines(tgt_file)

        if src_count == tgt_count:
            print(f"{name}: {src_count} pairs")
        else:
            print(f"{name}: MISALIGNED — src {src_count}, tgt {tgt_count}")


if __name__ == "__main__":
    main()