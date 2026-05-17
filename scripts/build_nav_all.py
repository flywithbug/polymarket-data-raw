#!/usr/bin/env python3
import subprocess
from pathlib import Path


def run_step(script_path: Path) -> None:
    print(f"[RUN] {script_path}")
    subprocess.run(["python3", str(script_path)], check=True)


def main() -> int:
    root_dir = Path(__file__).resolve().parent.parent
    scripts_dir = root_dir / "scripts"

    # 1) sports_types + sports_config.yaml -> nav/sports.json
    # 2) nav/sports.json + root.json -> nav/root_tags/sports.json
    # 3) nav/root_tags/*.json + root.json -> nav/nav_root.json
    run_step(scripts_dir / "build_root_tag_sports.py")
    run_step(scripts_dir / "build_nav_root_from_root_tags.py")

    print("[OK] All nav build steps finished")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
