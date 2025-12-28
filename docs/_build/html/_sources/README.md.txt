# numistalib Documentation

This directory contains comprehensive documentation for numistalib.

## Documentation Structure

### User Guides

- [installation.md](installation.md) - Installation and setup
- [quickstart.md](quickstart.md) - 5-minute getting started guide
- [cli_guide.md](cli_guide.md) - Complete CLI command reference
- [python_api_guide.md](python_api_guide.md) - Python API usage guide
- [configuration.md](configuration.md) - Configuration reference
- [advanced_usage.md](advanced_usage.md) - Advanced patterns and techniques

### Reference Documentation

- [architecture.md](architecture.md) - System architecture and design
- [contributing.md](contributing.md) - Contribution guidelines
- [changelog.md](changelog.md) - Version history
- [license.md](license.md) - MIT License

### API Reference

- [API Reference](api/index.rst) - Sphinx autodoc API reference
  - [client.rst](api/client.rst) - HTTP client
  - [services.rst](api/services.rst) - Service layer
  - [models.rst](api/models.rst) - Data models
  - [cli.rst](api/cli.rst) - CLI commands

### Technical Reference

- [numista-swagger.yml](numista-swagger.yml) - Numista API specification

## Building Documentation

### Prerequisites

Install documentation dependencies:

```bash
uv sync --group docs
```

### Build HTML

```bash
cd docs
uv run sphinx-build -b html . _build/html
```

Or using Make:

```bash
cd docs
make html
```

### View Documentation

Open `docs/_build/html/index.html` in your browser.

### Build Other Formats

PDF:

```bash
cd docs
make latexpdf
```

EPUB:

```bash
cd docs
make epub
```

## ReadTheDocs

This documentation is configured for ReadTheDocs deployment.

### Configuration Files

- [.readthedocs.yml](../.readthedocs.yml) - RTD build configuration
- [conf.py](conf.py) - Sphinx configuration
- [requirements.txt](requirements.txt) - Documentation dependencies

### Deployment

The documentation will build automatically when pushed to GitHub (once RTD webhook is configured).

## Documentation Standards

### Formatting

- Use § numbering for sections
- Markdown for user guides
- reStructuredText for API reference
- Code examples should be runnable
- Include "Next Steps" links at guide ends

### Content

- Progressive complexity (basic → advanced)
- Concrete, copy-pasteable examples
- Clear explanations
- Complete coverage of features
- Cross-references between docs

### Maintenance

- Update changelog for releases
- Keep API reference in sync with code
- Test all code examples
- Update screenshots/diagrams as needed

## § 1 Numista API Endpoint Trees

Each section below mirrors the OpenAPI file (`docs/numista-swagger.yml`) and lists every path, method, and request
parameter set per API version.
All calls require the `Numista-API-Key` header; endpoints under “User” additionally need the
OAuth scopes noted in the swagger comments.

## § 1.1 Version 3 (`https://api.numista.com/v3`)

- `/types`
  - `GET` Search the catalogue (at least one of `q`, `issuer`, `catalogue`, `date`, or `year` is required).
    - Query: `lang` (enum en/es/fr, default `en`), `category` (coin|banknote|exonumia), `q` (string),
      `issuer` (string code), `catalogue` (int), `number` (string, requires `catalogue`), `ruler` (int),
      `material` (int), `year` (string/range), `date` (string/range), `size` (string/range in mm),
      `weight` (string/range in g), `page` (int, default `1`), `count` (int, default `50`, max `50`).
  - `POST` Add a type to the catalogue (requires catalogue-edit permission).
    - Query: `lang` (enum en/es/fr, default `en`).
    - Body: `type_update` JSON including localized `title`, `category`, `issuer`, `value`, `ruling_authority`, `shape`,
      `composition`, physical data (`weight`, `size`, `thickness`, `orientation`), demonetization/calendar metadata,
      `obverse`/`reverse`/`edge` descriptions, `mints`, rich `comments`, `related_coins`, `tags`, and `references`.
- `/types/{type_id}`
  - `GET` Get details about a type.
    - Path: `type_id` (int).
    - Query: `lang` (enum en/es/fr, default `en`).
- `/types/{type_id}/issues`
  - `GET` List every issue of a type.
    - Path: `type_id` (int).
    - Query: `lang` (enum en/es/fr, default `en`).
  - `POST` Add an issue (requires catalogue-edit permission).
    - Path: `type_id` (int).
    - Query: `lang` (enum en/es/fr, default `en`).
    - Body: `issue_update` JSON covering `is_dated`, year span, `mint_letter`, `mintage`,
      localized `comment`, and related catalogue references.
- `/types/{type_id}/issues/{issue_id}/prices`
  - `GET` Return price estimates stratified by grade.
    - Path: `type_id` (int), `issue_id` (int).
    - Query: `currency` (ISO 4217 code, default `EUR`), `lang` (enum en/es/fr, default `en`).
- `/issuers`
  - `GET` Enumerate issuers.
    - Query: `lang` (enum en/es/fr, default `en`).
- `/mints`
  - `GET` Enumerate mints.
    - Query: `lang` (enum en/es/fr, default `en`).
- `/mints/{mint_id}`
  - `GET` Fetch mint details.
    - Path: `mint_id` (int).
    - Query: `lang` (enum en/es/fr, default `en`).
