import yaml
from pathlib import Path
from typing import Dict, Any

def load_config(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def get_destination_path(entry: Dict[str, Any], raw_dir: str | Path, partial: bool = False) -> Path:
    filename = entry["archive"]
    base_path = Path(raw_dir) / filename
    
    if partial:
        return base_path.with_suffix(base_path.suffix + ".partial")
        
    return base_path

