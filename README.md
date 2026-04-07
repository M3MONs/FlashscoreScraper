# Flashscore Scraper

A command-line tool for scraping sports data from [Flashscore](https://www.flashscore.com).

## Description

This project provides a scraper to extract sports event information, odds, and other data from Flashscore website.

## Installation

1. Ensure you have Python 3.13 or higher installed.
2. Clone the repository.
3. Install dependencies:
   ```
   uv sync
   uv run playwright install chromium
   ```
   
## Usage

All commands print JSON to stdout and accept the common options described below

### Scrape Odds
```
uv run main.py odds <url> [--odds <type> ...] [--bookmakers <id> ...] [--sport <sport>] [--engine <engine>] [--timeout <seconds>]
```

### Scrape Event Information
```
uv run main.py event <url> [--sport <sport>] [--engine <engine>] [--timeout <seconds>]
```

### Scrape Event Context Information
```
uv run main.py event-info <url> [--sport <sport>] [--engine <engine>] [--timeout <seconds>]
```

### Options

| Option | Description | Default |
|---|---|---|
| `url` | Flashscore event URL | *(required)* |
| `--sport` | Sport type (e.g. `football`). Auto-detected from URL if not provided. | `None` |
| `--engine` | Scraping engine: `playwright` or `curl` | `playwright` |
| `--timeout` | Request timeout in seconds | `10` |
| `-v`, `--verbose` | Enable debug logging | off |

### `odds`-only Options

| Option | Description | Default |
|---|---|---|
| `--odds` | One or more odds types to scrape. Scrapes all types when omitted. | all |
| `--bookmakers` | Bookmaker IDs to include (e.g. `2 16 17`). Includes all bookmakers when omitted. | all |

### Examples

```bash
# Scrape all odds for a football match
uv run main.py odds https://www.flashscore.com/match/football/...

# Scrape only 1X2 and over/under odds, filtered to two bookmakers
uv run main.py odds https://www.flashscore.com/match/football/... --odds 1x2-odds over-under --bookmakers 2 16

# Scrape event summary
uv run main.py event https://www.flashscore.com/match/football/...

# Scrape extended event info with verbose logging
uv run main.py event-info https://www.flashscore.com/match/football/... -v
```

## Supported Sports

### Football

| Odds Type | `--odds` value |
|---|---|
| 1X2 | `1x2-odds` |
| Over/Under | `over-under` |
| Asian Handicap | `asian-handicap` |
| Both Teams to Score | `both-teams-to-score` |
| Double Chance | `double-chance` |
| European Handicap | `european-handicap` |
| Draw No Bet | `draw-no-bet` |
| Correct Score | `correct-score` |
| Half Time / Full Time | `ht-ft` |
| Odd/Even | `odd-even` |

## Running Tests

```bash
uv run pytest
```
