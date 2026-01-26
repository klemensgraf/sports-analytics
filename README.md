# Sports Analytics

> **Note**: This project is currently under active development. Some features and components are still in progress.

An end-to-end machine learning project demonstrating a complete data pipeline from ingestion to model training. This
project showcases modern data engineering and ML practices using NHL game data as a real-world example.

> **NHL API Documentation**: This project uses the NHL API (`https://api-web.nhle.com/v1`). Special thanks to [Zach M (@Zmalski)](https://github.com/Zmalski) for maintaining the comprehensive [NHL API Reference](https://github.com/Zmalski/NHL-API-Reference) documentation that serves as an invaluable resource for understanding the available endpoints and data structures.

## Overview

This project implements a complete data pipeline following these stages:

1. **Data Extraction**: Automated data ingestion from the NHL's API
2. **Data Loading**: Partitioned storage using DuckDB for efficient querying
3. **Data Transformation**: Data cleaning and feature engineering (in progress)
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
- **Testing**: Unit tests for core utilities and data processing

## Project Structure

```
sports-analytics/
├── src/sports_analytics/
│   ├── defs/
│   │   ├── hockey/
│   │   │   ├── nhl.py           # NHL data ingestion assets
│   │   │   ├── partitions.py    # Partition definitions
│   │   │   └── constants.py     # Configuration constants
│   │   └── resources.py         # Dagster resources (DB, API)
│   ├── utils/
│   │   ├── apis.py              # API client implementations
│   │   └── helpers.py           # Utility functions
│   └── definitions.py           # Main Dagster definitions
├── tests/
│   └── unit/                    # Unit test suite
└── pyproject.toml               # Project dependencies
```

## Getting Started

### Prerequisites

- Python 3.12 or higher (but less than 3.15)
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

## Features

### Implemented

- Daily-partitioned data ingestion for NHL games
- NHL API integration with error handling (using `https://api-web.nhle.com/v1`)
- DuckDB storage with partition management
- Automated removal of incomplete games
- Column name standardization (snake_case)
- Comprehensive unit testing

### In Progress

- DBT transformation models for data cleaning
- Additional data sources (player stats, team stats)
- Data quality checks and validation

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
