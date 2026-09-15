from __future__ import annotations

from qiskit.transpiler.passes import RemoveBarriers

from qceval.loader import CircuitLoader
from qceval.metrics.evaluator import CircuitMetricsEvaluator


EXPECTED_METRICS = {
    "disqco.mfpqc.qv.n24.qv_n24_1": {
        "qubit_count": 24,
        "dag_depth": 168,
        "circuit_depth": 168,
        "circuit_width": 24,
        "maximum_qubit_depth": 168,
        "maximum_qubit_depth_id": "q0",
        "maximum_dual_qubit_count": 72,
        "retention_lifespan": 5.123963979403259,
        "gate_density": 1.0,
        "dual_gate_count": 864,
        "measurement_density": 0.0,
        "size_factor": 8.302017809751204,
        "gate_count": 4032,
        "single_gate_count": 2304,
        "measurement_count": 0,
        "entanglement_variance": 0.0,
        "communication_supermarq": 0.6739130434782609,
        "measurement_supermarq": 0.0,
        "critical_depth_supermarq": 0.08333333333333333,
        "entanglement_ratio_supermarq": 0.2727272727272727,
        "parallelism_supermarq": 0.946969696969697,
        "liveness_supermarq": 1.0,
    },
    "disqco.mfpqc.qft.n32.qft_n32": {
        "qubit_count": 32,
        "dag_depth": 247,
        "circuit_depth": 247,
        "circuit_width": 32,
        "maximum_qubit_depth": 125,
        "maximum_qubit_depth_id": "q0",
        "maximum_dual_qubit_count": 62,
        "retention_lifespan": 5.5093883366279774,
        "gate_density": 0.4433198380566802,
        "dual_gate_count": 992,
        "measurement_density": 0.0,
        "size_factor": 8.161660452056282,
        "gate_count": 3504,
        "single_gate_count": 1520,
        "measurement_count": 0,
        "entanglement_variance": 0.0,
        "communication_supermarq": 1.0,
        "measurement_supermarq": 0.0,
        "critical_depth_supermarq": 0.12298387096774194,
        "entanglement_ratio_supermarq": 0.39490445859872614,
        "parallelism_supermarq": 0.901671974522293,
        "liveness_supermarq": 0.4433198380566802,
    },
    "disqco.mfpqc.qaoa.n16.qaoa_n16_prob0p5_1": {
        "qubit_count": 16,
        "dag_depth": 65,
        "circuit_depth": 65,
        "circuit_width": 16,
        "maximum_qubit_depth": 27,
        "maximum_qubit_depth_id": "q6",
        "maximum_dual_qubit_count": 22,
        "retention_lifespan": 4.174387269895637,
        "gate_density": 0.2951923076923077,
        "dual_gate_count": 110,
        "measurement_density": 0.0,
        "size_factor": 5.726847747587197,
        "gate_count": 307,
        "single_gate_count": 87,
        "measurement_count": 0,
        "entanglement_variance": 0.36647694847488105,
        "communication_supermarq": 0.4583333333333333,
        "measurement_supermarq": 0.0,
        "critical_depth_supermarq": 0.38181818181818183,
        "entanglement_ratio_supermarq": 0.5583756345177665,
        "parallelism_supermarq": 0.6700507614213198,
        "liveness_supermarq": 0.2951923076923077,
    },
    "disqco.mfpqc.cp_scaling.f0p5.n16.cp_scaling_f0p5_n16_1": {
        "qubit_count": 16,
        "dag_depth": 70,
        "circuit_depth": 70,
        "circuit_width": 16,
        "maximum_qubit_depth": 44,
        "maximum_qubit_depth_id": "q3",
        "maximum_dual_qubit_count": 24,
        "retention_lifespan": 4.248495242049359,
        "gate_density": 0.4928571428571429,
        "dual_gate_count": 122,
        "measurement_density": 0.0,
        "size_factor": 6.313548046277095,
        "gate_count": 552,
        "single_gate_count": 308,
        "measurement_count": 0,
        "entanglement_variance": 0.35564746589525376,
        "communication_supermarq": 0.425,
        "measurement_supermarq": 0.0,
        "critical_depth_supermarq": 0.26229508196721313,
        "entanglement_ratio_supermarq": 0.2837209302325581,
        "parallelism_supermarq": 0.8372093023255813,
        "liveness_supermarq": 0.4928571428571429,
    },
    "qasmbench.small.bell_n4.bell_n4": {
        "qubit_count": 4,
        "dag_depth": 14,
        "circuit_depth": 14,
        "circuit_width": 4,
        "maximum_qubit_depth": 13,
        "maximum_qubit_depth_id": "q0",
        "maximum_dual_qubit_count": 4,
        "retention_lifespan": 2.6390573296152584,
        "gate_density": 0.7142857142857143,
        "dual_gate_count": 7,
        "measurement_density": 1.0063379226837874,
        "size_factor": 3.6888794541139363,
        "gate_count": 40,
        "single_gate_count": 26,
        "measurement_count": 4,
        "entanglement_variance": 0.17328679513998632,
        "communication_supermarq": 0.5,
        "measurement_supermarq": 0.0,
        "critical_depth_supermarq": 0.5714285714285714,
        "entanglement_ratio_supermarq": 0.21212121212121213,
        "parallelism_supermarq": 0.5757575757575757,
        "liveness_supermarq": 0.7857142857142857,
    },
    "qasmbench.small.adder_n4.adder_n4": {
        "qubit_count": 4,
        "dag_depth": 12,
        "circuit_depth": 12,
        "circuit_width": 4,
        "maximum_qubit_depth": 11,
        "maximum_qubit_depth_id": "q3",
        "maximum_dual_qubit_count": 6,
        "retention_lifespan": 2.4849066497880004,
        "gate_density": 0.6875,
        "dual_gate_count": 10,
        "measurement_density": 0.9678002527269728,
        "size_factor": 3.4965075614664802,
        "gate_count": 33,
        "single_gate_count": 13,
        "measurement_count": 4,
        "entanglement_variance": 0.27465307216702745,
        "communication_supermarq": 0.6666666666666666,
        "measurement_supermarq": 0.0,
        "critical_depth_supermarq": 0.6,
        "entanglement_ratio_supermarq": 0.43478260869565216,
        "parallelism_supermarq": 0.4782608695652174,
        "liveness_supermarq": 0.7708333333333334,
    },
}

