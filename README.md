# PySPICE: Python Circuit Simulation Program

A Python-based circuit simulation program that implements Modified Nodal Analysis (MNA) for solving electronic circuits.

## Overview

PySPICE is a circuit simulation tool that uses Modified Nodal Analysis (MNA) to solve both linear and nonlinear circuits. It supports various circuit elements and can handle both DC and transient analysis.

## Features

- Modified Nodal Analysis (MNA) implementation
- Support for basic circuit elements (R, L, C, V, I)
- DC and transient analysis
- Nonlinear device support
- Unit testing framework

## Circuit Analysis Implementation

### 1. Modified Nodal Analysis (MNA)

The program uses MNA to analyze circuits by:

- Selecting a reference (ground) node
- Applying KCL at each node
- Adding voltage source equations
- Handling current variables for inductors and voltage sources

### 2. Data Structures and Circuit Elements

#### Circuit Elements

Each circuit element is represented by a Python class with properties:

```python
class CircuitElement:
    def __init__(self, name, node1, node2, value):
        self.name = name      # Element identifier
        self.node1 = node1    # Positive terminal node
        self.node2 = node2    # Negative terminal node
        self.value = value    # Element value (R, L, C, etc.)
```

Specific element types inherit from the base class:

- Resistor (R)
- Capacitor (C)
- Inductor (L)
- Voltage Source (V)
- Current Source (I)

#### Circuit Matrix Construction

The MNA matrix equation has the form:

```
[A][x] = [b]
```

where:

- [A] is the conductance matrix
- [x] is the vector of unknown node voltages and branch currents
- [b] is the vector of known current and voltage sources

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

```python
# Example DAE solver interface
def solve_dae(circuit, t_start, t_end, step_size):
    """
    Solve circuit DAE system using numerical integration

    Args:
        circuit: Circuit object containing elements and topology
        t_start: Start time
        t_end: End time
        step_size: Integration step size

    Returns:
        t: Time points
        y: Solution vectors (node voltages and branch currents)
    """
```

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
import unittest

class TestResistor(unittest.TestCase):
    def test_resistor_stamp(self):
        """Test resistor contribution to MNA matrix"""
        R = Resistor("R1", 1, 0, 1000)  # 1kΩ resistor
        matrix = np.zeros((2, 2))
        R.stamp(matrix)
        self.assertEqual(matrix[0,0], 1e-3)  # Check conductance value
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
from pyspice import Circuit, Resistor, VoltageSource

# Create circuit
ckt = Circuit()

# Add elements
ckt.add(VoltageSource('V1', 1, 0, 5))  # 5V source
ckt.add(Resistor('R1', 1, 2, 1000))    # 1kΩ resistor
ckt.add(Resistor('R2', 2, 0, 2000))    # 2kΩ resistor

# Solve
solution = ckt.solve()
print(f"Node voltages: {solution.voltages}")
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
