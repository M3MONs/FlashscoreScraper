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

The scraper provides several commands:

### Scrape Odds
```
uv run main.py odds <url> [--sport <sport>] [--engine <engine>] [--timeout <seconds>]
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
- `--sport`: Specify sport type (e.g., football, tennis). If not provided, detected from URL.
- `--engine`: Scraping engine (default: playwright). Available: playwright, curl.
- `--timeout`: Request timeout in seconds (default: 10).

## Supported Sports

- Football (in progress)
