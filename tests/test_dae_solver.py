import unittest
import numpy as np
import matplotlib.pyplot as plt
import os
from plasmaSpice.core.dae_solver import DAESolver

class TestDAESolver(unittest.TestCase):
    def setUp(self):
        self.output_dir = 'test_outputs'
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
    # def test_series_lc_branch_circuit(self):
    #     """Test circuit with series LC branch using IDA solver"""
    #     # Circuit parameters
    #     V = 10.0     # Source voltage (V)
    #     R1 = 100     # Resistance 1 (Ω)
    #     R2 = 1000    # Resistance 2 (Ω)
    #     R3 = 500     # Resistance 3 (Ω)
    #     L1 = 0.1     # Inductance (H)
    #     C1 = 1e-6    # Capacitance (F)
        
    #     def residual(t, y, yd):
    #         """DAE system in residual form: 0 = F(t, y, y')"""
    #         v2, v3, v4, iL1 = y
    #         dv2, dv3, dv4, diL1 = yd
            
    #         res = np.zeros(4)
    #         res[0] = (V-v2)/R1 - v2/R2 - iL1    # KCL at v2
    #         res[1] = L1*diL1 - (v2 - v3)        # Inductor equation
    #         res[2] = iL1 - C1*(dv3 - dv4)       # Capacitor equation
    #         res[3] = iL1 - v4/R3                 # KCL at v4
    #         return res
        
    #     # Initial conditions
    #     v2_0 = V * R2/(R1 + R2)  # 电压分压
    #     y0 = np.array([v2_0, 0.0, 0.0, 0.0])    # [v2, v3, v4, iL1]
    #     yd0 = np.zeros_like(y0)                  # 初始导数全为0
        
    #     # Solve
    #     solver = DAESolver()
    #     solution = solver.solve(residual, (0, 10e-3), y0, yd0)
        
    #     # Save solution data
    #     data_file = os.path.join(self.output_dir, 'solution_data.txt')
    #     with open(data_file, 'w') as f:
    #         f.write('# Time(s) v2(V) v3(V) v4(V) iL1(A)\n')
    #         for i in range(len(solution.t)):
    #             f.write(f'{solution.t[i]:.6e} ')
    #             for j in range(4):
    #                 f.write(f'{solution.y[j,i]:.6e} ')
    #             f.write('\n')
                
    #     # Load and plot data
    #     data = np.loadtxt(os.path.join(self.output_dir, 'solution_data.txt'), skiprows=1)
    #     t = data[:,0]
    #     v2 = data[:,1]
    #     v3 = data[:,2]
    #     v4 = data[:,3]
    #     iL1 = data[:,4]
        
    #     plt.figure(figsize=(10, 8))
        
    #     # Voltage plots
    #     plt.subplot(211)
    #     t_ms = t * 1000  # 转换为毫秒
    #     plt.plot(t_ms, [V]*len(t), 'k--', label='v1 (source)')
    #     plt.plot(t_ms, v2, 'r-', label='v2 (R2)')
    #     plt.plot(t_ms, v3, 'g-', label='v3 (L1-C1)')
    #     plt.plot(t_ms, v4, 'm-', label='v4 (C1-R3)')
    #     plt.grid(True)
    #     plt.xlabel('Time (ms)')
    #     plt.ylabel('Voltage (V)')
    #     plt.title('Node Voltages')
    #     plt.legend()
        
    #     # Current plot
    #     plt.subplot(212)
    #     plt.plot(t_ms, iL1*1000, 'b-', label='iL1 (LC branch)')
    #     plt.grid(True)
    #     plt.xlabel('Time (ms)')
    #     plt.ylabel('Current (mA)')
    #     plt.title('LC Branch Current')
    #     plt.legend()
        
    #     plt.tight_layout()
    #     plt.savefig(os.path.join(self.output_dir, 'series_lc_response.png'))
    #     plt.close()

    def test_example_lc_branch_circuit(self):
        """Test circuit with example RLC branch in our paper"""
        # Circuit parameters
        V = 500.0     # Source voltage (V)
        R1 = 50       # Resistance 1 (Ω)
        Cm1 = 1.5e-10   # Capacitance 1 (F)
        Cm2 = 2e-10   # Capacitance 2 (F)
        Lm = 4.3e-6   # Inductance (H)
        Rm = 0.5      # Resistance (Ω)
        Cs = 2e-10    # Capacitance (F)
        Rs = 0.5      # Resistance (Ω)
        
        def residual(t, y, yd):
            """DAE system in residual form: 0 = F(t, y, y')"""
            v1, v2, v3, v4, v5, v6, iV1, iL1 = y
            dv1, dv2, dv3, dv4, dv5, dv6, diV1, diL1 = yd
            
            res = np.zeros(8)
            # Node 1: Current of R1 - Voltage source current
            res[0] = (v1-v2)/R1 - iV1
            
            # Node 2: KCL at Cm1-Cm2 junction
            res[1] = Cm1*dv2 + Cm2*(dv2 - dv3) + (v2 - v1)/R1
            
            # Node 3: KCL at Cm2-L junction
            res[2] = Cm2*(dv3 - dv2) + iL1
            
            # Node 4: KCL at L-Rm junction
            res[3] = (v4 - v5)/Rm - iL1
            
            # Node 5: KCL at Rm-Cs junction
            res[4] = Cs*(dv5 - dv6) + (v5 - v4)/Rm
            
            # Node 6: KCL at Cs-Rs junction
            res[5] = Cs*(dv6 - dv5) + v6/Rs
            
            # Inductor equation
            res[6] = (v3 -v4) - Lm*diL1
            
            # Voltage source equation
            res[7] = v1 - V
            
            return res
        
        # Initial conditions - 更合理的初始值
        y0 = np.array([V, 0, 0, 0, 0, 0, 0, 0])  # 电压源和第一个节点从V开始
        yd0 = np.zeros_like(y0)                   # 初始导数全为0
        
        # Solve
        solver = DAESolver()
        solution = solver.solve(residual, (0, 1e-6), y0, yd0)
        
        # Save solution data
        data_file = os.path.join(self.output_dir, 'solution_data_example.txt')
        with open(data_file, 'w') as f:
            f.write('# Time(s) v1(V) v2(V) v3(V) v4(V) v5(V) v6(V) iV1(A) iL1(A)\n')
            for i in range(len(solution.t)):
                f.write(f'{solution.t[i]:.6e} ')
                for j in range(8):
                    f.write(f'{solution.y[j,i]:.6e} ')
                f.write('\n')
                
        # Load and plot data
        data = np.loadtxt(os.path.join(self.output_dir, 'solution_data_example.txt'))
        t = data[:,0]
        v1 = data[:,1]
        v2 = data[:,2]
        v3 = data[:,3]
        v4 = data[:,4]
        v5 = data[:,5]
        v6 = data[:,6]
        iV1 = data[:,7]
        iL1 = data[:,8]
        
        plt.figure(figsize=(12, 8))
        
        # Voltage plots
        plt.subplot(211)
        t_us = t * 1e6  # 转换为微秒
        plt.plot(t_us, v1, 'k-', label='v1 (source)')
        plt.plot(t_us, v2, 'r-', label='v2')
        plt.plot(t_us, v3, 'g-', label='v3')
        plt.plot(t_us, v4, 'b-', label='v4')
        plt.plot(t_us, v5, 'm-', label='v5')
        plt.plot(t_us, v6, 'c-', label='v6')
        plt.grid(True)
        plt.xlabel('Time (μs)')
        plt.ylabel('Voltage (V)')
        plt.title('Node Voltages')
        plt.legend()
        
        # Current plot
        plt.subplot(212)
        plt.plot(t_us, iV1, 'r-', label='iV1 (source)')
        plt.plot(t_us, iL1, 'b-', label='iL1 (inductor)')
        plt.grid(True)
        plt.xlabel('Time (μs)')
        plt.ylabel('Current (A)')
        plt.title('Branch Currents')
        plt.legend()
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'example_lc_response.png'))
        plt.close()

if __name__ == '__main__':
    unittest.main() 