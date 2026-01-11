import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

URL = "https://www.isu.org/events/?discipline=FIGURE+SKATING&season=2025%2F2026"

MONTH_MAP = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,
    "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
    "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
}

@app.get("/schedule.json")
def get_schedule():
    html = requests.get(URL, timeout=15).text
    soup = BeautifulSoup(html, "html.parser")

    events = []

    for item in soup.select(".event-item"):
        title = item.select_one("h3")
        date = item.select_one(".event-date")
        location = item.select_one(".event-location")

        if not title or not date:
            continue

        raw_date = date.text.strip()

        month = None
        for m in MONTH_MAP:
            if m in raw_date:
                month = MONTH_MAP[m]
                break

        city = ""
        country = ""
        if location:
            parts = location.text.split(",")
            city = parts[0].strip()
            if len(parts) > 1:
                country = parts[-1].strip()

        events.append({
            "title": title.text.strip(),
            "date": raw_date,
            "month": month,
            "city": city,
            "country": country
        })

    return {
        "updated": datetime.utcnow().isoformat(),
        "events": events
    }
