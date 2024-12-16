from assimulo.problem import Implicit_Problem
from assimulo.solvers import IDA
import numpy as np

class DAESolver:
    """DAE solver using Assimulo's IDA interface"""
    
    def __init__(self, solver_options=None):
        """
        Initialize DAE solver with options.
        
        Args:
            solver_options (dict): Solver configuration options
                - atol: Absolute tolerance (default: 1e-6)
                - rtol: Relative tolerance (default: 1e-6)
                - maxsteps: Maximum number of steps (default: 10000)
                - inith: Initial step size (default: 1e-14)
                - verbosity: Output level (default: 50)
                - suppress_alg: Suppress algebraic variable warnings (default: True)
                - ncp: Number of communication points (default: 10000)
        """
        self.options = {
            'atol': 1e-6,
            'rtol': 1e-3,
            'maxsteps': 10000,
            'inith': 1e-14,
            'verbosity': 50,
            'suppress_alg': True,
            'ncp': 10000
        }
        
        # Update with user provided options
        if solver_options is not None:
            self.options.update(solver_options)
    
    def configure(self, **kwargs):
        """
        Update solver options.
        
        Args:
            **kwargs: Solver options to update
        """
        self.options.update(kwargs)
    
    def solve(self, residual_fn, t_span, y0, yd0, t_eval=None):
        """
        Solve DAE system: F(t, y, y') = 0
        
        Args:
            residual_fn: Function that evaluates the residual
            t_span: Tuple (t0, tf) for time range
            y0: Initial state vector
            yd0: Initial state derivative vector
            t_eval: Optional time points for output
            
        Returns:
            Solution object containing results
        """
        # Create problem
        problem = Implicit_Problem(residual_fn, y0, yd0, t0=t_span[0])
        
        # Create solver
        solver = IDA(problem)
        
        # Configure solver with current options
        for key, value in self.options.items():
            if hasattr(solver, key):
                setattr(solver, key, value)
        
        # Set algebraic variables
        if 'algvar' in self.options:
            solver.algvar = self.options['algvar']
            print("Setting algvar:", self.options['algvar'])
        
        # Solve system
        if t_eval is not None:
            solution = solver.simulate(t_span[1], ncp_list=t_eval)
        else:
            solution = solver.simulate(t_span[1], ncp=self.options['ncp'])
        
        return Solution(solution[0], solution[1].T)

class Solution:
    """Solution returned by DAE solver"""
    def __init__(self, t, y):
        self.t = np.array(t)
        self.y = np.array(y)
        self.success = True
        self.message = "Integration successful."