# Flashscore Scraper

A command-line tool for scraping sports data from Flashscore.

## Description

This project provides a scraper to extract sports event information, odds, and other data from Flashscore website.

## Installation

1. Ensure you have Python 3.13 or higher installed.
2. Clone the repository.
3. Install dependencies:
   ```
   uv sync
   ```

## Usage

The scraper provides three commands:

### Scrape Odds
```
uv run main.py odds <url> [--odds <type1> <type2> ...] [--bookmakers <id1> <id2> ...] [--sport <sport>] [--engine <engine>] [--timeout <seconds>]
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
| `--odds` | *(odds command only)* Specific odds types to scrape (e.g. `1x2-odds`, `over-under`). All types scraped if omitted. | `[]` |
| `--bookmakers` | *(odds command only)* Bookmaker IDs to include (e.g. `2 16 17`). All bookmakers included if omitted. | `[]` |

## Supported Sports

- Football (in progress)
