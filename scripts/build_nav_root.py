#!/usr/bin/env python3
import json
from pathlib import Path


def main() -> int:
    root_dir = Path(__file__).resolve().parent.parent
    nav_dir = root_dir / "nav"

    root_file = nav_dir / "root.json"
    crypto_file = nav_dir / "crypto.json"
    sports_file = nav_dir / "sports.json"
    out_file = nav_dir / "nav_root.json"

    root_data = json.loads(root_file.read_text(encoding="utf-8"))
    crypto_data = json.loads(crypto_file.read_text(encoding="utf-8"))
    sports_data = json.loads(sports_file.read_text(encoding="utf-8"))

    root_tags = root_data.get("rootTag", [])
    if not isinstance(root_tags, list):
        raise ValueError("root.json: rootTag must be an array")

    for tag in root_tags:
        slug = tag.get("slug")
        if slug == "crypto":
            tag["children"] = crypto_data.get("children", [])
        elif slug == "sports":
            tag["children"] = sports_data.get("children", [])

    merged = {
        "rootTag": root_tags,
        "eventPath": root_data.get("eventPath"),
    }

    out_file.write_text(json.dumps(merged, ensure_ascii=False, indent=4) + "\n", encoding="utf-8")
    print(f"[OK] Generated: {out_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
