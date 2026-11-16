# JSC

Scrapes number statistics from [Jogos Santa Casa](https://www.jogossantacasa.pt), picks numbers for the next draw, and (optionally) places the bet automatically. A small static web UI shows the generated picks.

Supported games:

| Game        | Numbers | Specials | Scheduled run (09:00) |
|-------------|---------|----------|-----------------------|
| Euromilhões | 5       | 2 stars  | Wed, Sat              |
| Totoloto    | 5       | 1        | Thu, Sun              |
| EuroDreams  | 6       | 1        | Tue, Fri              |

## How it works

- **`py/py.py`** – APScheduler entrypoint; runs `j.py` for each game on its schedule.
- **`py/j.py`** – Scrapy spider that reads the game's statistics page, picks numbers based on absences and frequency across number ranges, and writes the result to `/data/<game>.json`. It then calls `auto.py` once per configured account.
- **`py/auto.py`** – Playwright (Firefox + stealth) script that logs in and places the bet.
- **`ui/`** – Static page served by nginx that displays the picks from `ui/data/`.

## Running

Requires Docker and Docker Compose.

1. Copy `.env.example` to `.env` and fill in your credentials:

   ```bash
   cp .env.example .env
   ```

2. Start the services:

   ```bash
   docker compose up --build
   ```

- UI: http://localhost:3000
- Scraper service: port 5001

Both containers share the `shared-data` volume, so JSON written by the scraper to `/data` is served by nginx at `/data/`.

### Running a single game manually

```bash
docker compose exec py python j.py euromilhoes
```

Valid arguments: `euromilhoes`, `totolotoN`, `EuroDreams`.

## Disclaimer

Personal project. Lottery outcomes are random; the number selection here does not improve your odds. Use automated betting at your own risk and in line with the site's terms.
