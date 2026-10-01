from __future__ import annotations
import json, shutil, sys
from datetime import datetime, timezone
from pathlib import Path

def parse_publish_at(value: str) -> datetime:
    value = str(value or "").strip()
    if not value:
        raise ValueError("publishAt is required")
    if value.endswith("Z"):
        return datetime.fromisoformat(value[:-1] + "+00:00")
    if len(value) >= 6 and value[-6] in "+-" and value[-3] == ":":
        return datetime.fromisoformat(value)
    return datetime.fromisoformat(value + "+09:00")

def event_key(event: dict):
    return (
        str(event.get("date", "")).strip(),
        str(event.get("title", "")).strip(),
        str(event.get("venue", "")).strip(),
    )

def main() -> int:
    if len(sys.argv) != 3:
        print("usage: publish_scheduled.py <scheduler_repo> <public_repo>")
        return 2

    scheduler_repo = Path(sys.argv[1]).resolve()
    public_repo = Path(sys.argv[2]).resolve()
    queue_dir = scheduler_repo / "scheduler" / "queue"
    assets_dir = scheduler_repo / "scheduler" / "assets" / "flyers"
    events_path = public_repo / "events.json"
    flyers_dir = public_repo / "assets" / "flyers"

    queue_dir.mkdir(parents=True, exist_ok=True)
    flyers_dir.mkdir(parents=True, exist_ok=True)

    events = json.loads(events_path.read_text(encoding="utf-8")) if events_path.exists() else []
    known = {event_key(e) for e in events}
    now = datetime.now(timezone.utc)
    count = 0

    for q in sorted(queue_dir.glob("*.json")):
        try:
            item = json.loads(q.read_text(encoding="utf-8"))
            if parse_publish_at(item.get("publishAt", "")).astimezone(timezone.utc) > now:
                continue

            event = dict(item["event"])
            key = event_key(event)

            if key not in known:
                event["publishMode"] = "now"
                event.pop("publishAt", None)
                events.append(event)
                known.add(key)

            for filename in item.get("assetFiles", []) or []:
                filename = Path(str(filename)).name
                src = assets_dir / filename
                if src.exists():
                    shutil.copy2(src, flyers_dir / filename)

            q.unlink()
            count += 1
            print("published:", key)

        except Exception as exc:
            print("ERROR", q.name, exc)

    if count:
        events.sort(
            key=lambda e: (
                str(e.get("date", "")),
                str(e.get("title", "")),
                str(e.get("venue", "")),
            )
        )
        events_path.write_text(
            json.dumps(events, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    print("published_count=", count)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
