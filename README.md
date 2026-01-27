# Sports Analytics

> **Note**: This project is currently under active development. Some features and components are still in progress.

An end-to-end machine learning project demonstrating a complete data pipeline from ingestion to model training. This
project showcases modern data engineering and ML practices using NHL game data as a real-world example.

> **NHL API Documentation**: This project uses the NHL API (`https://api-web.nhle.com/v1`). Special thanks to [Zach M (@Zmalski)](https://github.com/Zmalski) for maintaining the comprehensive [NHL API Reference](https://github.com/Zmalski/NHL-API-Reference) documentation that serves as an invaluable resource for understanding the available endpoints and data structures.

## Overview

This project implements a complete data pipeline following these stages:

1. **Data Extraction**: Automated data ingestion from the NHL's API
2. **Data Loading**: Partitioned storage using DuckDB for efficient querying
3. **Data Transformation**: SQL-based transformations with DBT and comprehensive data quality testing
4. **Model Training**: Machine learning model development (planned)

## Architecture

The project uses a modern data stack:

- **[Dagster](https://dagster.io/)**: Orchestration and workflow management with asset-based pipeline
- **[DuckDB](https://duckdb.org/)**: Embedded analytical database for data storage and querying
- **[Data Build Tool (DBT)](https://www.getdbt.com/product/dbt)**: SQL-based transformation layer
- **[Scikit-Learn](https://scikit-learn.org/stable/)**: Fundamental library for data processing and ML

### Current Implementation

The pipeline currently includes:

- **ELT Pipeline**: Daily-partitioned extraction of NHL game data from the NHL API
- **Data Assets**: Dagster assets for orchestrating data ingestion
- **API Integration**: Custom NHL API resource with error handling and support for game schedules, scores, play-by-play data, and more
- **Storage Layer**: DuckDB with partition support for time-series data
- **DBT Integration**: Fully configured transformation layer with Dagster integration
- **Data Quality**: Multiple comprehensive tests across all data sources using DBT expectations
- **Testing**: Unit tests for core utilities and data processing with CI/CD via GitHub Actions

## Project Structure

```text
sports-analytics/
├── src/sports_analytics/
│   ├── analytics/               # DBT project root
│   │   ├── dbt_project.yml      # DBT configuration
│   │   ├── profiles.yml         # DBT connection profiles
│   │   ├── packages.yml         # DBT package dependencies
│   │   ├── models/
│   │   │   ├── sources/
│   │   │   │   └── nhl.yml      # Source definitions with 28+ tests
│   │   │   └── staging/
│   │   │       └── stg_nhl_players.sql  # Player staging model
│   │   └── dbt_packages/        # Installed DBT packages
│   ├── defs/
│   │   ├── nhl/
│   │   │   ├── raw.py           # NHL raw data ingestion assets
│   │   │   ├── partitions.py    # Partition definitions
│   │   │   └── constants.py     # Configuration constants
│   │   ├── dbt.py               # DBT-Dagster integration
│   │   ├── project.py           # DBT project configuration
│   │   └── resources.py         # Dagster resources (DB, API, DBT)
│   ├── utils/
│   │   ├── apis.py              # API client implementations
│   │   └── helpers.py           # Utility functions
│   └── definitions.py           # Main Dagster definitions
├── tests/
│   └── unit/                    # Unit test suite
│       ├── assets/              # Asset tests
│       └── utils/               # Utility tests
└── pyproject.toml               # Project dependencies
```

## Getting Started

### Prerequisites

- Python 3.12 or higher (but less than 3.14)
- UV package manager (recommended) or pip

### Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd sports-analytics
```

2. Install dependencies:

```bash
uv sync
```

### Configuration

Create a `.env` file in the project root:

```dotenv
# DuckDB
DUCKDB_DATABASE=<path/to/db/file.duckdb>

# DBT
DBT_TARGET=dev

# APIs
NHL_API_BASE_URL=https://api-web.nhle.com/v1
```

#### MotherDuck Integration (Optional)

If you would like to try out [MotherDuck](https://motherduck.com/) for cloud-based DuckDB, you can
sign up
and [create a token](https://motherduck.com/docs/key-tasks/authenticating-and-connecting-to-motherduck/authenticating-to-motherduck/#authentication-using-an-access-token).

Update your `.env` file:

```dotenv
# DuckDB with MotherDuck
DUCKDB_DATABASE=md:<database>
MOTHERDUCK_TOKEN=<token>

# DBT
DBT_TARGET=dev

# APIs
NHL_API_BASE_URL=https://api-web.nhle.com/v1
```

### Running the Pipeline

Start the Dagster web interface:

```bash
dg dev
```

Navigate to `http://localhost:3000` to view and materialize assets.

### Running Tests

Execute the test suite:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=sports_analytics
```

### Data Quality Testing

The project implements comprehensive data quality testing using DBT:

**Source Tests** (28+ tests across 3 data sources):

1. **Games Data** (`raw_games.nhl_games_final`):
   - Unique game IDs and compound uniqueness checks
   - Game type validation (regular season, postseason)
   - Game state verification (only complete games)
   - Score and shot range validations
   - Period type validation

2. **Standings Data** (`raw_standings.nhl_standings_now`):
   - Exact row count (32 NHL teams)
   - Conference and division validation
   - Games played range checks
   - Team naming conventions

3. **Player Data** (`raw_players.nhl_players`):
   - Player ID uniqueness
   - Position, shoots/catches validation
   - Physical attributes (height, weight) range checks
   - Sweater number validation

Run DBT tests:

```bash
dbt test --project-dir src/sports_analytics/analytics
```

## Features

### Implemented

- **Data Ingestion**:
  - Daily-partitioned NHL game results (`raw_nhl_games_final`)
  - Current NHL team standings (`raw_nhl_standings_now`)
  - Player roster data for all 32 teams (`raw_nhl_players`)
  - NHL API integration with error handling (using `https://api-web.nhle.com/v1`)
- **Data Storage**:
  - DuckDB storage with partition management
  - Automated removal of incomplete games
  - Column name standardization (snake_case)
- **Data Transformation**:
  - DBT integration with Dagster
  - Custom asset key mapping for seamless integration
  - Staging models for data transformation
  - DBT packages: `dbt_expectations` (v0.10.10), `dbt_date` (v0.17.1)
- **Data Quality**:
  - 28+ comprehensive source tests across all data sources
  - Validation for uniqueness, ranges, types, and business logic
  - Automated testing using DBT expectations
- **Testing & CI/CD**:
  - Comprehensive unit test suite
  - GitHub Actions CI pipeline (Python 3.12, 3.13)
  - Mock fixtures for API responses

### In Progress

- Additional DBT staging and mart models
- Enhanced feature transformations for ML readiness
- Expanded data quality monitoring

### Planned

- Feature engineering for ML models
- ML model training pipeline
- Model evaluation and versioning
- Prediction API

## Development

### Code Quality

The project uses:

- **[ruff](https://docs.astral.sh/ruff/)**: Fast Python linter and formatter
- **[ty](https://docs.astral.sh/ty/)**: For autocomplete and type safety

### Contributing

This is an educational project demonstrating end-to-end ML pipeline development. Feel free to explore the code and
implementation patterns. If you want to add your features to it, feel free to fork the repository.

## Data Sources & Acknowledgments

This project uses the NHL API for data ingestion:
- **NHL Web API**: `https://api-web.nhle.com/v1`
- **API Documentation**: [NHL API Reference by Zach M (@Zmalski)](https://github.com/Zmalski/NHL-API-Reference)

Special thanks to Zach M for creating and maintaining comprehensive documentation of the NHL's API endpoints, which has been instrumental in understanding the available data and building this pipeline.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

This project is for educational purposes and demonstrates end-to-end ML pipeline development.
