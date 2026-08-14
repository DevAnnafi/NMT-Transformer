import yaml
from pathlib import Path
from typing import Dict, Any
import requests
import os

def load_config(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def get_destination_path(entry: Dict[str, Any], raw_dir: str | Path, partial: bool = False) -> Path:
    filename = entry["archive"]
    base_path = Path(raw_dir) / filename
    
    if partial:
        return base_path.with_suffix(base_path.suffix + ".partial")
        
    return base_path

def download_corpus(entry, cfg) -> tuple[Path, bool]:
    dest = get_destination_path(entry, cfg["data"]["raw_dir"])
    partial = get_destination_path(entry, cfg["data"]["raw_dir"], partial=True)
    if dest.exists():
        return dest, False
    resp = requests.get(entry["url"], stream=True, timeout=cfg["download"]["timeout_seconds"] ) 
    resp.raise_for_status()
    with open(partial, "wb") as f:
        for chunk in resp.iter_content(chunk_size=cfg["download"]["chunk_size"]):
            f.write(chunk)
    actual = partial.stat().st_size
    expected = entry["expected_bytes"]
    if expected is not None and actual != expected:
        partial.unlink()
        raise ValueError(f"{entry['name']}: expected {expected} bytes, got {actual}")
    print(f"{entry['name']}: {actual} bytes (record this in config)")
    os.replace(partial, dest)
    return dest, True

