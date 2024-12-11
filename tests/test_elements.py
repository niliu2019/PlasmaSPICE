import unittest
from plasmaSpice.core.circuit import Circuit
from plasmaSpice.core.elements import Capacitor, VoltageSource, Resistor, Inductor

def main():
    unittest.main()

class TestCapacitor(unittest.TestCase):
    def test_dc_open_circuit(self):
        """Test that capacitor acts as open circuit in DC"""
        ckt = Circuit()
        
        # Create a circuit with a voltage source, resistor and capacitor
        ckt.add_element(VoltageSource("V1", 1, 0, 5.0))
        ckt.add_element(Resistor("R1", 1, 2, 1000))  # 1kΩ resistor to prevent floating node
        ckt.add_element(Capacitor("C1", 2, 0, 1e-6))  # 1µF
        
        # Solve DC
        result = ckt.solve_dc()
        
        # In DC, capacitor is open circuit, so:
        # - No current flows through the capacitor
        # - Node 2 voltage should be same as node 1 (5V)
        self.assertAlmostEqual(result["V1"], 5.0)
        self.assertAlmostEqual(result["V2"], 5.0)
    
    def test_capacitor_voltage_divider(self):
        """Test capacitor in a voltage divider configuration"""
        ckt = Circuit()
        
        # Create a voltage divider with resistor and capacitor
        ckt.add_element(VoltageSource("V1", 1, 0, 10.0))
        ckt.add_element(Resistor("R1", 1, 2, 1000))  # 1kΩ
        cap = Capacitor("C1", 2, 0, 1e-6)  # 1µF
        ckt.add_element(cap)
        
        # Solve DC
        result = ckt.solve_dc()
        
        # In DC:
        # - Capacitor is open circuit
        # - All voltage drops across capacitor
        # - Node 2 should be at 10V
        self.assertAlmostEqual(result["V2"], 10.0)
        
        # Check capacitor voltage calculation method
        voltage = cap.get_voltage(result)
        self.assertAlmostEqual(voltage, 10.0)

class TestInductor(unittest.TestCase):
    def test_dc_short_circuit(self):
        """Test that inductor acts as short circuit in DC"""
        ckt = Circuit()
        
        # Create a circuit with voltage source and inductor in series
        ckt.add_element(VoltageSource("V1", 1, 0, 5.0))
        ckt.add_element(Inductor("L1", 1, 2, 1e-3))  # 1mH
        
        # Solve DC
        result = ckt.solve_dc()
        
        # In DC, inductor is short circuit, so:
        # - No voltage drop across inductor
        # - Node 2 voltage should be same as node 1
        self.assertAlmostEqual(result["V1"], 5.0)
        self.assertAlmostEqual(result["V2"], 5.0)
    
    def test_inductor_voltage_divider(self):
        """Test inductor in a voltage divider configuration"""
        ckt = Circuit()
        
        # Create a voltage divider with resistor and inductor
        ckt.add_element(VoltageSource("V1", 1, 0, 10.0))
        ckt.add_element(Resistor("R1", 1, 2, 1000))  # 1kΩ
        ind = Inductor("L1", 2, 0, 1e-3)  # 1mH
        ckt.add_element(ind)
        
        # Solve DC
        result = ckt.solve_dc()
        
        # In DC:
        # - Inductor is short circuit
        # - All voltage drops across resistor
        # - Node 2 should be at 0V
        self.assertAlmostEqual(result["V2"], 0.0)

if __name__ == '__main__':
    main()