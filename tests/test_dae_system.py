import unittest
import numpy as np
import matplotlib.pyplot as plt
from plasmaSpice.core.circuit import Circuit
from plasmaSpice.core.elements import VoltageSource, Resistor, Capacitor, Inductor

class TestDAESystem(unittest.TestCase):
    def setUp(self):
        self.output_dir = 'test_outputs'
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
    def test_example_lc_branch_circuit(self):
        """Test complex RLC circuit with automatic DAE system construction"""
        # Create circuit
        ckt = Circuit()
        
        # Circuit parameters
        V = 500.0     # Source voltage (V)
        R1 = 50       # Resistance 1 (Ω)
        Cm1 = 1.5e-10 # Capacitance 1 (F)
        Cm2 = 2e-10   # Capacitance 2 (F)
        Lm = 4.3e-6   # Inductance (H)
        Rm = 0.5      # Resistance (Ω)
        Cs = 2e-10    # Capacitance (F)
        Rs = 0.5      # Resistance (Ω)
        
        # Add circuit elements
        ckt.add_element(VoltageSource("V1", 1, 0, V))
        ckt.add_element(Resistor("R1", 1, 2, R1))
        ckt.add_element(Capacitor("Cm1", 2, 0, Cm1))
        ckt.add_element(Capacitor("Cm2", 2, 3, Cm2))
        ckt.add_element(Inductor("Lm", 3, 4, Lm))
        ckt.add_element(Resistor("Rm", 4, 5, Rm))
        ckt.add_element(Capacitor("Cs", 5, 6, Cs))
        ckt.add_element(Resistor("Rs", 6, 0, Rs))
        
        # Solve transient analysis
        solution = ckt.solve_dae((0, 1e-6), debug=True)
        
        # Save and plot results
        data_file = os.path.join(self.output_dir, 'auto_dae_solution.txt')
        with open(data_file, 'w') as f:
            f.write('# Time(s) v1(V) v2(V) v3(V) v4(V) v5(V) v6(V) iV1(A) iL1(A)\n')
            for i in range(len(solution.t)):
                f.write(f'{solution.t[i]:.6e} ')
                for j in range(8):
                    f.write(f'{solution.y[j,i]:.6e} ')
                f.write('\n')
        
        # Plot results
        plt.figure(figsize=(12, 8))
        
        # Voltage plots
        plt.subplot(211)
        t_us = solution.t * 1e6  # 转换为微秒
        plt.plot(t_us, solution.y[0,:], 'k-', label='v1 (source)')
        plt.plot(t_us, solution.y[1,:], 'r-', label='v2')
        plt.plot(t_us, solution.y[2,:], 'g-', label='v3')
        plt.plot(t_us, solution.y[3,:], 'b-', label='v4')
        plt.plot(t_us, solution.y[4,:], 'm-', label='v5')
        plt.plot(t_us, solution.y[5,:], 'c-', label='v6')
        plt.grid(True)
        plt.xlabel('Time (μs)')
        plt.ylabel('Voltage (V)')
        plt.title('Node Voltages')
        plt.legend()
        
        # Current plot
        plt.subplot(212)
        plt.plot(t_us, solution.y[6,:], 'r-', label='iV1 (source)')
        plt.plot(t_us, solution.y[7,:], 'b-', label='iL1 (inductor)')
        plt.grid(True)
        plt.xlabel('Time (μs)')
        plt.ylabel('Current (A)')
        plt.title('Branch Currents')
        plt.legend()
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'auto_dae_response.png'))
        plt.close()
        
        # Build DAE system
        A, B, C, y0, yd0, algvar_list = ckt.build_dae_system()
        
        print("\nAutomatic DAE System:")
        print("A matrix:")
        print(A)
        print("\nB matrix:")
        print(B)
        print("\nC vector:")
        print(C)
        
        # Test same point as manual system
        y_test = np.array([V, 0, 0, 0, 0, 0, 0, 0])
        yd_test = np.zeros_like(y_test)
        res_test = A @ yd_test - B @ y_test - C
        
        print("\nTest point y:", y_test)
        print("Test point yd:", yd_test)
        print("Residual:", res_test)

if __name__ == '__main__':
    unittest.main() 