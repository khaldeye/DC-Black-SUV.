DC BLACK/SUV WEEKLY — LIVE-UPDATE PWA

What this version does
- Loads event data from events.json every time the app opens.
- Re-checks every 15 minutes while the app is open.
- Keeps an offline cached copy.
- The Home Screen app does not need to be reinstalled when events.json changes.

How to make updates truly automatic
1. Host this folder on HTTPS (GitHub Pages, Netlify, Cloudflare Pages, etc.).
2. Keep index.html, config.js, manifest.webmanifest, sw.js and icons unchanged.
3. Replace/update events.json each week.
4. The installed iPhone app will pick up the new events automatically.

Remote-feed option
- Edit config.js and set dataUrl to any public HTTPS JSON endpoint.
- That endpoint must return:
  {
    "week_label": "...",
    "generated_at": "ISO timestamp",
    "region": "...",
    "events": [ ... ]
  }

Important limitation
- ChatGPT's scheduled task can generate your weekly schedule, but it cannot directly publish into a website from this standalone file by itself.
- To remove the last manual step completely, connect the app to a writable host/data source (for example GitHub, a small Cloudflare Worker/KV endpoint, or another service you control).
