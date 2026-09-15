import os
from pathlib import Path

import pytest

repo_root = Path(__file__).parent.parent.resolve()
os.environ.setdefault("QCEVAL_HOME", str(repo_root))
from qceval.config import BENCHMARK_DIR  # noqa: E402


def pytest_report_header(config):
    return f"---\nbenchmark directory: {BENCHMARK_DIR}"


def pytest_collection_modifyitems(config, items):
    skip_downloader = pytest.mark.skip(reason="Skipping downloader tests in CI")
    for item in items:
        if "test_downloader.py" in str(item.fspath):
            item.add_marker(skip_downloader)
