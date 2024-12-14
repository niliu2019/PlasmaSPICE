from assimulo.problem import Implicit_Problem
from assimulo.solvers import IDA
import numpy as np

class DAESolver:
    """DAE solver using Assimulo's IDA interface"""
    def solve(self, residual_fn, t_span, y0, yd0, t_eval=None):
        """Solve DAE system: F(t, y, y') = 0"""
        # Create problem
        problem = Implicit_Problem(residual_fn, y0, yd0, t0=t_span[0])
        
        # Create solver
        solver = IDA(problem)
        
        # 基本求解器设置
        solver.atol = 1e-6          # 绝对容差
        solver.rtol = 1e-3          # 相对容差
        solver.maxsteps = 500000    # 最大步数
        solver.verbosity = 50       # 输出信息
        solver.suppress_alg = True  # 抑制代数变量警告
        solver.algvar = [0, 1, 1, 1, 1, 1, 0, 1]  # v1,v2,v3,v4,v5,v6,iV1,iL1
        solver.inith = 1e-14        # 初始步长
        
        # 使用更多的输出点以获得更好的分辨率
        solution = solver.simulate(t_span[1], ncp=10000)
        t = solution[0]
        y = solution[1]
        
        return Solution(t, y.T)

class Solution:
    """Solution returned by solve_ivp"""
    def __init__(self, t, y):
        self.t = t
        self.y = y
        self.success = True
        self.message = "Integration successful." 