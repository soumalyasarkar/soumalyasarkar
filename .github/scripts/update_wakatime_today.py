
#!/usr/bin/env python3

import base64
import os
from pathlib import Path
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import requests


# Configuration
API_KEY = os.environ["WAKATIME_API_KEY"]
TIMEZONE = "Asia/Kolkata"

local_today = datetime.now(ZoneInfo(TIMEZONE)).date()
today = local_today.isoformat()
end_date = local_today - timedelta(days=1)
start_date = end_date - timedelta(days=6)


# WakaTime API authentication
token = base64.b64encode(
    f"{API_KEY}:".encode()
).decode()


# Fetch today's and the previous seven completed days in one API request.
url = "https://wakatime.com/api/v1/users/current/summaries"

response = requests.get(
    url,
    params={
        "start": start_date.isoformat(),
        "end": today,
        "timezone": TIMEZONE,
    },
    headers={
        "Authorization": f"Basic {token}",
    },
    timeout=30,
)

response.raise_for_status()

data = response.json().get("data", [])
summaries = {entry.get("range", {}).get("date"): entry for entry in data}


def total_for(day: date) -> str:
    entry = summaries.get(day.isoformat(), {})
    return entry.get("grand_total", {}).get("text", "0 secs")


coding_time = total_for(local_today)
completed_week = [end_date - timedelta(days=offset) for offset in range(6, -1, -1)]
week_lines = [f"{day.strftime('%a, %d %b')}: {total_for(day)}" for day in completed_week]


# Update README
readme = Path("README.md")

content = readme.read_text(
    encoding="utf-8"
)

marker = "<!--WAKATIME_TODAY_TIME-->"

if marker not in content:
    raise SystemExit(
        "ERROR: Today's WakaTime marker not found in README!"
    )

# Replace the entire panel so reruns never accumulate stale rows.
start_marker = "<!--START_SECTION:waka-today-->"
end_marker = "<!--END_SECTION:waka-today-->"
if start_marker not in content or end_marker not in content:
    raise SystemExit("ERROR: Today's WakaTime section markers are missing!")

start = content.index(start_marker) + len(start_marker)
end = content.index(end_marker, start)
panel = (
    "\n<table>\n<tr>\n"
    "<td width=\"50%\" valign=\"top\">\n\n"
    "**☀️ TODAY'S CODING**\n\n"
    f"{marker}\n`{coding_time}`\n\n<sub>{today} · Asia/Kolkata</sub>\n\n"
    "</td>\n<td width=\"50%\" valign=\"top\">\n\n"
    "**📅 LAST 7 COMPLETED DAYS**\n\n"
    "```text\n" + "\n".join(week_lines) + "\n```\n"
    "</td>\n</tr>\n</table>\n"
)
content = content[:start] + panel + content[end:]

readme.write_text(
    content,
    encoding="utf-8",
)

print("--------------------------------")
print("WakaTime Daily Stats Updated")
print("--------------------------------")
print(f"Date: {today}")
print(f"Coding time: {coding_time}")
print("--------------------------------")
