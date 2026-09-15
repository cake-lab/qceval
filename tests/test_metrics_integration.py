from __future__ import annotations

from qceval.loader import CircuitLoader
from qceval.metrics import CircuitMetricsEvaluator


def test_metrics_for_real_benchmarks():
    loader = CircuitLoader()
    evaluator = CircuitMetricsEvaluator()

    benchmark_ids = [
        # "disqco.mfpqc.qv.n96",
        "disqco.mfpqc.qft.n16",
        # "disqco.mfpqc.qaoa.n96",
        # "disqco.mfpqc.cp_scaling.n96",
        # "disqco.mfpqc.cp_large.n128",
        "qasmbench.small.bell_n4",
        # "qasmbench.small.adder_n4",
    ]

    # Collect circuits from multiple benchmarks
    all_circuits = []
    for benchmark_id in benchmark_ids:
        loaded_circuits = loader.load(benchmark_id)
        circuit_id, circuit = next(loaded_circuits)
        all_circuits.append((circuit_id, circuit))

    # Pass directly to evaluate (using new API)
    metrics = evaluator.evaluate(all_circuits)

    # Verify results
    assert len(metrics) == len(all_circuits)

    assert metrics["disqco.mfpqc.qft.n16.qft_n16"]["qubit_count"] == 16
    assert metrics["disqco.mfpqc.qft.n16.qft_n16"]["gate_count"] > 0
    assert 0.0 < metrics["disqco.mfpqc.qft.n16.qft_n16"]["liveness_supermarq"] <= 1.0

    assert metrics["qasmbench.small.bell_n4.bell_n4"]["qubit_count"] == 4
    assert metrics["qasmbench.small.bell_n4.bell_n4"]["measurement_count"] == 4
    assert metrics["qasmbench.small.bell_n4.bell_n4"]["gate_count"] > 0

    for circuit_id, _ in all_circuits:
        assert metrics[circuit_id]["qubit_count"] > 0
        assert metrics[circuit_id]["gate_count"] >= 0
