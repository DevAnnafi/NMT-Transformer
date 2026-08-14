from src.data.download import load_config, download_corpus
import argparse
import sys

parser = argparse.ArgumentParser(
    description="NMT-Transformer"
)

parser.add_argument(
    '--config',
    default='configs/base.yaml',
    help='Path to the YAML config file',
)

group = parser.add_mutually_exclusive_group(required=True)

group.add_argument(
    '--corpus',
    metavar='NAME',
    help= 'Name of a single corpus to download',
)

group.add_argument(
    '--all',
    action='store_true',  
)

args = parser.parse_args()

print(args)

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

args = parser.parse_args()
cfg = load_config(args.config)
entries = select_entries(cfg, args)
for entry in entries:
    path, fetched = download_corpus(entry, cfg)
    if fetched:
        print(f"{entry['name']}: fetched {path.stat().st_size} bytes")
    else:
        print(entry["name"], "already present")
    