from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MetricSpec:
    """Describe a built-in metric exposed by `CircuitMetricsEvaluator`."""

    metric_id: str
    method_name: str
    description: str


"""
# METRICS
## BASELINE METRICS

- Qubit count
- Maximum qubit depth
- Maximum qubit depth ID
- Gate count
    - Single Gate count
    - Dual Gate count
- Circuit depth
- Circuit width

- Size factor

## QASMBENCH METRICS

- Operation Density / Gate density 
- Retention lifespan / FDM
- Measurement ratio / Measurement density
- Entanglement variance

## SUPERMARQ METRICS

- Communication
- Critical Depth
- Entanglement-ratio
- Parallelism
- Liveness
- Measurement

"""


BUILTIN_METRIC_SPECS: tuple[MetricSpec, ...] = (
    # Baseline metrics
    MetricSpec(
        "qubit_count",
        "_metric_qubit_count",
        "Total qubits in the circuit",
    ),
    MetricSpec(
        "maximum_qubit_depth",
        "_metric_maximum_qubit_depth",
        "Largest per-qubit gate depth",
    ),
    MetricSpec(
        "maximum_qubit_depth_id",
        "_metric_maximum_qubit_depth_id",
        "Qubit ID with the largest per-qubit gate depth",
    ),
    MetricSpec(
        "gate_count",
        "_metric_gate_count",
        "Legacy qubit-weighted gate count (sum of qubits touched per gate)",
    ),
    MetricSpec(
        "gate_node_count",
        "_metric_gate_node_count",
        "Raw DAG gate node count (each gate node counts as 1)",
    ),
    MetricSpec(
        "single_gate_count",
        "_metric_single_gate_count",
        "Total single-qubit gate count",
    ),
    MetricSpec(
        "dual_gate_count",
        "_metric_dual_gate_count",
        "Total dual-qubit gate count",
    ),
    MetricSpec(
        "dag_depth",
        "_metric_dag_depth",
        "DAG depth after barrier removal",
    ),
    MetricSpec(
        "circuit_depth",
        "_metric_circuit_depth",
        "Circuit matrix depth",
    ),
    MetricSpec(
        "circuit_width",
        "_metric_circuit_width",
        "Circuit width",
    ),
    MetricSpec(
        "size_factor",
        "_metric_size_factor",
        "Log-scaled legacy qubit-weighted gate count",
    ),
    MetricSpec(
        "maximum_dual_qubit_count",
        "_metric_maximum_dual_qubit_count",
        "Number of dual-qubit gates touching the most active qubit",
    ),
    MetricSpec(
        "measurement_count",
        "_metric_measurement_count",
        "Total measurement count",
    ),
    # QASMBench metrics
    MetricSpec(
        "gate_density",
        "_metric_gate_density",
        "Gate density (QASMBench)",
    ),
    MetricSpec(
        "retention_lifespan",
        "_metric_retention_lifespan",
        "Log-scaled retention lifespan / FDM (QASMBench)",
    ),
    MetricSpec(
        "measurement_density",
        "_metric_measurement_density",
        "Measurement density (QASMBench)",
    ),
    MetricSpec(
        "entanglement_variance",
        "_metric_entanglement_variance",
        "Entanglement variance (QASMBench)",
    ),
    # SUPERMARQ metrics
    MetricSpec(
        "communication_supermarq",
        "_metric_communication_supermarq",
        "Communication (SupermarQ)",
    ),
    MetricSpec(
        "critical_depth_supermarq",
        "_metric_critical_depth_supermarq",
        "Critical Depth (SupermarQ)",
    ),
    MetricSpec(
        "entanglement_ratio_supermarq",
        "_metric_entanglement_ratio_supermarq",
        "Entanglement Ratio (SupermarQ)",
    ),
    MetricSpec(
        "parallelism_supermarq",
        "_metric_parallelism_supermarq",
        "Parallelism (SupermarQ)",
    ),
    MetricSpec(
        "liveness_supermarq",
        "_metric_liveness_supermarq",
        "Liveness (SupermarQ)",
    ),
    MetricSpec(
        "measurement_supermarq",
        "_metric_measurement_supermarq",
        "Measurement (SupermarQ)",
    ),
)