BENCHMARK_CASES = [
    ("disqco.mfpqc.qv.n24.1", "disqco.mfpqc.qv.n24.qv_n24_1"),
    ("disqco.mfpqc.qft.n32", "disqco.mfpqc.qft.n32.qft_n32"),
    ("disqco.mfpqc.qaoa.n16.1", "disqco.mfpqc.qaoa.n16.qaoa_n16_prob0p5_1"),
    (
        "disqco.mfpqc.cp_scaling.f0p5.n16.1",
        "disqco.mfpqc.cp_scaling.f0p5.n16.cp_scaling_f0p5_n16_1",
    ),
    ("qasmbench.small.bell_n4", "qasmbench.small.bell_n4.bell_n4"),
    ("qasmbench.small.adder_n4", "qasmbench.small.adder_n4.adder_n4"),
]


def _load_metric_inputs(benchmark_id: str):
    loader = CircuitLoader()
    loaded_circuits = loader.load(benchmark_id)
    circuit_id, circuit = next(loaded_circuits)
    normalized_circuit = RemoveBarriers()(circuit.copy()).decompose(reps=10)
    return [(circuit_id, normalized_circuit)]


def _assert_metrics_match(computed: dict, expected: dict) -> None:
    for metric_name, expected_value in expected.items():
        computed_value = computed[metric_name]

        assert computed_value == expected_value, (
            f"{metric_name}: computed {computed_value!r} does not match expected {expected_value!r}"
        )


def test_qasm_metrics_match_expected_values():
    evaluator = CircuitMetricsEvaluator()

    for benchmark_id, expected_circuit_id in BENCHMARK_CASES:
        metrics = evaluator.evaluate(_load_metric_inputs(benchmark_id))

        assert expected_circuit_id in metrics
        _assert_metrics_match(
            metrics[expected_circuit_id], EXPECTED_METRICS[expected_circuit_id]
        )
