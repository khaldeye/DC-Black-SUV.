#!/usr/bin/env python3
"""Refresh the current Monday-Sunday DMV event feed from Ticketmaster."""
import datetime as dt
import json
import os
from pathlib import Path
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo

key = os.getenv("TICKETMASTER_API_KEY", "").strip()
if not key:
    raise SystemExit("Set the TICKETMASTER_API_KEY repository secret before running.")
tz = ZoneInfo("America/New_York")
now = dt.datetime.now(tz)
monday = now.date() - dt.timedelta(days=now.weekday())
sunday = monday + dt.timedelta(days=6)
begin = dt.datetime.combine(monday, dt.time.min, tz).astimezone(dt.timezone.utc)
finish = dt.datetime.combine(sunday + dt.timedelta(days=1), dt.time.min, tz).astimezone(dt.timezone.utc)
fmt = lambda x: x.strftime("%Y-%m-%dT%H:%M:%SZ")
allowed_va = {"arlington","alexandria","tysons","vienna","fairfax","falls church","reston","mclean","herndon","ashburn","dulles"}
allowed_md = {"national harbor","oxon hill","bethesda","silver spring","rockville","college park","hyattsville","bowie","gaithersburg"}
items = {}
for state in ("DC", "VA", "MD"):
    for page in range(3):
        params = urllib.parse.urlencode(dict(apikey=key, stateCode=state, startDateTime=fmt(begin),
                                              endDateTime=fmt(finish), size=200, page=page, sort="date,asc"))
        req = urllib.request.Request("https://app.ticketmaster.com/discovery/v2/events.json?" + params,
                                     headers={"User-Agent": "DCBlackSUV/1.0"})
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.load(response)
        for e in data.get("_embedded", {}).get("events", []):
            items[e["id"]] = e
        if page + 1 >= data.get("page", {}).get("totalPages", 0):
            break

rows = []
for e in items.values():
    venue = (e.get("_embedded", {}).get("venues") or [{}])[0]
    city = venue.get("city", {}).get("name", "").strip()
    state = venue.get("state", {}).get("stateCode", "DC")
    if state == "VA" and city.lower() not in allowed_va: continue
    if state == "MD" and city.lower() not in allowed_md: continue
    date = e.get("dates", {}).get("start", {}).get("localDate")
    if not date or not monday.isoformat() <= date <= sunday.isoformat(): continue
    segment = (e.get("classifications") or [{}])[0].get("segment", {}).get("name", "").lower()
    kind = "sport" if "sport" in segment else "concert" if "music" in segment else "expo"
    rawtime = e.get("dates", {}).get("start", {}).get("localTime")
    try: timelabel = dt.datetime.strptime(rawtime[:5], "%H:%M").strftime("%I:%M %p").lstrip("0")
    except (ValueError, TypeError): timelabel = "Time TBA"
    address = ", ".join(x for x in [venue.get("address", {}).get("line1", ""), city, state] if x)
    rows.append(dict(id="tm-"+e["id"], day=dt.date.fromisoformat(date).strftime("%a"),
        date=date, time=timelabel, name=e.get("name", "Event"), address=address or venue.get("name", "Venue TBA"),
        venue=venue.get("name", ""), pickup="End time unconfirmed; check event listing",
        rating=4 if kind in ("concert","sport") else 3, type=kind, profile="Demand estimate only",
        tag=kind.title(), status=e.get("dates", {}).get("status", {}).get("code", "onsale"),
        source=e.get("url", "")))
rows.sort(key=lambda e: (e["date"], e["time"], e["name"]))
if not rows:
    raise SystemExit("No events found; keeping existing events.json")
label = f"{monday:%b} {monday.day} – {sunday:%b} {sunday.day}, {sunday.year}"
payload = dict(week_label=label, generated_at=now.isoformat(), region="DC • Northern Virginia • Maryland",
               source="Ticketmaster Discovery API", events=rows)
Path("events.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
print(f"Updated {len(rows)} events for {label}")
