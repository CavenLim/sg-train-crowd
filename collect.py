import csv, json, os, urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

KEY = os.environ["LTA_API_KEY"]
LINES = ["CCL","CEL","CGL","DTL","EWL","NEL","NSL","BPL","SLRT","PLRT","TEL"]
URL = "https://datamall2.mytransport.sg/ltaodataservice/PCDRealTime?TrainLine="
SGT = timezone(timedelta(hours=8))

def fetch(line):
    req = urllib.request.Request(
        URL + line,
        headers={"AccountKey": KEY, "accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r).get("value", [])

now = datetime.now(timezone.utc)
rows = []
for line in LINES:
    try:
        for s in fetch(line):
            rows.append([
                now.isoformat(timespec="seconds"), line,
                s.get("Station"), s.get("StartTime"),
                s.get("EndTime"), s.get("CrowdLevel"),
            ])
    except Exception as e:
        print(f"{line} failed: {e}")

if rows:
    path = Path("data") / f"{now.astimezone(SGT):%Y-%m-%d}.csv"
    path.parent.mkdir(exist_ok=True)
    is_new = not path.exists()
    with path.open("a", newline="") as f:
        w = csv.writer(f)
        if is_new:
            w.writerow(["polled_at_utc","line","station",
                        "start_time","end_time","crowd_level"])
        w.writerows(rows)
print(f"saved {len(rows)} rows")
