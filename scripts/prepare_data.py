import argparse

from src.data.download import (
    load_config
)

from src.data.clean import clean_corpus

from scripts.download_data import select_entries


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

def main():
    args = build_parser().parse_args()
    cfg = load_config(args.config)
    entries = select_entries(cfg, args)

    for entry in entries:
        name = entry["name"]

        if entry.get("format") == "sgml":
            print(f"{name}: sgml, extraction deferred to Day 2")
            continue

        print(f"{name}: cleaning...")
        stats = clean_corpus(entry, cfg)
        print(stats)


if __name__ == "__main__":
    main()


