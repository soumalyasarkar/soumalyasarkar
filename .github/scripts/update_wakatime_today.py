
import os
import base64
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

import requests

API_KEY = os.environ["WAKATIME_API_KEY"]
TIMEZONE = "Asia/Kolkata"

today = datetime.now(ZoneInfo(TIMEZONE)).date().isoformat()

# Authenticate with WakaTime
token = base64.b64encode(
    f"{API_KEY}:".encode()
).decode()

response = requests.get(
    "https://wakatime.com/api/v1/users/current/summaries",
    params={
        "start": today,
        "end": today,
        "timezone": TIMEZONE
    },
    headers={
        "Authorization": f"Basic {token}"
    },
    timeout=30
)

response.raise_for_status()

data = response.json().get("data", [])

if data:
    total = data[0].get("grand_total", {})
    coding_time = total.get("text", "0 secs")
else:
    coding_time = "0 secs"

# Update README
readme = Path("README.md")
content = readme.read_text(encoding="utf-8")

marker = "<!--WAKATIME_TODAY_TIME-->"

if marker not in content:
    raise SystemExit("Today's WakaTime marker not found!")

replacement = (
    f"{marker}\n"
    f"`{coding_time}`\n\n"
    f"<sub>{today} · Asia/Kolkata</sub>\n"
)

content = content.replace(
    marker,
    replacement,
    1
)

readme.write_text(content, encoding="utf-8")

print(f"Today's coding time: {coding_time}")
