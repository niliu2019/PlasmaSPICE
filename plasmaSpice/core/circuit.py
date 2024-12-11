import numpy as np
from collections import defaultdict

class Circuit:
    """Circuit class for Modified Nodal Analysis (MNA)."""
    
    def __init__(self):
        """Initialize an empty circuit."""
        self.elements = []
        self.nodes = set()
        self.node_map = {}  # Maps node numbers to matrix indices
    
    def add_element(self, element):
        """
        Add an element to the circuit.
        
        Args:
            element: Component object to add
        """
        self.elements.append(element)
        if element.entrance != 0:  # Don't add ground node
            self.nodes.add(element.entrance)
        if element.exit != 0:  # Don't add ground node
            self.nodes.add(element.exit)
    
    def _build_node_map(self):
        """Build mapping between node numbers and matrix indices."""
        sorted_nodes = sorted(list(self.nodes))
        self.node_map = {node: idx for idx, node in enumerate(sorted_nodes)}
        return len(sorted_nodes)
    
    def solve_dc(self, debug=False):
        """
        Solve the circuit for DC operating point.
        
        Args:
            debug (bool): If True, print debug information
            
        Returns:
            dict: Node voltages keyed by node number
        """
        # Get matrix size (number of nodes excluding ground)
        size = self._build_node_map()
        
        # Initialize MNA matrix and RHS vector
        matrix = np.zeros((size, size))
        vector = np.zeros(size)
        
        # Build MNA matrix
        for element in self.elements:
            element.stamp(matrix, vector)
        
        if debug:
            print("Node mapping:", self.node_map)
            print("\nMNA Matrix:")
            print(matrix)
            print("\nRHS Vector:")
            print(vector)
        
        # Solve system
        try:
            voltages = np.linalg.solve(matrix, vector)
            result = {node: voltages[idx] for node, idx in self.node_map.items()}
            
            if debug:
                print("\nNode Voltages:")
                for node, voltage in result.items():
                    print(f"Node {node}: {voltage:.3f}V")
            
            return result
        except np.linalg.LinAlgError:
            raise ValueError("The system is singular or nearly singular.")