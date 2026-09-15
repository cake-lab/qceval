import os
from pathlib import Path

from dotenv import load_dotenv


REPO_ROOT = Path(__file__).resolve().parents[2]
DOTENV_PATH = REPO_ROOT / ".env"
DEFAULT_QCEVAL_HOME = Path.home() / ".qceval"
DEFAULT_BENCHMARK_REPO_URL = "https://github.com/cake-lab/qceval.git"
DEFAULT_BENCHMARK_SOURCE_DIR = None

QCEVAL_HOME = os.getenv("QCEVAL_HOME", str(DEFAULT_QCEVAL_HOME))
QCEVAL_BENCHMARK_REPO_URL = os.getenv(
    "QCEVAL_BENCHMARK_REPO_URL", DEFAULT_BENCHMARK_REPO_URL
)
QCEVAL_BENCHMARKS_SOURCE_DIR = os.getenv("QCEVAL_BENCHMARKS_SOURCE_DIR")


def _resolve_path(raw_path: str | None) -> Path:
    if raw_path is None:
        return DEFAULT_QCEVAL_HOME

    path = Path(raw_path)
    if not path.is_absolute():
        return (REPO_ROOT / path).resolve()
    return path


def get_data_home() -> Path:
    """Return the benchmark data root.

    Precedence is:
    1. QCEVAL_HOME environment variable
    2. .env file in the repository root
    3. ~/.qceval
    """
    env_path = os.getenv("QCEVAL_HOME")
    if env_path:
        path = _resolve_path(env_path)
    else:
        load_dotenv(dotenv_path=DOTENV_PATH, override=False)
        env_path = os.getenv("QCEVAL_HOME")
        if env_path:
            path = _resolve_path(env_path)
        else:
            path = DEFAULT_QCEVAL_HOME

    path.mkdir(parents=True, exist_ok=True)
    return path


DATA_HOME = get_data_home()
BENCHMARK_DIR = DATA_HOME / "benchmarks"
RAW_DATA_DIR = DATA_HOME / "raw"
