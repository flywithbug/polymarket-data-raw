#!/usr/bin/env python3
import json
from pathlib import Path


def main() -> int:
    root_dir = Path(__file__).resolve().parent.parent
    nav_dir = root_dir / "nav"

    root_cfg_file = nav_dir / "root_config.yaml"
    root_tags_dir = nav_dir / "root_tags"
    out_file = nav_dir / "nav_root.json"

    if not root_tags_dir.exists():
        raise FileNotFoundError(f"Missing directory: {root_tags_dir}")

    try:
        import yaml
    except ImportError as e:
        raise RuntimeError("PyYAML is required: pip install pyyaml") from e

    cfg = {}
    if root_cfg_file.exists():
        cfg = yaml.safe_load(root_cfg_file.read_text(encoding="utf-8")) or {}

    visible_root_slugs = cfg.get("visibleRootSlugs") or []
    strict_missing = bool(cfg.get("strictMissingTagFile", True))
    event_path = cfg.get("eventPath", "https://gamma-api.polymarket.com/events/keyset")

    if visible_root_slugs:
        target_slugs = visible_root_slugs
    else:
        target_slugs = sorted([p.stem for p in root_tags_dir.glob("*.json")])

    merged_root_tags = []
    for slug in target_slugs:
        tag_file = root_tags_dir / f"{slug}.json"
        if not tag_file.exists():
            if strict_missing:
                raise FileNotFoundError(f"Missing root tag file: {tag_file}")
            continue
        tag_data = json.loads(tag_file.read_text(encoding="utf-8"))
        if not isinstance(tag_data, dict):
            raise ValueError(f"Invalid tag json (expect object): {tag_file}")
        merged_root_tags.append(tag_data)

    merged = {
        "rootTag": merged_root_tags,
        "eventPath": event_path,
    }

    out_file.write_text(json.dumps(merged, ensure_ascii=False, indent=4) + "\n", encoding="utf-8")
    print(f"[OK] Generated: {out_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
