# QCeval

Quantum circuit evaluation and benchmarking for research and development.

[![CI](https://github.com/cake-lab/qceval/actions/workflows/ci.yaml/badge.svg?branch=main)](https://github.com/cake-lab/qceval/actions/workflows/ci.yaml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-3776AB.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

## Installation

Install the environment with [uv](https://docs.astral.sh/uv/):

```bash
uv sync
```

## Quick start

Download the benchmark collection, load a circuit, and calculate its metrics:

```python
from qceval import BenchmarkDownloader, CircuitLoader, CircuitMetricsEvaluator

BenchmarkDownloader.download_benchmarks()

circuits = CircuitLoader().load("qasmbench.small")
metrics = CircuitMetricsEvaluator().evaluate(circuits, ["qubit_count", "gate_count"])
print(metrics)
```

## Benchmark Location Configuration

By default, benchmark data is stored in `~/.qceval`.

The relevant environment variables are:

- `QCEVAL_HOME`: Where to store benchmark data (default: ~/.qceval).
- `QCEVAL_BENCHMARK_REPO_URL`: URL of the repository to download benchmark data from (default: <https://github.com/cake-lab/qceval.git>).
- `QCEVAL_BENCHMARKS_SOURCE_DIR`: (Optional) Absolute path to a local copy of the benchmark repository. If set, this will be used instead of downloading the benchmarks from the remote repository.

> [!NOTE]
>
> This environment variables can be set in a `.env` file in the repository root, or exported in your shell. You can see an example `.env` file in [docs/.env.example](docs/.env.example).

See [docs/configuration.md](docs/configuration.md) for the full setup notes.

## Development

Run the checks used by CI:

```bash
uv run ruff check src tests
uv run pytest tests/ -q
uv build
```

The package is licensed under the Apache License, Version 2.0. Benchmark files may have additional terms; see the license files distributed with the relevant benchmark collection.
