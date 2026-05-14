#!/usr/bin/env sh
set -eu

# Merge nav/sports_types/*.json back into nav/sports.json
# - Uses nav/sports_types/index.json for type files
# - Uses nav/sports_types/root_config.json for root sorting + promoted league config
# - Creates nav/sports.json.bak before overwrite

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TYPES_DIR="$ROOT_DIR/nav/sports_types"
INDEX_FILE="$TYPES_DIR/index.json"
ROOT_CONFIG_FILE="$TYPES_DIR/root_config.json"
TARGET_FILE="$ROOT_DIR/nav/sports.json"

if ! command -v jq >/dev/null 2>&1; then
  echo "[ERROR] jq is required but not found in PATH" >&2
  exit 1
fi

if [ ! -f "$INDEX_FILE" ]; then
  echo "[ERROR] Missing index file: $INDEX_FILE" >&2
  exit 1
fi

if [ ! -f "$ROOT_CONFIG_FILE" ]; then
  echo "[ERROR] Missing root config file: $ROOT_CONFIG_FILE" >&2
  exit 1
fi

jq . "$ROOT_CONFIG_FILE" >/dev/null

TMP_TYPES="$(mktemp)"
TMP_MERGED="$(mktemp)"
TMP_TARGET="$(mktemp)"

cleanup() {
  rm -f "$TMP_TYPES" "$TMP_MERGED" "$TMP_TARGET"
}
trap cleanup EXIT

jq -r '.types[]' "$INDEX_FILE" > "$TMP_TYPES"

# Start with empty merged array
printf '[]\n' > "$TMP_MERGED"

COUNT=0
while IFS= read -r t; do
  [ -n "$t" ] || continue
  f="$TYPES_DIR/$t.json"

  if [ ! -f "$f" ]; then
    echo "[ERROR] Missing type file: $f" >&2
    exit 1
  fi

  jq . "$f" >/dev/null

  TMP_NEXT="$(mktemp)"
  jq -n --argfile a "$TMP_MERGED" --argfile b "$f" '$a + ($b.items // [])' > "$TMP_NEXT"
  mv "$TMP_NEXT" "$TMP_MERGED"

  COUNT=$((COUNT + 1))
done < "$TMP_TYPES"

if [ "$COUNT" -eq 0 ]; then
  echo "[ERROR] No type files found from $INDEX_FILE" >&2
  exit 1
fi

jq -n \
  --argfile cfg "$ROOT_CONFIG_FILE" \
  --argfile merged "$TMP_MERGED" '
    def walk_nodes:
      ., (.children[]? | walk_nodes);

    def order_map($arr):
      reduce range(0; ($arr | length)) as $i ({}; . + { ($arr[$i]): $i });

    ($cfg.rootOrder // []) as $rootOrder |
    ($cfg.rootPromotedSlugs // []) as $promotedSlugs |
    ($merged) as $base |
    ([ $base[] | walk_nodes ]) as $allNodes |

    # Promote league nodes to root by slug
    ([ $promotedSlugs[] as $slug
      | ($allNodes[] | select(.slug == $slug) | .) ]
      | group_by(.slug)
      | map(.[0])) as $promoted |

    # Remove root duplicates for promoted slugs
    ([ $base[] | select((.slug as $s | ($promotedSlugs | index($s))) == null) ]) as $baseWithoutPromoted |

    ($promoted + $baseWithoutPromoted) as $combined |
    (order_map($rootOrder)) as $omap |

    {
      children: (
        [ range(0; ($combined | length)) as $i | ($combined[$i] + {"__idx": $i}) ]
        | sort_by(( $omap[.slug] // 1000000 ), .__idx)
        | map(del(.__idx))
      )
    }
  ' > "$TMP_TARGET"

jq . "$TMP_TARGET" >/dev/null

if [ -f "$TARGET_FILE" ]; then
  cp "$TARGET_FILE" "$TARGET_FILE.bak"
fi

mv "$TMP_TARGET" "$TARGET_FILE"

echo "[OK] Merged $COUNT type files into $TARGET_FILE"
echo "[OK] Root config applied: $ROOT_CONFIG_FILE"
if [ -f "$TARGET_FILE.bak" ]; then
  echo "[OK] Backup created: $TARGET_FILE.bak"
fi
