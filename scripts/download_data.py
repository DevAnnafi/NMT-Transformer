from src.data.download import load_config, download_corpus
import argparse

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