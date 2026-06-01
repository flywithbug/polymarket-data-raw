#!/usr/bin/env python3
import json
import time
import sys
import urllib.parse
import urllib.request
from typing import Any, Dict, List

BASE_URL = "https://gamma-api.polymarket.com/events"
TAG_SLUGS = [
    "soccer",
]
ORDER = "volume24hr"
ASCENDING = "false"
CLOSED = "false"
LIMIT = 100
START_AFTER_CURSOR = ""
MAX_PAGES_PER_RUN = 0
TIMEOUT_SECONDS = 40
MAX_RETRIES = 3
RETRY_INTERVAL_SECONDS = 1
ENABLE_POLLING = True
POLL_INTERVAL_SECONDS = 60
MAX_POLLS = 1


def build_base_url(tag_slug: str) -> str:
    return (
        f"{BASE_URL}/keyset"
        f"?tag_slug={urllib.parse.quote(tag_slug, safe='')}"
    )

        # f"&order={ORDER}"
        # f"&ascending={ASCENDING}"
        # f"&closed={CLOSED}"


def build_output_paths(tag_slug: str) -> tuple[str, str]:
    safe_slug = "".join(c if (c.isalnum() or c in ("-", "_")) else "_" for c in tag_slug)
    return (
        f"teams_map_{safe_slug}.json",
        f"teams_id_name_map_{safe_slug}.json",
    )


def with_keyset_pagination(base_url: str, limit: int, after_cursor: str) -> str:
    parsed = urllib.parse.urlparse(base_url)
    query = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
    query["limit"] = [str(limit)]
    if after_cursor:
        query["after_cursor"] = [after_cursor]
    elif "after_cursor" in query:
        del query["after_cursor"]
    new_query = urllib.parse.urlencode(query, doseq=True)
    return urllib.parse.urlunparse(
        (parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment)
    )


def fetch_page(
    base_url: str, limit: int, after_cursor: str, timeout: int
) -> tuple[str, List[Dict[str, Any]], str]:
    url = with_keyset_pagination(base_url, limit, after_cursor)
    last_error: Exception | None = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "teams-map-fetcher/1.0"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
            break
        except Exception as e:
            last_error = e
            print(f"[retry] attempt={attempt}/{MAX_RETRIES} url={url} err={e}", file=sys.stderr)
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_INTERVAL_SECONDS)
    else:
        raise RuntimeError(f"request failed after retries: {url}") from last_error

    if isinstance(payload, dict):
        events = payload.get("events", [])
        next_cursor = payload.get("next_cursor", "")
        if not isinstance(next_cursor, str):
            next_cursor = ""
        return url, (events if isinstance(events, list) else []), next_cursor
    if isinstance(payload, list):
        return url, payload, ""
    return url, [], ""


def build_teams_map(events: List[Dict[str, Any]], teams_map: Dict[str, Dict[str, Any]]) -> None:
    for event in events:
        teams = event.get("teams", [])
        if not isinstance(teams, list):
            continue
        for team in teams:
            if not isinstance(team, dict):
                continue
            team_id = team.get("id")
            if team_id is None:
                continue
            teams_map[f"ID_{team_id}"] = team


def run_once(tag_slug: str) -> int:
    base_url = build_base_url(tag_slug)
    output_json_path, output_id_name_json_path = build_output_paths(tag_slug)
    teams_map: Dict[str, Dict[str, Any]] = {}
    after_cursor = START_AFTER_CURSOR
    page_index = 1

    while True:
        if MAX_PAGES_PER_RUN > 0 and page_index > MAX_PAGES_PER_RUN:
            print(
                f"[stop] reach max pages per run: {MAX_PAGES_PER_RUN}",
                file=sys.stderr,
            )
            break

        request_url, events, next_cursor = fetch_page(base_url, LIMIT, after_cursor, TIMEOUT_SECONDS)
        print(f"[page {page_index}] GET {request_url}", file=sys.stderr)
        print(f"[page {page_index}] events_count={len(events)}", file=sys.stderr)
        print(f"[page {page_index}] next_cursor={next_cursor or '<empty>'}", file=sys.stderr)
        if not events:
            break

        build_teams_map(events, teams_map)
        page_index += 1

        if not next_cursor:
            break
        after_cursor = next_cursor

    output_json = json.dumps(teams_map, ensure_ascii=False, indent=2, sort_keys=True)
    with open(output_json_path, "w", encoding="utf-8") as f:
        f.write(output_json)
        f.write("\n")

    teams_id_name_map = {
        team_id: str(team.get("name", "")) for team_id, team in teams_map.items()
    }
    output_id_name_json = json.dumps(
        teams_id_name_map, ensure_ascii=False, indent=2, sort_keys=True
    )
    with open(output_id_name_json_path, "w", encoding="utf-8") as f:
        f.write(output_id_name_json)
        f.write("\n")

    print(
        f"[done] tag_slug={tag_slug} teams_count={len(teams_map)} output={output_json_path} "
        f"id_name_output={output_id_name_json_path}",
        file=sys.stderr,
    )
    return 0


def main() -> int:
    if not TAG_SLUGS:
        raise RuntimeError("TAG_SLUGS 不能为空")

    if not ENABLE_POLLING:
        for tag_slug in TAG_SLUGS:
            run_once(tag_slug)
        return 0

    poll_count = 0
    while True:
        poll_count += 1
        print(f"[poll] round={poll_count}", file=sys.stderr)
        for tag_slug in TAG_SLUGS:
            print(f"[poll] tag_slug={tag_slug}", file=sys.stderr)
            run_once(tag_slug)

        if MAX_POLLS > 0 and poll_count >= MAX_POLLS:
            break
        print(f"[poll] sleep_seconds={POLL_INTERVAL_SECONDS}", file=sys.stderr)
        time.sleep(POLL_INTERVAL_SECONDS)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
