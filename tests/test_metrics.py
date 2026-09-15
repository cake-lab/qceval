import pytest
from qiskit import QuantumCircuit

from qceval.metrics import CircuitMetricsEvaluator


def test_metric_evaluator_rejects_invalid_inputs():
    evaluator = CircuitMetricsEvaluator()
    with pytest.raises(TypeError):
        evaluator.evaluate("OPENQASM 2.0;")


def test_metric_evaluator_evaluates_named_circuits_from_list():
    evaluator = CircuitMetricsEvaluator()
    circuit = QuantumCircuit(2, 1)
    circuit.h(0)
    circuit.cx(0, 1)
    circuit.measure(0, 0)

    metrics = evaluator.evaluate([("example", circuit)])
    all_metrics = evaluator.evaluate([("example", circuit)], [])

    assert metrics["example"]["qubit_count"] == 2
    assert metrics["example"]["dual_gate_count"] == 1
    assert metrics["example"]["gate_count"] >= 2
    assert "gate_count" in all_metrics["example"]
    assert "measurement_supermarq" in all_metrics["example"]


def test_metric_evaluator_evaluates_named_circuits_from_generator():
    evaluator = CircuitMetricsEvaluator()
    circuit = QuantumCircuit(2, 1)
    circuit.h(0)
    circuit.cx(0, 1)
    circuit.measure(0, 0)

    def circuit_generator():
        yield ("example", circuit)

    metrics = evaluator.evaluate(circuit_generator())
    assert metrics["example"]["qubit_count"] == 2
    assert metrics["example"]["dual_gate_count"] == 1


def test_metric_evaluator_filters_metrics_by_name():
    evaluator = CircuitMetricsEvaluator()
    circuit = QuantumCircuit(1)
    circuit.x(0)

    metrics = evaluator.evaluate(
        [("example", circuit)],
        ["qubit_count", "gate_count"],
    )

    assert metrics == {"example": {"qubit_count": 1, "gate_count": 1}}


def test_metric_evaluator_supports_custom_metrics():
    evaluator = CircuitMetricsEvaluator()

    evaluator.register_metric(
        "double_qubits",
        lambda analysis: analysis.qubit_count * 2,
        "Example custom metric",
    )

    circuit = QuantumCircuit(3)
    metrics = evaluator.evaluate(
        [("example", circuit)],
        ["double_qubits"],
    )

    assert metrics == {"example": {"double_qubits": 6}}
