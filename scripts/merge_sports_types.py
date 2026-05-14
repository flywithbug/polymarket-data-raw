#!/usr/bin/env python3
import json
import shutil
from pathlib import Path


def walk_nodes(node):
    yield node
    for child in node.get("children", []) or []:
        yield from walk_nodes(child)


def main() -> int:
    root_dir = Path(__file__).resolve().parent.parent
    types_dir = root_dir / "nav" / "sports_types"
    index_file = types_dir / "index.json"
    root_cfg_file = types_dir / "root_config.json"
    target_file = root_dir / "nav" / "sports.json"

    if not index_file.exists():
        raise FileNotFoundError(f"Missing index file: {index_file}")
    if not root_cfg_file.exists():
        raise FileNotFoundError(f"Missing root config file: {root_cfg_file}")

    index = json.loads(index_file.read_text(encoding="utf-8"))
    cfg = json.loads(root_cfg_file.read_text(encoding="utf-8"))

    type_names = index.get("types", [])
    if not type_names:
        raise ValueError(f"No types found in {index_file}")

    base = []
    for t in type_names:
        f = types_dir / f"{t}.json"
        if not f.exists():
            raise FileNotFoundError(f"Missing type file: {f}")
        data = json.loads(f.read_text(encoding="utf-8"))
        item = data.get("item")
        if not isinstance(item, dict):
            raise ValueError(f"Invalid item in {f}: expect object")
        base.append(item)

    root_order = cfg.get("rootOrder", [])
    promoted_slugs = cfg.get("rootPromotedSlugs", [])

    all_nodes = []
    for node in base:
        all_nodes.extend(list(walk_nodes(node)))

    promoted = []
    seen = set()
    for slug in promoted_slugs:
        if slug in seen:
            continue
        for n in all_nodes:
            if n.get("slug") == slug:
                promoted.append(n)
                seen.add(slug)
                break

    promoted_slug_set = set(promoted_slugs)
    base_without_promoted = [n for n in base if n.get("slug") not in promoted_slug_set]

    # promoted nodes always stay at the front, preserving rootPromotedSlugs order
    order_map = {slug: i for i, slug in enumerate(root_order)}
    base_with_idx = list(enumerate(base_without_promoted))
    base_with_idx.sort(key=lambda it: (order_map.get(it[1].get("slug"), 1_000_000), it[0]))
    sorted_base = [n for _, n in base_with_idx]

    children = promoted + sorted_base

    output = {"children": children}

    if target_file.exists():
        backup = target_file.with_suffix(target_file.suffix + ".bak")
        shutil.copyfile(target_file, backup)

    target_file.write_text(json.dumps(output, ensure_ascii=False, indent=4) + "\n", encoding="utf-8")

    print(f"[OK] Merged {len(type_names)} type files into {target_file}")
    print(f"[OK] Root config applied: {root_cfg_file}")
    backup_file = target_file.with_suffix(target_file.suffix + ".bak")
    if backup_file.exists():
        print(f"[OK] Backup created: {backup_file}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
