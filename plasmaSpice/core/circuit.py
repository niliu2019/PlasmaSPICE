"""
Circuit class for Modified Nodal Analysis (MNA) and DAE system analysis.
"""

import numpy as np
from collections import defaultdict
from .elements import Inductor, Capacitor, VoltageSource

class Circuit:
    """Circuit class for both DC and transient analysis."""
    
    def __init__(self):
        """Initialize an empty circuit."""
        self.elements = []          # All circuit elements
        self.nodes = set()          # Set of all nodes (excluding ground)
        self.voltage_sources = []   # List of voltage sources
        self.node_map = {}          # Maps node numbers to matrix indices
        self.vsrc_map = {}          # Maps voltage sources to matrix indices
        self._algvar_list = []      # Store algebraic and differential variable list
    
    def _update_algvar_list(self):
        """
        Update the list of algebraic and differential variable identifiers, 
        corresponding to the state vector order.
        State vector order: [v1,...,vn, iV1,...,iVm, iL1,...,iLk]
        1 = Differential variable (capacitor node voltages, inductor currents)
        0 = Algebraic variable (other node voltages, voltage source currents)
        """
        # Get system size
        n_nodes, n_currents = self._build_maps()
        self._algvar_list = [0] * (n_nodes + n_currents)  # Initialize all variables as algebraic
        
        # Process node voltages - only nodes connected to capacitors are differential
        for element in self.elements:
            if isinstance(element, Capacitor):  # Only consider capacitors
                if element.entrance != 0:
                    idx = self.node_map[element.entrance]
                    self._algvar_list[idx] = 1
                if element.exit != 0:
                    idx = self.node_map[element.exit]
                    self._algvar_list[idx] = 1
        
        # Process voltage source currents (keep as algebraic 0)
        
        # Process inductor currents (differential variables)
        for element in self.elements:
            if isinstance(element, Inductor):
                idx = self.vsrc_map[element]
                self._algvar_list[idx] = 1
    
    def add_element(self, element):
        # Direction validation
        if element.entrance == 0 and element.exit != 0:
            print(f"Warning: Resistor {element.name} has ground node as entrance. "
                    "Consider swapping entrance/exit nodes for consistency.")
    
        self.elements.append(element)
        
        # Add nodes to the set (excluding ground node 0)
        if element.entrance != 0:
            self.nodes.add(element.entrance)
        if element.exit != 0:
            self.nodes.add(element.exit)
        
        # Voltage source processing
        if isinstance(element, VoltageSource):
            self.voltage_sources.append(element)
        
        # Update variable type list
        self._update_algvar_list()
    
    def _build_maps(self):
        """
        Build mappings between nodes/sources and matrix indices.
        
        For DAE system:
        1. node_map: maps nodes to voltage indices
        2. vsrc_map: maps voltage sources and inductors to current indices
           - Voltage sources come first
           - Inductors follow voltage sources
        
        Returns:
            tuple: (number of nodes, number of voltage sources + inductors)
        """
        # Map nodes to indices (excluding ground node 0)
        sorted_nodes = sorted(list(self.nodes))
        self.node_map = {node: idx for idx, node in enumerate(sorted_nodes)}
        
        # First map voltage sources
        vsrc_start_idx = len(sorted_nodes)
        self.vsrc_map = {}
        for idx, src in enumerate(self.voltage_sources):
            self.vsrc_map[src] = vsrc_start_idx + idx
        
        # Then map inductors
        inductor_start_idx = vsrc_start_idx + len(self.voltage_sources)
        inductors = [elem for elem in self.elements if isinstance(elem, Inductor)]
        for idx, ind in enumerate(inductors):
            self.vsrc_map[ind] = inductor_start_idx + idx
        
        return len(sorted_nodes), len(self.voltage_sources) + len(inductors)
    
    def _build_mna_matrix(self, n_nodes, n_vsrc, debug=False):
        """
        Build the MNA matrix and RHS vector for DC analysis.
        
        Args:
            n_nodes (int): Number of nodes (excluding ground)
            n_vsrc (int): Number of voltage sources
            debug (bool): If True, print debug information
            
        Returns:
            tuple: (MNA matrix, RHS vector)
        """
        # Total size of the MNA matrix
        size = n_nodes + n_vsrc
        
        if debug:
            print(f"\nMatrix size: {size}x{size}")
            print(f"- Number of nodes (excluding ground): {n_nodes}")
            print(f"- Number of voltage sources: {n_vsrc}")
            print("\nNode mapping:", self.node_map)
            if n_vsrc > 0:
                print("Voltage source mapping:", 
                      {src.name: idx for src, idx in self.vsrc_map.items()})
        
        # Initialize MNA matrix and RHS vector
        matrix = np.zeros((size, size))
        vector = np.zeros(size)
        
        # Let each element contribute to the matrix
        for element in self.elements:
            element.stamp(matrix, vector, self.node_map, self.vsrc_map)
        
        if debug and size > 0:
            print("\nMNA Matrix:")
            print(matrix)
            print("\nRHS Vector:")
            print(vector)
            
            if n_nodes > 0 and n_vsrc > 0:
                print("\nSubmatrices:")
                print("G (conductances):")
                print(matrix[:n_nodes, :n_nodes])
                print("\nB (voltage source connections):")
                print(matrix[:n_nodes, n_nodes:])
                print("\nC (transpose of B):")
                print(matrix[n_nodes:, :n_nodes])
                print("\nD (should be zero):")
                print(matrix[n_nodes:, n_nodes:])
        
        return matrix, vector
    
    def _build_dc_maps(self):
        """
        Build mappings for DC analysis
        """
        # Map nodes to indices
        sorted_nodes = sorted(list(self.nodes))
        self.node_map = {node: idx for idx, node in enumerate(sorted_nodes)}
        
        # Only map voltage sources (no inductors)
        vsrc_start_idx = len(sorted_nodes)
        self.vsrc_map = {}
        for idx, src in enumerate(self.voltage_sources):
            self.vsrc_map[src] = vsrc_start_idx + idx
        
        return len(sorted_nodes), len(self.voltage_sources)
    
    def solve_dc(self, debug=False):
        """Solve DC operating point"""
        # Build DC maps (without inductors)
        n_nodes, n_vsrc = self._build_dc_maps()
        
        if n_nodes == 0:
            return {}
        
        # Initialize MNA matrix
        size = n_nodes + n_vsrc
        matrix = np.zeros((size, size))
        vector = np.zeros(size)
        
        # Let each element contribute to the matrix
        for element in self.elements:
            element.stamp(matrix, vector, self.node_map, self.vsrc_map)
        
        if debug:
            print("\nDC Analysis Debug Info:")
            print("Node map:", self.node_map)
            print("Vsrc map:", self.vsrc_map)
            print("\nMNA Matrix:")
            print(matrix)
            print("\nRHS Vector:")
            print(vector)
            
            # 打印子矩阵
            if n_nodes > 0 and n_vsrc > 0:
                print("\nSubmatrices:")
                print("G (conductances):")
                print(matrix[:n_nodes, :n_nodes])
                print("\nB (voltage source connections):")
                print(matrix[:n_nodes, n_nodes:])
                print("\nC (transpose of B):")
                print(matrix[n_nodes:, :n_nodes])
                print("\nD (should be zero):")
                print(matrix[n_nodes:, n_nodes:])
        
        try:
            solution = np.linalg.solve(matrix, vector)
            
            # Extract results
            result = {}
            
            # Node voltages
            for node, idx in self.node_map.items():
                result[f"V{node}"] = solution[idx]
            
            # Source currents
            for src, idx in self.vsrc_map.items():
                if isinstance(src, VoltageSource):
                    result[f"I_{src.name}"] = solution[idx]
            
            return result
            
        except np.linalg.LinAlgError as e:
            raise ValueError(f"Failed to solve circuit: {str(e)}\n"
                           "The system might be singular or poorly conditioned.")
    
    def validate_circuit(self):
        """
        Validate the circuit configuration.
        
        Returns:
            bool: True if circuit is valid, False otherwise
        """
        # check node connections
        node_connections = defaultdict(int)
        for element in self.elements:
            node_connections[element.entrance] += 1
            node_connections[element.exit] += 1
        
        # check floating nodes
        for node, count in node_connections.items():
            if count < 2 and node != 0:  # ground node can have only one connection
                print(f"Warning: Node {node} might be floating (only {count} connection)")
                return False
            
        return True
    
    def _get_consistent_initial_conditions(self, A, B, C):
        """
        Calculate consistent initial condiitons for DAE system
        For DAE system A * y' + B * y + C = 0
        Using algvar_list to calculate initial conditions
        - solve y0: (A * algvar_list + B)* y0 + C = 0
        """

        n_nodes, n_currents = self._build_maps()
        size = n_nodes + n_currents

        # Initialize matrices
        y0 = np.zeros(size)
        yd0 = np.zeros(size)
        
        # Build system matrix for algebraic variables
        # M * y0 = -C, where M = B for algebraic rows
        M = B.copy()
        
        # Zero out rows corresponding to differential variables
        for i in range(size):
             if self._algvar_list[i] == 1:
                M[i,:] = 0
                M[i,i] = 1
        
        y0 = np.linalg.solve(M, -C)
        
        return y0, yd0
    
    def build_dae_system(self):
        """
        Build DAE system matrices: A * dx/dt = B * x + C
        
        State vector order: x = [v1,...,vn, iV1,...,iVm, iL1,...,iLk]
        where:
        - v1 to vn: node voltages
        - iV1 to iVm: voltage source currents
        - iL1 to iLk: inductor currents
        
        Returns:
            tuple: (A, B, C) matrices and initial conditions (y0, yd0)
        """
        # Build node and current mappings
        n_nodes, n_currents = self._build_maps()
        
        # Total size of the system
        size = n_nodes + n_currents
        
        # Initialize matrices
        A = np.zeros((size, size))  # Derivative term coefficient matrix
        B = np.zeros((size, size))  # State variable coefficient matrix
        C = np.zeros(size)          # Constant term vector
        
        # Let each element contribute to the matrices
        for element in self.elements:
            element.stamp_dae(A, B, C, self.node_map, self.vsrc_map)
        
        # Use consistent initial conditions
        y0, yd0 = self._get_consistent_initial_conditions(A, B, C)
        
        return A, B, C, y0, yd0, self._algvar_list
    
    def solve_dae(self, t_span, debug=False):
        """
        Solve circuit DAE system for transient analysis.
        
        Args:
            t_span: tuple (t0, tf) for time range
            debug: bool, if True print debug information
            
        Returns:
            Solution object from DAESolver
        """
        # Build DAE system
        A, B, C, y0, yd0, algvar_list = self.build_dae_system()
        
        if debug:
            print("\nDAE System:")
            print("A matrix:")
            print(A)
            print("\nB matrix:")
            print(B)
            print("\nC vector:")
            print(C)
            print("\nInitial conditions:")
            print("y0:", y0)
            print("yd0:", yd0)
            print("algvar:", algvar_list)
        
        # Create solver with algvar configuration
        from .dae_solver import DAESolver
        solver = DAESolver({
            'algvar': algvar_list
        })
        
        def residual(t, y, yd):
            """DAE system residual function"""
            return A @ yd + B @ y + C
        
        return solver.solve(residual, t_span, y0, yd0)
    