# PlasmaSpice: Python Circuit Simulation Program

A Python-based circuit simulation program that implements Modified Nodal Analysis (MNA) for solving electronic circuits.

## Overview

PlasmaSpice is a circuit simulation tool that uses Modified Nodal Analysis (MNA) to solve both linear and nonlinear circuits. It supports various circuit elements and can handle both DC and transient analysis.

## Features

- Modified Nodal Analysis (MNA) implementation with complete matrix formulation:
  - G matrix: conductance matrix for passive elements
  - B matrix: voltage source connections
  - C matrix: current variables
  - D matrix: for dependent sources
- Support for basic circuit elements (R, L, C, V, I)
- DC and transient analysis
- Nonlinear device support
- Unit testing framework

## Circuit Analysis Implementation

### 1. Modified Nodal Analysis (MNA)

The program uses MNA to analyze circuits by constructing a system of equations in the form:

```
[G B] [v] = [i]
[C D] [j]   [e]
```

where:

- G (n×n) contains conductances from passive elements
- B (n×m) contains voltage source connections
- C (m×n) is typically B^T for independent sources
- D (m×m) is zero for independent sources
- v is the vector of node voltages
- j is the vector of voltage source currents
- i is the vector of known currents
- e is the vector of voltage source values

### 2. Data Structures and Circuit Elements

#### Circuit Elements

Each circuit element is represented by a Python class with properties:

```python
class Component:
    def __init__(self, name, entrance, exit):
        self.name = name      # Element identifier
        self.entrance = entrance    # Positive terminal node
        self.exit = exit    # Negative terminal node
```

Specific element types inherit from the base class:

- Resistor (R)
- Capacitor (C)
- Inductor (L)
- Voltage Source (V)
- Current Source (I)

### 3. Solving Circuit Equations

#### DC Analysis

- Uses numpy.linalg for solving linear systems
- Implements Newton-Raphson method for nonlinear circuits

#### Transient Analysis

For time-dependent circuits, the program:

1. Converts circuit equations to DAE (Differential Algebraic Equations) form
2. Uses numerical integration methods:
   - Backward Euler
   - Trapezoidal Rule
   - Gear Method

### 4. Unit Testing

The project uses Python's unittest framework for testing. Test modules are organized as follows:

```
tests/
├── test_elements.py      # Test circuit element classes
├── test_mna.py          # Test MNA matrix construction
├── test_dc_analysis.py  # Test DC solutions
└── test_transient.py    # Test transient analysis
```

Example test case:

```python
def test_voltage_divider():
    """Test a simple voltage divider circuit"""
    ckt = Circuit()

    # Add components
    ckt.add_element(VoltageSource("V1", 1, 0, 5.0))  # 5V source
    ckt.add_element(Resistor("R1", 1, 2, 1000))      # 1kΩ
    ckt.add_element(Resistor("R2", 2, 0, 1000))      # 1kΩ

    # Solve and verify
    result = ckt.solve_dc()
    assert abs(result["V2"] - 2.5) < 1e-10  # Node 2 should be at 2.5V
```

## Installation

```bash
pip install -r requirements.txt
```

## Dependencies

- numpy: For matrix operations
- scipy: For numerical integration and sparse matrix handling
- matplotlib: For plotting results
- pytest: For unit testing

## Usage Example

```python
from plasmaSpice.core import Circuit, Resistor, VoltageSource

# Create circuit
ckt = Circuit()

# Add elements
ckt.add_element(VoltageSource("V1", 1, 0, 5))  # 5V source
ckt.add_element(Resistor("R1", 1, 2, 1000))    # 1kΩ resistor
ckt.add_element(Resistor("R2", 2, 0, 2000))    # 2kΩ resistor

# Solve
result = ckt.solve_dc()
print(f"Node voltages: {result}")
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
