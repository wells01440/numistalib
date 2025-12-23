# Numista-lib

Python wrapper for the Numista API with caching, rate limiting, and retry logic.

## Features

- **Complete API Coverage**: Search types, get details, catalogues, issuers, and more
- **HTTP Caching**: RFC 9111-compliant persistent caching with hishel
- **Rate Limiting**: Configurable rate limits to respect API quotas
- **Retry Logic**: Exponential backoff with jitter for resilient requests
- **Rich CLI**: Beautiful command-line interface with tables and colors
- **Type Safety**: Full Pydantic models with strict validation

## Installation

```bash
uv pip install -e .
```

## Configuration

1. Get your API key from [Numista API](https://en.numista.com/api/)
2. Copy `.env.example` to `.env`:

   ```bash
   cp .env.example .env
   ```

3. Add your API key to `.env`:

   ```bash
   NUMISTA_API_KEY=your_api_key_here
   ```

## CLI Usage

### Search for types

```bash
numista-lib types search -q "dollar"
numista-lib types search --issuer united-states --year 2020
```

### Get type details

```bash
numista-lib types get 95420
```

### List catalogues

```bash
numista-lib catalogues
```

### List issuers

```bash
numista-lib issuers
numista-lib issuers --lang es
```

### Configuration management

```bash
numista-lib config list
numista-lib config get cache_dir
```

## Python Usage

```python
from numista_lib.client import NumistaApiClient
from numista_lib.config import Settings, logger
from numista_lib.services import TypeService

settings = Settings()

with NumistaApiClient(settings, logger) as client:
    service = TypeService(client, logger)
    
    # Search for types
    results = service.search_types(query="dollar", page=1, count=10)
    for coin_type in results:
        print(f"{coin_type.numista_id}: {coin_type.title}")
    
    # Get full details
    full_type = service.get_type(95420)
    print(f"Weight: {full_type.weight}g")
    print(f"Composition: {full_type.composition}")
```

## Development

### Install dependencies

```bash
uv sync
```

### Run tests

```bash
uv run pytest tests/ -v
```

### Check code quality

```bash
uv run ruff check src/
uv run ruff format src/
uv run pyright src/
```

### Check complexity

```bash
uv run radon cc src/numista_lib/ -a -nb
uv run xenon --max-absolute B src/numista_lib/
```

## Architecture

- **models/**: Pydantic models for API entities
- **client.py**: HTTP client with caching, rate limiting, retry
- **services/**: Business logic for each API endpoint
- **config.py**: Settings management with Pydantic BaseSettings
- **cli.py**: Click-based command-line interface

## License

MIT License - see [license.txt](license.txt)

## Contributing

See [AGENTS.md](AGENTS.md) for coding standards and guidelines.
