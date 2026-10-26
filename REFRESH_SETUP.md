# DC Black SUV event refresh

The app retains its existing layout. Its Refresh button searches the Ticketmaster Discovery API directly on demand. The scheduled GitHub Actions job refreshes events.json on Mondays at 12:15 UTC (7:15 AM EST / 8:15 AM EDT). The date range is calculated dynamically for each current Monday–Sunday week.

## Required one-time setup

1. Register for a Ticketmaster Discovery API key at https://developer.ticketmaster.com/ .
2. In repository Settings > Secrets and variables > Actions, create a repository secret named `TICKETMASTER_API_KEY` containing that key. The weekly job reads the secret; it is not committed to GitHub.
3. To enable the in-browser Refresh button, set `ticketmasterPublicKey` in `config.js` to a **separate browser-appropriate API key**. This key is visible to anyone using the website. If you do not want to expose an API key, leave it blank; Refresh will load the most recently published feed and explain that live search is not configured.
4. Merge this branch into `main` to enable scheduled GitHub Actions and deploy the app.
5. Run the `Update DMV events` workflow once from Actions > Run workflow, and check its logs and events.json.

## Limits

- Ticketmaster covers ticketed concerts, sports and some other events. It does not provide comprehensive galas, conferences, embassy receptions, airport flight data or rideshare surge predictions.
- Demand ratings are heuristics, not real Uber demand.
- Manual Refresh searches in the browser and changes what that device displays. It does **not** write to GitHub. The weekly workflow writes the shared events.json file.
- GitHub Pages cannot safely initiate an authenticated GitHub Actions dispatch without an additional backend. A future authenticated endpoint could make the button persist results to GitHub.
- Provider status fields are included. Events marked cancelled are hidden from the main list.
- GitHub scheduled workflows may run late or be skipped during service delays.
