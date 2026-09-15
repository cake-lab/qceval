from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import Callable

import networkx as nx
import numpy as np
import qiskit
from tabulate import tabulate

from .metric_specs import BUILTIN_METRIC_SPECS


MetricValue = int | float | str


@dataclass(frozen=True)
class _CircuitAnalysis:
    working_circuit: qiskit.QuantumCircuit
    qubit_count: int
    cbit_count: int
    measurement_count: int
    gate_node_count: int
    gate_count_legacy: int
    dual_gate_count: int
    dual_gate_count_id: dict[int, int]
    single_gate_count: int
    maximum_qubit_depth_id: str
    maximum_qubit_depth: int
    maximum_dual_qubit_count: int
    dag_depth: int
    circuit_depth: int


# TODO change to MetricsEvaluator?
# TODO put at top level module?
class CircuitMetricsEvaluator:
    """Evaluate named circuits and compute a configurable metric set.

    The evaluator uses Qiskit circuit analysis to compute a variety of built-in metrics, and can be extended with custom metrics as needed.
    Built-in metrics are registered from `metric_specs.py`, and callers can
    add their own metrics with `register_metric`.
    """

    def __init__(self) -> None:
        self.metric_registry: dict[str, Callable[[_CircuitAnalysis], MetricValue]] = {}
        self.metric_descriptions: dict[str, str] = {}

        self._register_builtin_metrics()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    @property
    def metric_ids(self) -> tuple[str, ...]:
        return tuple(self.metric_registry)

    def register_metric(
        self,
        metric_id: str,
        compute_fn: Callable[[_CircuitAnalysis], MetricValue],
        description: str = "",
        overwrite: bool = False,
    ) -> None:
        """Register or replace a metric implementation.

        Args:
            metric_id: Public identifier used when selecting metrics.
            compute_fn: Callable that computes the metric from analysis data.
            description: Optional human-readable description.
            overwrite: Allow replacing an existing metric with the same id.
        """
        if not overwrite and metric_id in self.metric_registry:
            raise ValueError(f"Metric '{metric_id}' is already registered.")
        self.metric_registry[metric_id] = compute_fn
        if description:
            self.metric_descriptions[metric_id] = description

    def evaluate(
        self,
        circuits: Iterable[tuple[str, qiskit.QuantumCircuit]],
        metrics: Sequence[str] | None = None,
    ) -> dict[str, dict[str, MetricValue]]:
        """Evaluate one or more named circuits.

        Args:
            circuits: Iterable of (circuit_id, QuantumCircuit) tuples.
                Can be a generator from CircuitLoader, list, or other iterable.
            metrics: Optional subset of metric ids to compute.

        Returns:
            Nested mapping of circuit id to metric id to metric value.
        """
        metric_ids = self._resolve_metric_ids(metrics)
        results = {}
        try:
            for circuit_id, circuit in circuits:
                results[str(circuit_id)] = self._evaluate_circuit(circuit, metric_ids)
        except TypeError as e:
            raise TypeError(
                "evaluate expects an iterable of (circuit_id, QuantumCircuit) tuples. "
                "This can come from CircuitLoader.load() or a list of tuples."
            ) from e
        except ValueError as e:
            raise TypeError(
                "evaluate expects an iterable of (circuit_id, QuantumCircuit) tuples. "
                "This can come from CircuitLoader.load() or a list of tuples."
            ) from e
        return results

    def print_metrics(
        self, results: dict[str, dict[str, MetricValue]], fmt: str = "grid"
    ) -> None:
        """Print metrics as a table. Handles both single and multiple circuits.

        Args:
            results: Output from evaluate() - dict mapping circuit_id to metrics dict.
            fmt: Table format (tabulate format string, e.g. 'grid', 'plain', 'github').
        """
        if not results:
            print("No results to display.")
            return

        # Check if this is a single circuit or multiple
        is_single_circuit = len(results) == 1

        if is_single_circuit:
            # Single circuit: detailed table with descriptions
            metrics = list(results.values())[0]
            table_data = []
            for metric_id, value in metrics.items():
                description = self.metric_descriptions.get(metric_id, "")
                table_data.append([metric_id, description, value])
            print(
                tabulate(
                    table_data,
                    headers=["Metric", "Description", "Value"],
                    tablefmt=fmt,
                )
            )
        else:
            # Multiple circuits: comparison table
            # Get all unique metrics across all circuits
            all_metrics = set()
            for circuit_metrics in results.values():
                all_metrics.update(circuit_metrics.keys())
            all_metrics = sorted(all_metrics)

            # Build table with circuits as columns
            table_data = []
            for metric_id in all_metrics:
                row = [metric_id]
                for circuit_id in sorted(results.keys()):
                    value = results[circuit_id].get(metric_id, "N/A")
                    row.append(value)
                table_data.append(row)

            headers = ["Metric"] + sorted(results.keys())
            print(
                tabulate(
                    table_data,
                    headers=headers,
                    tablefmt=fmt,
                )
            )

    def _register_builtin_metrics(self) -> None:
        """Register the built-in metrics declared in `metric_specs.py`."""
        for spec in BUILTIN_METRIC_SPECS:
            self.register_metric(
                spec.metric_id,
                getattr(self, spec.method_name),
                spec.description,
            )

    # ------------------------------------------------------------------
    # Registration Helpers
    # ------------------------------------------------------------------

    def _resolve_metric_ids(self, metrics: Sequence[str] | None) -> list[str]:
        """Normalize and de-duplicate requested metric ids."""
        if not metrics:
            return list(self.metric_registry)

        resolved: list[str] = []
        seen: set[str] = set()
        for metric_id in metrics:
            if metric_id not in self.metric_registry:
                available_metric_ids = ", ".join(self.metric_registry)
                raise ValueError(
                    f"Unknown metric '{metric_id}'. Available metric ids: {available_metric_ids}"
                )
            if metric_id in seen:
                continue
            seen.add(metric_id)
            resolved.append(metric_id)
        return resolved

    def _evaluate_circuit(
        self, circuit: qiskit.QuantumCircuit, metric_ids: Sequence[str]
    ) -> dict[str, MetricValue]:
        """Analyze one circuit and compute the requested metrics."""
        if not isinstance(circuit, qiskit.QuantumCircuit):
            raise TypeError("evaluate expects qiskit.QuantumCircuit values.")

        analysis = self._analyze_circuit(circuit)
        return {
            metric_id: self.metric_registry[metric_id](analysis)
            for metric_id in metric_ids
        }

    # ------------------------------------------------------------------
    # Circuit Analysis
    # ------------------------------------------------------------------

    def _analyze_circuit(self, circuit: qiskit.QuantumCircuit) -> _CircuitAnalysis:
        """Build a DAG view and precompute all shared metrics.

        Analyzes the circuit as provided. For consistent gate counting,
        callers should decompose and normalize circuits before evaluation.
        """
        working_circuit = circuit.copy()
        dag = qiskit.converters.circuit_to_dag(working_circuit)

        qubit_count = int(circuit.num_qubits)
        cbit_count = int(circuit.num_clbits)

        # Measurements
        measurement_count = sum(1 for op in dag.op_nodes() if op.name == "measure")

        # Gates and two-qubit ops
        gate_nodes = list(dag.gate_nodes())
        gate_node_count = int(len(gate_nodes))
        gate_count_legacy = self._calc_legacy_gate_count(gate_nodes)
        two_q_ops = list(dag.two_qubit_ops())
        dual_gate_count = int(len(two_q_ops))

        dual_gate_count_id: dict[int, int] = {}
        for op in two_q_ops:
            for q in op.qargs:
                qi = working_circuit.qubits.index(q)
                dual_gate_count_id[qi] = dual_gate_count_id.get(qi, 0) + 1

        single_gate_count = int(gate_node_count - dual_gate_count)

        circ_matrix, dag_depth = self._get_circuit_matrix(working_circuit, qubit_count)

        qubit_depths = self._get_qubit_operation_depths(
            gate_nodes, working_circuit, qubit_count
        )
        maximum_qubit_depth_id = ""
        maximum_qubit_depth = 0
        if qubit_depths:
            max_idx = int(np.argmax(qubit_depths))
            maximum_qubit_depth_id = f"q{max_idx}"
            maximum_qubit_depth = int(qubit_depths[max_idx])

        maximum_dual_qubit_count = 0
        if maximum_qubit_depth_id:
            mq_idx = int(maximum_qubit_depth_id[1:])
            maximum_dual_qubit_count = dual_gate_count_id.get(mq_idx, 0)

        return _CircuitAnalysis(
            working_circuit=working_circuit,
            qubit_count=qubit_count,
            cbit_count=cbit_count,
            measurement_count=measurement_count,
            gate_node_count=gate_node_count,
            gate_count_legacy=gate_count_legacy,
            dual_gate_count=dual_gate_count,
            dual_gate_count_id=dual_gate_count_id,
            single_gate_count=single_gate_count,
            maximum_qubit_depth_id=maximum_qubit_depth_id,
            maximum_qubit_depth=maximum_qubit_depth,
            maximum_dual_qubit_count=maximum_dual_qubit_count,
            dag_depth=dag_depth,
            circuit_depth=circ_matrix.shape[1],
        )

    # ------------------------------------------------------------------
    # Built-in Metrics
    # ------------------------------------------------------------------

    def _metric_qubit_count(self, analysis: _CircuitAnalysis) -> int:
        return analysis.qubit_count

    def _metric_maximum_qubit_depth(self, analysis: _CircuitAnalysis) -> int:
        return analysis.maximum_qubit_depth

    def _metric_maximum_qubit_depth_id(self, analysis: _CircuitAnalysis) -> str:
        return analysis.maximum_qubit_depth_id

    def _metric_gate_count(self, analysis: _CircuitAnalysis) -> int:
        return analysis.gate_count_legacy

    def _metric_gate_node_count(self, analysis: _CircuitAnalysis) -> int:
        return analysis.gate_node_count

    def _metric_single_gate_count(self, analysis: _CircuitAnalysis) -> int:
        return analysis.single_gate_count

    def _metric_dual_gate_count(self, analysis: _CircuitAnalysis) -> int:
        return analysis.dual_gate_count

    def _metric_dag_depth(self, analysis: _CircuitAnalysis) -> int:
        return analysis.dag_depth

    def _metric_circuit_depth(self, analysis: _CircuitAnalysis) -> int:
        return analysis.circuit_depth

    def _metric_circuit_width(self, analysis: _CircuitAnalysis) -> int:
        return analysis.qubit_count

    def _metric_size_factor(self, analysis: _CircuitAnalysis) -> float:
        return self._calc_size_factor(analysis.gate_count_legacy)

    def _metric_maximum_dual_qubit_count(self, analysis: _CircuitAnalysis) -> int:
        return analysis.maximum_dual_qubit_count

    def _metric_measurement_count(self, analysis: _CircuitAnalysis) -> int:
        return analysis.measurement_count

    def _metric_gate_density(self, analysis: _CircuitAnalysis) -> float:
        """Compute QASMBench gate density from single- and two-qubit activity."""
        return self._calc_operation_density(
            analysis.single_gate_count,
            analysis.dual_gate_count,
            analysis.dag_depth,
            analysis.qubit_count,
        )

    def _metric_retention_lifespan(self, analysis: _CircuitAnalysis) -> float:
        """Return the log-scaled depth proxy used by the retention lifespan metric."""
        return self._calc_fdm(analysis.dag_depth)

    def _metric_measurement_density(self, analysis: _CircuitAnalysis) -> float:
        """Compute the measurement density metric used by QASMBench."""
        return self._calc_measurement_density(
            analysis.measurement_count, analysis.dag_depth, analysis.qubit_count
        )

    def _metric_entanglement_variance(self, analysis: _CircuitAnalysis) -> float:
        """Measure how unevenly two-qubit interactions are distributed."""
        return self._calc_entanglement_variance(
            analysis.qubit_count, analysis.dual_gate_count, analysis.dual_gate_count_id
        )

    def _metric_communication_supermarq(self, analysis: _CircuitAnalysis) -> float:
        """Compute the SUPERMARQ communication score from the DAG connectivity."""
        return self._compute_communication(
            analysis.working_circuit, analysis.qubit_count
        )

    def _metric_critical_depth_supermarq(self, analysis: _CircuitAnalysis) -> float:
        """Compute the SUPERMARQ depth score from the two-qubit critical path."""
        return self._compute_critical_depth(analysis.working_circuit)

    def _metric_entanglement_ratio_supermarq(self, analysis: _CircuitAnalysis) -> float:
        """Compute the SUPERMARQ entanglement score from two-qubit operation share."""
        return self._compute_entanglement_ratio(analysis.working_circuit)

    def _metric_parallelism_supermarq(self, analysis: _CircuitAnalysis) -> float:
        """Compute the SUPERMARQ parallelism score from DAG depth versus gate count."""
        return self._compute_parallelism(analysis.working_circuit)

    def _metric_liveness_supermarq(self, analysis: _CircuitAnalysis) -> float:
        """Compute the SUPERMARQ liveness score from per-layer qubit activity."""
        return self._compute_liveness(analysis.working_circuit, analysis.qubit_count)

    def _metric_measurement_supermarq(self, analysis: _CircuitAnalysis) -> float:
        """Compute the SUPERMARQ measurement score from reset placement."""
        return self._compute_measurement(analysis.working_circuit)

    ############################################################################
    # Metric Calculation                                                       #
    ############################################################################

    @staticmethod
    def _get_qubit_operation_depths(
        gate_nodes: Sequence[object],
        circuit: qiskit.QuantumCircuit,
        qubit_count: int,
    ) -> list[int]:
        """Count how many gate operations touch each qubit (legacy depth semantics)."""
        qubit_depths = [0] * qubit_count
        for op in gate_nodes:
            for qubit in op.qargs:
                qubit_index = circuit.qubits.index(qubit)
                qubit_depths[qubit_index] += 1
        return qubit_depths

    @staticmethod
    def _calc_legacy_gate_count(
        gate_nodes: Sequence[object],
    ) -> int:
        """Count gates with legacy semantics: per gate, multiply by touched qubits.

        A single-qubit gate counts as 1, a two-qubit gate counts as 2, and so on."""
        return int(sum(len(op.qargs) for op in gate_nodes))

    @staticmethod
    def _calc_size_factor(gate_count: int) -> float:
        if gate_count <= 0:
            return 0.0
        return float(np.log(gate_count))

    @staticmethod
    def _calc_operation_density(
        single_gate_count: int,
        dual_gate_count: int,
        depth: int,
        qubit_count: int,
    ) -> float:
        if depth == 0 or qubit_count == 0:
            return 0.0
        return float((single_gate_count + 2 * dual_gate_count) / (depth * qubit_count))

    @staticmethod
    def _calc_fdm(depth: int) -> float:
        if depth <= 0:
            return 0.0
        return float(np.log(depth))

    @staticmethod
    def _calc_measurement_density(
        measurement_count: int, depth: int, qubit_count: int
    ) -> float:
        if measurement_count == 0 or qubit_count == 0 or depth == 0:
            return 0.0
        return float(np.log(qubit_count * depth) / measurement_count)

    @staticmethod
    def _get_circuit_matrix(
        circuit: qiskit.QuantumCircuit,
        qubit_count: int,
    ) -> tuple[np.ndarray, int]:
        """Build a qubit-by-layer activity matrix and return it with the DAG depth."""
        dag = qiskit.converters.circuit_to_dag(circuit)
        circ_matrix = np.zeros((qubit_count, dag.depth()))
        for i, layer in enumerate(dag.layers()):
            for op in layer["partition"]:
                for qubit in op:
                    qubit_index = circuit.qubits.index(qubit)
                    circ_matrix[qubit_index, i] = 1
        return circ_matrix, dag.depth()

    @staticmethod
    def _calc_entanglement_variance(
        qubit_count: int,
        dual_gate_count: int,
        dual_gate_count_id: dict[int, int],
    ) -> float:
        if qubit_count == 0:
            return 0.0
        avg_cnot = 2 * dual_gate_count / qubit_count
        numerator = 0.0
        for value in dual_gate_count_id.values():
            numerator += np.square(value - avg_cnot)
        numerator = np.log(numerator + 1)
        return float(numerator / qubit_count)

    @staticmethod
    def _compute_communication(
        circuit: qiskit.QuantumCircuit, qubit_count: int
    ) -> float:
        """Measure the spread of two-qubit interactions across the register."""
        if qubit_count < 2:
            return 0.0
        dag = qiskit.converters.circuit_to_dag(circuit)
        graph = nx.Graph()
        for op in dag.two_qubit_ops():
            q1, q2 = op.qargs
            graph.add_edge(circuit.qubits.index(q1), circuit.qubits.index(q2))
        degree_sum = sum(graph.degree(node) for node in graph.nodes)
        return float(degree_sum / (qubit_count * (qubit_count - 1)))

    @staticmethod
    def _compute_critical_depth(circuit: qiskit.QuantumCircuit) -> float:
        """Compute the average longest-path contribution of two-qubit gate types."""
        dag = qiskit.converters.circuit_to_dag(circuit)
        dag.remove_all_ops_named("barrier")
        two_q_gates = {op.name for op in dag.two_qubit_ops()}
        n_ed = 0
        longest_path_counts = dag.count_ops_longest_path()
        for name in two_q_gates:
            n_ed += longest_path_counts.get(name, 0)
        n_e = len(dag.two_qubit_ops())
        if n_ed == 0 or n_e == 0:
            return 0.0
        return float(n_ed / n_e)

    @staticmethod
    def _compute_entanglement_ratio(circuit: qiskit.QuantumCircuit) -> float:
        """Measure the fraction of gate nodes that are two-qubit operations."""
        dag = qiskit.converters.circuit_to_dag(circuit)
        dag.remove_all_ops_named("barrier")
        gate_nodes = len(dag.gate_nodes())
        if gate_nodes == 0:
            return 0.0
        return float(len(dag.two_qubit_ops()) / gate_nodes)

    @staticmethod
    def _compute_parallelism(circuit: qiskit.QuantumCircuit) -> float:
        """Estimate parallelism as the gap between depth and gate count."""
        dag = qiskit.converters.circuit_to_dag(circuit)
        dag.remove_all_ops_named("barrier")
        gate_nodes = len(dag.gate_nodes())
        if gate_nodes == 0:
            return 0.0
        return float(max(1 - (circuit.depth() / gate_nodes), 0))

    @staticmethod
    def _compute_liveness(circuit: qiskit.QuantumCircuit, qubit_count: int) -> float:
        """Estimate how much of the register is active throughout the circuit."""
        dag = qiskit.converters.circuit_to_dag(circuit)
        dag.remove_all_ops_named("barrier")
        if dag.depth() == 0 or qubit_count == 0:
            return 0.0
        activity_matrix = np.zeros((qubit_count, dag.depth()))
        for i, layer in enumerate(dag.layers()):
            for op in layer["partition"]:
                for qubit in op:
                    qubit_index = circuit.qubits.index(qubit)
                    activity_matrix[qubit_index, i] = 1
        return float(np.sum(activity_matrix) / (qubit_count * dag.depth()))

    @staticmethod
    def _compute_measurement(circuit: qiskit.QuantumCircuit) -> float:
        """Measure how often reset operations appear relative to circuit depth."""
        temporary_circuit = circuit.copy()
        temporary_circuit.remove_final_measurements()
        dag = qiskit.converters.circuit_to_dag(temporary_circuit)
        dag.remove_all_ops_named("barrier")
        gate_depth = dag.depth()
        if gate_depth == 0:
            return 0.0
        reset_moments = 0
        for layer in dag.layers():
            reset_present = False
            for op in layer["graph"].op_nodes():
                if op.name == "reset":
                    reset_present = True
            if reset_present:
                reset_moments += 1
        return float(reset_moments / gate_depth)
