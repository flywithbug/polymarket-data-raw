#!/usr/bin/env python3
import json
from pathlib import Path


def walk_nodes(node):
    yield node
    for child in node.get("children", []) or []:
        yield from walk_nodes(child)


def main() -> int:
    root_dir = Path(__file__).resolve().parent.parent
    types_dir = root_dir / "nav" / "sports_types"
    index_file = types_dir / "index.json"
    root_cfg_file = types_dir / "sports_config.yaml"
    target_file = root_dir / "nav" / "sports.json"

    if not index_file.exists():
        raise FileNotFoundError(f"Missing index file: {index_file}")
    if not root_cfg_file.exists():
        raise FileNotFoundError(f"Missing root config file: {root_cfg_file}")

    index = json.loads(index_file.read_text(encoding="utf-8"))
    try:
        import yaml
    except ImportError as e:
        raise RuntimeError("PyYAML is required: pip install pyyaml") from e

    cfg = yaml.safe_load(root_cfg_file.read_text(encoding="utf-8")) or {}

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

    root_order = cfg.get("rootOrder") or []
    promoted_slugs = cfg.get("rootPromotedSlugs") or []

    all_nodes = []
    for node in base:
        all_nodes.extend(list(walk_nodes(node)))

    promoted = []
    seen = set()
    for slug in promoted_slugs:
        if slug in seen:
            continue

        chosen = None
        for n in all_nodes:
            if n.get("slug") == slug and n.get("p_slug") != "sports":
                chosen = n
                break

        if chosen is None:
            for n in all_nodes:
                if n.get("slug") == slug:
                    chosen = n
                    break

        if chosen is not None:
            promoted.append(chosen)
            seen.add(slug)

    order_map = {slug: i for i, slug in enumerate(root_order)}
    base_by_slug = {str(n.get("slug") or "").strip(): n for n in base}

    # rootOrder now works as both ordering and filtering.
    # Only slugs listed in rootOrder are kept.
    sorted_base = []
    for slug in root_order:
        node = base_by_slug.get(str(slug).strip())
        if node is not None:
            sorted_base.append(node)

    children = promoted + sorted_base

    output = {"children": children}

    target_file.write_text(json.dumps(output, ensure_ascii=False, indent=4) + "\n", encoding="utf-8")

    print(f"[OK] Merged {len(type_names)} type files into {target_file}")
    print(f"[OK] Root config applied: {root_cfg_file}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
