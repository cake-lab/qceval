import shutil
import subprocess
import tempfile
from pathlib import Path

from .config import (
    BENCHMARK_DIR,
    QCEVAL_BENCHMARK_REPO_URL,
    QCEVAL_BENCHMARKS_SOURCE_DIR,
    RAW_DATA_DIR,
    REPO_ROOT,
)


class BenchmarkDownloader:
    @classmethod
    def download_benchmarks(cls):
        """Download benchmarks from the configured source directory or the default repo URL."""
        if BENCHMARK_DIR.exists():
            print(f"Benchmarks already exist at {BENCHMARK_DIR}")
            return

        RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

        if QCEVAL_BENCHMARKS_SOURCE_DIR:
            source_dir = Path(QCEVAL_BENCHMARKS_SOURCE_DIR)
            if not source_dir.is_absolute():
                source_dir = REPO_ROOT / source_dir
            source_dir = source_dir.resolve()

            if not source_dir.exists():
                raise FileNotFoundError(
                    f"Benchmark source directory does not exist: {source_dir}"
                )

            benchmark_src = source_dir / "benchmarks"
            if not benchmark_src.exists():
                raise FileNotFoundError(
                    f"Benchmark directory not found in source checkout: {benchmark_src}"
                )

            print(
                f"Downloading benchmarks from source dir {benchmark_src} to {BENCHMARK_DIR}"
            )
            shutil.copytree(benchmark_src, BENCHMARK_DIR)
            return

        repo_url = QCEVAL_BENCHMARK_REPO_URL
        temp_dir = Path(
            tempfile.mkdtemp(prefix="qceval-benchmarks-", dir=str(RAW_DATA_DIR))
        )
        print(f"Downloading benchmarks from repo URL {repo_url} to {temp_dir}")
        subprocess.run(["git", "clone", repo_url, str(temp_dir)], check=True)

        benchmark_src = temp_dir / "benchmarks"
        if not benchmark_src.exists():
            raise FileNotFoundError(
                f"Expected benchmark directory not found in cloned repository: {benchmark_src}"
            )

        shutil.move(str(benchmark_src), str(BENCHMARK_DIR))
        shutil.rmtree(temp_dir, ignore_errors=True)

    @staticmethod
    def clean_all():
        """Clean all downloaded benchmarks and raw data."""
        if RAW_DATA_DIR.exists():
            print("Cleaning raw data...")
            shutil.rmtree(RAW_DATA_DIR)
        if BENCHMARK_DIR.exists():
            print("Cleaning all benchmarks...")
            shutil.rmtree(BENCHMARK_DIR)