- `/catalogues`
  - `GET` List available reference catalogues (no parameters).
- `/search_by_image`
  - `POST` Find candidate types via up to two reference photos.
    - Query: `lang` (enum en/es/fr, default `en`),
      `activate_experimental_features` (bool, default `false`, unlocks year/grade beta output).
    - Body: JSON with optional `category` (coin|banknote|exonumia), required `images` array (1–2 items each containing
      `mime_type` of `image/jpeg` or `image/png` plus base64 `image_data`), and optional `max_results` (int 1–100,
      default `100`).
- `/publications/{id}`
  - `GET` Return information about a specific publication.
    - Path: `id` (string such as `L123456`).
- `/oauth_token`
  - `GET` Exchange for an OAuth token (authorization-code or client-credentials flows).
    - Query: `grant_type` (`authorization_code` default or `client_credentials`), `code`, `client_id`, `client_secret`,
      `redirect_uri`, `scope` (comma-delimited list when using client credentials). Mandatory fields depend on
      `grant_type` exactly as described in the API docs.
- `/users/{user_id}`
  - `GET` Fetch public profile data.
    - Path: `user_id` (int).
    - Query: `lang` (enum en/es/fr, default `en`).
- `/users/{user_id}/collections`
  - `GET` List the user’s collections (path `user_id` only).
- `/users/{user_id}/collected_items`
  - `GET` List collected items (requires OAuth scope `view_collection`).
    - Path: `user_id` (int).
    - Query: `category` (coin|banknote|exonumia), `type` (int), `collection` (int).
  - `POST` Add an item (requires `edit_collection` scope).
    - Path: `user_id` (int).
    - Body: JSON with `type` (int, required), optional `issue` (int), `quantity` (int, default `1`), `grade`
      (enum g/vg/f/vf/xf/au/unc), `for_swap` (bool), `private_comment`, `public_comment`, `price` (value+currency),
      `collection` (int), `storage_location`, `acquisition_place`, `acquisition_date` (YYYY-MM-DD), `serial_number`,
      `internal_id`, `weight`, `size`, `axis`, and nested `grading_details` (company, slab IDs, CAC sticker, strike,
      surface, designations).
- `/users/{user_id}/collected_items/{item_id}`
  - `GET` Retrieve a single collection item.
    - Path: `user_id` (int), `item_id` (int).
  - `PATCH` Update an item (requires `edit_collection` scope).
    - Path: `user_id` (int), `item_id` (int).
    - Body: Same structure as the `POST` payload, with every field optional and nullable where noted (e.g., `grade`,
      `issue`, `price`).
  - `DELETE` Remove an item (requires `edit_collection` scope).
    - Path: `user_id` (int), `item_id` (int).

## § 1.2 Version 2 (`https://api.numista.com/v2`)

Version 2 exposes every endpoint listed for version 3 with the same request parameters. In addition, the following
legacy paths remain accessible through `/v2` (all were removed from `/v3`):

- `/coins`
  - `GET` Search for coins.
    - Query: `lang` (enum en/es/fr, default `en`), `q` (string, required), `issuer` (string code),
      `page` (int, default `1`), `count` (int, default `50`).
  - `POST` Add a coin type using the deprecated `coin_update` schema (requires catalogue-edit permission).
    - Query: `lang` (enum en/es/fr, default `en`).
    - Body: `coin_update` JSON (localized `title`, `issuer`, `type`, `value`, `ruling_authority`, `shape`,
      `composition`, measurements, `orientation`, demonetization, calendar, `obverse`/`reverse`/`edge`, `mints`,
      `comments`, `related_coins`, `tags`, `references`).
- `/coins/{coin_id}`
  - `GET` Retrieve coin metadata (deprecated in favor of `/types/{type_id}`).
    - Path: `coin_id` (int).
    - Query: `lang` (enum en/es/fr, default `en`).
- `/coins/{coin_id}/issues`
  - `GET` List issues of a legacy coin entry.
    - Path: `coin_id` (int).
    - Query: `lang` (enum en/es/fr, default `en`).
  - `POST` Insert a legacy issue (same `issue_update` body as `/types/{type_id}/issues`).
    - Path: `coin_id` (int).
    - Query: `lang` (enum en/es/fr, default `en`).
- `/coins/{coin_id}/issues/{issue_id}/prices`
  - `GET` Return price estimates for a legacy issue.
    - Path: `coin_id` (int), `issue_id` (int).
    - Query: `currency` (ISO 4217 code, default `EUR`), `lang` (enum en/es/fr, default `en`).
- `/users/{user_id}/collected_coins`
  - `GET` Legacy summary of collected coins (requires OAuth scope `view_collection`).
    - Path: `user_id` (int).
    - Query: `lang` (enum en/es/fr, default `en`), `coin` (int coin-type filter).

## § 1.3 Version 1 (`https://api.numista.com/v1`)

Version 1 shares the same endpoint tree as version 2 (including the `/coins` and `/users/{user_id}/collected_coins`
legacy paths above). Parameter names are identical, but some response fields remain in their original camelCase form
(`minYear`, `maxYear`, `value`, etc.) as noted inside `docs/numista-swagger.yml`.
