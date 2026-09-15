from pathlib import Path
from typing import Iterator, Tuple
import warnings

from qiskit import QuantumCircuit

from .config import BENCHMARK_DIR


class CircuitLoader:
    def load(
        self, id: str, transpiled: bool = False
    ) -> Iterator[Tuple[str, QuantumCircuit]]:
        """Yield one circuit or a batch of circuits as (id, QuantumCircuit) pairs.

        Examples:
            - load("disqco.mfpqc.qaoa.n64") -> yields many (id, QuantumCircuit)
            - load("disqco.mfpqc.qaoa.n64.prob0p5.reps1.1") -> yields a single (id, QuantumCircuit)
        """

        benchmark_path = BENCHMARK_DIR
        if not benchmark_path.exists():
            raise FileNotFoundError(
                f"Benchmark directory not found at {benchmark_path}. Please run the downloader to fetch the benchmarks."
            )

        id_parts = [part for part in id.split(".") if part]
        path = benchmark_path.joinpath(*id_parts)

        if path.is_dir():
            yield from self._load_batch(path, transpiled)
            return

        parent_directory = benchmark_path.joinpath(*id_parts[:-1])
        iteration = id_parts[-1] if id_parts else ""
        if parent_directory.is_dir() and iteration.isdigit():
            qasm_extension = ".transpiled.qasm" if transpiled else ".qasm"
            matching_files = sorted(
                parent_directory.glob(f"*_{iteration}{qasm_extension}")
            )
            if matching_files:
                circuit = QuantumCircuit.from_qasm_file(str(matching_files[0]))
                rel = matching_files[0].relative_to(benchmark_path).as_posix()
                key = rel.rsplit(".", 1)[0].replace("/", ".")
                yield (key, circuit)
                return

        raise FileNotFoundError(
            f"No circuit or batch found for ID: {id}\n"
            f"Expected directory: {path}\n"
            f"Expected parent directory: {parent_directory}"
        )

    def _load_batch(
        self, directory: Path, transpiled: bool
    ) -> Iterator[Tuple[str, QuantumCircuit]]:
        """Yield all QASM files from a directory recursively as
        `(dotted_id, QuantumCircuit)` pairs.
        """
        if not directory.is_dir():
            raise FileNotFoundError(f"Directory not found: {directory}")

        if transpiled:
            qasm_files = sorted(directory.rglob("*.transpiled.qasm"))
        else:
            all_qasm = sorted(directory.rglob("*.qasm"))
            qasm_files = [
                file_path
                for file_path in all_qasm
                if not file_path.name.endswith(".transpiled.qasm")
            ]

        if not qasm_files:
            raise FileNotFoundError(
                f"No {'transpiled' if transpiled else 'non-transpiled'} QASM files found in {directory}"
            )

        for qasm_file in qasm_files:
            try:
                circuit = QuantumCircuit.from_qasm_file(str(qasm_file))
            except Exception as exc:
                warnings.warn(
                    f"Skipping malformed QASM file {qasm_file}: {exc}",
                    RuntimeWarning,
                    stacklevel=2,
                )
                continue
            rel = qasm_file.relative_to(BENCHMARK_DIR).as_posix()
            key = rel.rsplit(".", 1)[0].replace("/", ".")
            yield (key, circuit)
