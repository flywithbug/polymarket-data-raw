#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path


def main() -> int:
    root_dir = Path(__file__).resolve().parent.parent
    scripts_dir = root_dir / "scripts"

    # Keep generation behavior aligned with existing pipeline:
    # sports_types (+ sports_config.yaml) -> nav/sports.json
    subprocess.run(["python3", str(scripts_dir / "merge_sports_types.py")], check=True)

    nav_dir = root_dir / "nav"
    sports_file = nav_dir / "sports.json"
    sports_cfg_file = nav_dir / "sports_types" / "sports_config.yaml"
    root_tags_dir = nav_dir / "root_tags"
    sports_tag_out_file = root_tags_dir / "sports.json"

    sports_data = json.loads(sports_file.read_text(encoding="utf-8"))
    try:
        import yaml
    except ImportError as e:
        raise RuntimeError("PyYAML is required: pip install pyyaml") from e

    sports_cfg = {}
    if sports_cfg_file.exists():
        sports_cfg = yaml.safe_load(sports_cfg_file.read_text(encoding="utf-8")) or {}

    sports_tag_meta = sports_cfg.get("sportsTagMeta") or {}
    sports_tag = None
    if sports_tag_out_file.exists():
        existing = json.loads(sports_tag_out_file.read_text(encoding="utf-8"))
        if isinstance(existing, dict):
            sports_tag = dict(existing)

    if sports_tag_meta:
        sports_tag = dict(sports_tag_meta)
    elif sports_tag is None:
        sports_tag = {
            "id": "1",
            "label": "Sports",
            "slug": "sports",
            "forceShow": False,
        }

    sports_tag["children"] = sports_data.get("children", [])

    root_tags_dir.mkdir(parents=True, exist_ok=True)
    sports_tag_out_file.write_text(
        json.dumps(sports_tag, ensure_ascii=False, indent=4) + "\n",
        encoding="utf-8",
    )

    print(f"[OK] Generated: {sports_tag_out_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
