import sys
import os
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
    """
    print("Creating voltage divider test circuit...")
    
    # Create circuit
    ckt = Circuit()
    
    # Add components
    print("\nAdding circuit elements:")
    ckt.add_element(VoltageSource("V1", 1, 0, 5.0))  # 5V source between node 1 and ground
    print("- Added voltage source V1: 5V between nodes 1 and 0 (ground)")
    
    ckt.add_element(Resistor("R1", 1, 2, 1000))      # 1kΩ between nodes 1 and 2
    print("- Added resistor R1: 1kΩ between nodes 1 and 2")
    
    ckt.add_element(Resistor("R2", 2, 0, 1000))      # 1kΩ between node 2 and ground
    print("- Added resistor R2: 1kΩ between node 2 and ground")
    
    # Solve the circuit
    print("\nSolving circuit...")
    voltages = ckt.solve_dc(debug=True)
    
    # Check results
    print("\nVerifying results:")
    print(f"Node 1 voltage: {voltages[1]:.3f}V (expected: 5.000V)")
    print(f"Node 2 voltage: {voltages[2]:.3f}V (expected: 2.500V)")
    
    assert abs(voltages[1] - 5.0) < 1e-10, f"Node 1 voltage should be 5V, got {voltages[1]}V"
    assert abs(voltages[2] - 2.5) < 1e-10, f"Node 2 voltage should be 2.5V, got {voltages[2]}V"
    
    print("\nTest passed! Voltage divider circuit working correctly.")

if __name__ == "__main__":
    test_voltage_divider() 