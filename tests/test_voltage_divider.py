"""
Test module for voltage divider circuit analysis.

This test verifies:
1. Basic circuit construction
2. MNA matrix formation
3. DC solution accuracy
4. Current calculations
"""

import sys
import os
import numpy as np
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plasmaSpice.core.circuit import Circuit
from plasmaSpice.core.elements import Resistor, VoltageSource

def test_voltage_divider():
    """
    Test a simple voltage divider circuit:
    
    V1 (5V)
    |
    R1 (1kΩ)
    |
    Node 2 (should be 2.5V)
    |
    R2 (1kΩ)
    |
    GND
    
    Expected results:
    - V1 = 5V (node 1)
    - V2 = 2.5V (node 2)
    - I = 2.5mA (through both resistors)
    """
    print("\n=== Testing Voltage Divider Circuit ===")
    
    # Create circuit
    print("\n1. Creating circuit...")
    ckt = Circuit()
    
    # Add components
    print("\n2. Adding circuit elements:")
    
    v1 = VoltageSource("V1", 1, 0, 5.0)
    ckt.add_element(v1)
    print("- Added voltage source V1: 5V between nodes 1 and 0 (ground)")
    
    r1 = Resistor("R1", 1, 2, 1000)
    ckt.add_element(r1)
    print("- Added resistor R1: 1kΩ between nodes 1 and 2")
    
    r2 = Resistor("R2", 2, 0, 1000)
    ckt.add_element(r2)
    print("- Added resistor R2: 1kΩ between node 2 and ground")
    
    # Verify circuit construction
    print("\n3. Verifying circuit construction:")
    assert len(ckt.nodes) == 2, f"Expected 2 nodes, got {len(ckt.nodes)}"
    assert len(ckt.voltage_sources) == 1, f"Expected 1 voltage source, got {len(ckt.voltage_sources)}"
    print("- Circuit construction verified")
    
    # Solve the circuit
    print("\n4. Solving circuit...")
    result = ckt.solve_dc(debug=True)
    
    # Verify results
    print("\n5. Verifying results:")
    
    # Node voltages
    v_node1 = result["V1"]
    v_node2 = result["V2"]
    i_source = result["I_V1"]
    
    print(f"Node voltages:")
    print(f"- V1: {v_node1:.6f}V (expected: 5.000000V)")
    print(f"- V2: {v_node2:.6f}V (expected: 2.500000V)")
    print(f"Source current:")
    print(f"- I_V1: {i_source*1000:.6f}mA (expected: 2.500000mA)")
    
    # Voltage tests
    assert abs(v_node1 - 5.0) < 1e-10, f"Node 1 voltage error: {abs(v_node1 - 5.0)}V"
    assert abs(v_node2 - 2.5) < 1e-10, f"Node 2 voltage error: {abs(v_node2 - 2.5)}V"
    print("- Node voltages verified")
    
    # Current test
    assert abs(i_source - 0.0025) < 1e-10, f"Source current error: {abs(i_source - 0.0025)}A"
    print("- Source current verified")
    
    # Verify Kirchhoff's Voltage Law (KVL)
    v_r1 = v_node1 - v_node2  # Voltage across R1
    v_r2 = v_node2 - 0        # Voltage across R2
    assert abs(v_r1 + v_r2 - 5.0) < 1e-10, "KVL error"
    print("- Kirchhoff's Voltage Law verified")
    
    # Verify Kirchhoff's Current Law (KCL)
    i_r1 = v_r1 / 1000  # Current through R1
    i_r2 = v_r2 / 1000  # Current through R2
    assert abs(i_r1 - i_r2) < 1e-10, "KCL error"
    assert abs(i_r1 - i_source) < 1e-10, "Current continuity error"
    print("- Kirchhoff's Current Law verified")
    
    print("\nTest passed! Voltage divider circuit working correctly.")

if __name__ == "__main__":
    test_voltage_divider() 