"""
Circuit class for Modified Nodal Analysis (MNA).

The MNA matrix equation has the form:
[G B] [v] = [i]
[C D] [j]   [e]

where:
- G (n * n): Conductance matrix for passive elements
- B (n * m): Voltage source connections
- C (m * n): Typically B^T for independent sources
- D (m * m): Zero for independent sources
- v: Node voltage vector
- j: Source current vector
- i: Known current vector
- e: Source voltage vector
"""

import numpy as np
from collections import defaultdict

class Circuit:
    """Circuit class for Modified Nodal Analysis (MNA)."""
    
    def __init__(self):
        """Initialize an empty circuit."""
        self.elements = []          # All circuit elements
        self.nodes = set()          # Set of all nodes (excluding ground)
        self.voltage_sources = []   # List of voltage sources
        self.node_map = {}          # Maps node numbers to matrix indices
        self.vsrc_map = {}          # Maps voltage sources to matrix indices
    
    def add_element(self, element):
        """
        Add an element to the circuit.
        
        Args:
            element: Component object to add
        """
        # Direction validation
        if element.__class__.__name__ == "Resistor":
            if element.entrance == 0 and element.exit != 0:
                print(f"Warning: Resistor {element.name} has ground node as entrance. "
                      "Consider swapping entrance/exit nodes for consistency.")
        
        self.elements.append(element)
        
        # Add nodes to the set (excluding ground node 0)
        if element.entrance != 0:
            self.nodes.add(element.entrance)
        if element.exit != 0:
            self.nodes.add(element.exit)
            
        # Keep track of voltage sources separately
        if element.__class__.__name__ == "VoltageSource":
            self.voltage_sources.append(element)
    
    def _build_maps(self):
        """
        Build mappings between nodes/sources and matrix indices.
        
        Returns:
            tuple: (number of nodes, number of voltage sources)
        """
        # Map nodes to indices (excluding ground node 0)
        sorted_nodes = sorted(list(self.nodes))
        self.node_map = {node: idx for idx, node in enumerate(sorted_nodes)}
        
        # Map voltage sources to indices
        self.vsrc_map = {src: idx for idx, src in enumerate(self.voltage_sources)}
        
        return len(sorted_nodes), len(self.voltage_sources)
    
    def _build_mna_matrix(self, n_nodes, n_vsrc, debug=False):
        """
        Build the MNA matrix and RHS vector.
        
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
    
    def solve_dc(self, debug=False):
        """
        Solve the circuit for DC operating point.
        
        Args:
            debug (bool): If True, print debug information
            
        Returns:
            dict: Solution containing node voltages and source currents
        """
        # Build node and voltage source mappings
        n_nodes, n_vsrc = self._build_maps()
        
        if n_nodes == 0:
            return {}  # Empty circuit
        
        # Build and solve the MNA system
        matrix, vector = self._build_mna_matrix(n_nodes, n_vsrc, debug)
        
        try:
            solution = np.linalg.solve(matrix, vector)
            
            # Extract results
            result = {}
            
            # Node voltages (v vector)
            for node, idx in self.node_map.items():
                result[f"V{node}"] = solution[idx]
            
            # Source currents (j vector)
            for src, idx in self.vsrc_map.items():
                result[f"I_{src.name}"] = solution[n_nodes + idx]
            
            if debug:
                print("\nSolution:")
                for name, value in result.items():
                    if name.startswith('V'):
                        print(f"{name}: {value:.6f}V")
                    else:
                        print(f"{name}: {value*1000:.6f}mA")
            
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