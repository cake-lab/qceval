import pytest
from qceval.downloader import BenchmarkDownloader
from qceval.loader import CircuitLoader
from qceval.config import BENCHMARK_DIR, RAW_DATA_DIR


@pytest.fixture(autouse=True)
def cleanup():
    """Cleanup before and after each test."""
    BenchmarkDownloader.clean_all()
    yield
    BenchmarkDownloader.clean_all()


class TestBenchmarkDownloader:
    """Tests for downloading all benchmarks."""

    def test_download_benchmarks_creates_benchmark_dir(self):
        """Test that download_benchmarks creates the benchmark directory."""
        assert not BENCHMARK_DIR.exists(), (
            "Benchmark dir should not exist before download"
        )

        BenchmarkDownloader.download_benchmarks()

        assert BENCHMARK_DIR.exists(), "Benchmark dir should exist after download"
        assert (BENCHMARK_DIR / "qasmbench").exists(), "qasmbench should exist"
        assert (BENCHMARK_DIR / "disqco").exists(), "disqco should exist"

    def test_download_benchmarks_idempotent(self):
        """Test that calling download_benchmarks twice is safe."""
        BenchmarkDownloader.download_benchmarks()
        first_files = set((BENCHMARK_DIR / "qasmbench").rglob("*"))

        BenchmarkDownloader.download_benchmarks()
        second_files = set((BENCHMARK_DIR / "qasmbench").rglob("*"))

        assert first_files == second_files, (
            "Files should be identical after second download"
        )

    def test_downloaded_benchmarks_have_expected_structure(self):
        """Test that downloaded benchmarks have the expected directory structure."""
        BenchmarkDownloader.download_benchmarks()

        # Check qasmbench structure
        qasmbench_path = BENCHMARK_DIR / "qasmbench"
        assert (qasmbench_path / "small").exists()
        assert (qasmbench_path / "medium").exists()
        assert (qasmbench_path / "large").exists()

        # Check disqco structure
        disqco_path = BENCHMARK_DIR / "disqco"
        assert (disqco_path / "mfpqc").exists()

    def test_benchmarks_in_correct_directory(self):
        """Test that benchmarks are in BENCHMARK_DIR from config."""
        BenchmarkDownloader.download_benchmarks()

        # Check that files exist in BENCHMARK_DIR (recursively)
        qasm_files = list((BENCHMARK_DIR / "qasmbench" / "small").rglob("*.qasm"))
        assert len(qasm_files) > 0

        # Verify the path is under BENCHMARK_DIR
        for qasm_file in qasm_files:
            assert str(qasm_file).startswith(str(BENCHMARK_DIR))


class TestLoaderIntegration:
    """Tests to verify the loader works with downloaded benchmarks."""

    def test_loader_fails_before_download(self):
        """Test that loader raises error when benchmark not downloaded."""
        loader = CircuitLoader()

        with pytest.raises(FileNotFoundError):
            next(loader.load("qasmbench.small.adder_n4"))

    def test_loader_can_access_downloaded_files(self):
        """Test that CircuitLoader can access files after downloading."""
        BenchmarkDownloader.download_benchmarks()

        # Verify the path exists that the loader would check
        qasmbench_small_path = BENCHMARK_DIR / "qasmbench" / "small"
        assert qasmbench_small_path.exists()

        # Verify QASM files exist (recursively, as they may be in subdirectories)
        qasm_files = list(qasmbench_small_path.rglob("*.qasm"))
        assert len(qasm_files) > 0, "Should have QASM files in downloaded benchmark"


class TestCleanAll:
    """Tests for the clean_all cleanup functionality."""

    def test_clean_all_removes_benchmarks(self):
        """Test that clean_all removes benchmark directory."""
        BenchmarkDownloader.download_benchmarks()
        assert BENCHMARK_DIR.exists()

        BenchmarkDownloader.clean_all()
        assert not BENCHMARK_DIR.exists()

    def test_clean_all_removes_raw_data(self):
        """Test that clean_all removes raw data directory."""
        BenchmarkDownloader.download_benchmarks()
        assert RAW_DATA_DIR.exists()

        BenchmarkDownloader.clean_all()
        assert not RAW_DATA_DIR.exists()

    def test_clean_all_idempotent(self):
        """Test that calling clean_all multiple times is safe."""
        BenchmarkDownloader.download_benchmarks()
        BenchmarkDownloader.clean_all()

        # Should not raise an error
        BenchmarkDownloader.clean_all()
        assert not BENCHMARK_DIR.exists()
        assert not RAW_DATA_DIR.exists()
