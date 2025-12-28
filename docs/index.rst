numistalib Documentation
========================

Welcome to **numistalib**, a Python caching API wrapper for the Numista numismatic database with RFC 9111-compliant HTTP caching, intelligent rate limiting, and resilient retry logic.

Includes an optional command-line interface with rich terminal output and sixel image support.

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   installation
   quickstart
   python_api_guide
   cli_guide
   configuration
   advanced_usage

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/client
   api/services
   api/models
   api/cli

.. toctree::
   :maxdepth: 1
   :caption: Additional Information

   architecture
   contributing
   CHANGELOG.md
   license
   DEPLOYMENT
   README

Legal & Attribution
-------------------

This project is an unofficial wrapper and is not affiliated with Numista. When using data from Numista, provide appropriate attribution and comply with Numista’s terms:

- Conditions of use: https://en.numista.com/conditions.php
- Legal information: https://en.numista.com/legal.php
- Pricing API terms: https://en.numista.com/api/pricing.php

Respect Numista’s rate limits and any restrictions on caching or redistribution, particularly for pricing data.
Built With
----------

This project leverages the following excellent open-source libraries:

* `httpx <https://www.python-httpx.org/>`_ - Modern HTTP client with sync/async support
* `hishel <https://hishel.com/>`_ - RFC 9111-compliant HTTP caching
* `pydantic <https://docs.pydantic.dev/>`_ - Data validation and settings management
* `pyrate-limiter <https://github.com/vutran1710/PyrateLimiter>`_ - Sophisticated rate limiting
* `tenacity <https://tenacity.readthedocs.io/>`_ - Retry logic with exponential backoff
* `click <https://click.palletsprojects.com/>`_ - CLI framework
* `rich <https://rich.readthedocs.io/>`_ - Terminal UI and formatting
* `textual-image <https://github.com/InValidFire/textual-image>`_ - Sixel protocol image display

Features
--------

Core API Features
~~~~~~~~~~~~~~~~~

* **HTTP Caching**: RFC 9111-compliant persistent caching with hishel (7-day TTL)
* **Rate Limiting**: Configurable throttling (45 requests/minute default)
* **Retry Logic**: Exponential backoff with jitter for resilient requests
* **Complete API Coverage**: Access all Numista API endpoints
* **Type Safety**: Full Pydantic models with strict validation
* **Sync/Async Support**: Both synchronous and asynchronous client implementations

Optional CLI Features
~~~~~~~~~~~~~~~~~~~~~~

* **Rich Terminal UI**: Beautiful command-line interface with tables and colors
* **Sixel Image Display**: View coin images directly in compatible terminals (Kitty, WezTerm, iTerm2, mlterm, foot, yaft)
* **Table/Panel Modes**: Flexible output formats for different use cases

Quick Example
-------------

CLI Usage
~~~~~~~~~

.. code-block:: bash

   # Search for coins
   numistalib types search -q "dollar"
   
   # Get detailed information
   numistalib types get 95420
   
   # List all catalogues
   numistalib catalogues

Python API Usage
~~~~~~~~~~~~~~~~

.. code-block:: python

   from numistalib.client import NumistaApiClient
   from numistalib.config import Settings
   from numistalib.services.types.service import TypeService
   
   settings = Settings()
   
   with NumistaApiClient(settings) as client:
       service = TypeService(client)
       
       # Search for types
       results = service.search_types(query="dollar", page=1, count=10)
       for coin_type in results:
           print(f"{coin_type.numista_id}: {coin_type.title}")

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
