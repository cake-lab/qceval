import pytest
from qiskit import QuantumCircuit

from qceval.loader import CircuitLoader


def test_load_single_qasmbench_circuit():
    loader = CircuitLoader()
    circuits = list(loader.load("qasmbench.small.adder_n4"))

    assert isinstance(circuits, list)
    assert len(circuits) == 1
    assert all(isinstance(circuit, QuantumCircuit) for _, circuit in circuits)
    expected_key = "qasmbench.small.adder_n4.adder_n4"
    keys = [k for k, _ in circuits]
    assert expected_key in keys


def test_load_single_disqco_qaoa_n16_1():
    loader = CircuitLoader()
    circuits = list(loader.load("disqco.mfpqc.qaoa.n16.1"))

    assert isinstance(circuits, list)
    assert len(circuits) == 1
    assert all(isinstance(circuit, QuantumCircuit) for _, circuit in circuits)
    expected_key = "disqco.mfpqc.qaoa.n16.qaoa_n16_prob0p5_1"
    keys = [k for k, _ in circuits]
    assert expected_key in keys


def test_load_single_disqco_qaoa_n16_1_transpiled():
    loader = CircuitLoader()
    circuits = list(loader.load("disqco.mfpqc.qaoa.n16.1", transpiled=True))

    assert isinstance(circuits, list)
    assert len(circuits) == 1
    assert all(isinstance(circuit, QuantumCircuit) for _, circuit in circuits)
    expected_key = "disqco.mfpqc.qaoa.n16.qaoa_n16_prob0p5_1.transpiled"
    keys = [k for k, _ in circuits]
    assert expected_key in keys


def test_load_batch_disqco_qaoa_n16():
    loader = CircuitLoader()
    circuits = list(loader.load("disqco.mfpqc.qaoa.n16"))

    assert isinstance(circuits, list)
    assert len(circuits) == 10
    assert all(isinstance(circuit, QuantumCircuit) for _, circuit in circuits)
    # check that keys follow the expected dotted pattern and include numbered instances
    sample_keys = sorted(
        k for k, _ in circuits if k.startswith("disqco.mfpqc.qaoa.n16.")
    )
    assert len(sample_keys) == 10
    assert any(sample_keys[0].endswith("_1") for _ in [0])


def test_load_batch_disqco_qaoa_n16_transpiled():
    loader = CircuitLoader()
    circuits = list(loader.load("disqco.mfpqc.qaoa.n16", transpiled=True))

    assert isinstance(circuits, list)
    assert len(circuits) == 10
    assert all(isinstance(circuit, QuantumCircuit) for _, circuit in circuits)
    sample_keys = sorted(
        k for k, _ in circuits if k.startswith("disqco.mfpqc.qaoa.n16.")
    )
    assert len(sample_keys) == 10
    assert any("transpiled" in k for k in sample_keys)


def test_missing_numeric_circuit_raises_file_not_found():
    loader = CircuitLoader()

    with pytest.raises(FileNotFoundError):
        next(loader.load("disqco.mfpqc.qaoa.n16.999"))


def test_missing_path_raises_file_not_found():
    loader = CircuitLoader()

    with pytest.raises(FileNotFoundError):
        next(loader.load("disqco.mfpqc.qaoa.q999"))
