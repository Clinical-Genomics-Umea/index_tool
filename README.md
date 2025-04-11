# Index Tool

A tool to save sequencing indices in a JSON-based format for Illumina sequencing.

## Features

Main reasons for converting to this format are:
1. A need to include override cycle patterns with the indexes.
2. Simplification of making Illumina samplesheet v2 files.
3. Ability to store all data as documents in a MongoDB database.

Indices can be imported for conversion from:
- Illumina index kit definition files (TSV)
- Custom CSV files

## Installation

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
python index_tool.py
```

## Development

### Setup Development Environment

1. Install development dependencies:
```bash
pip install -r requirements.txt
```

2. Run tests:
```bash
pytest
```

3. Code quality checks:
```bash
mypy .
pylint modules/
black .
```

## License

See the [LICENSE](LICENSE) file for details.
