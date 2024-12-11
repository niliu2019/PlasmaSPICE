"""
Circuit elements for Modified Nodal Analysis (MNA).

Each element contributes to different parts of the MNA matrix:
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

class Component:
    """Base class for all circuit elements."""
    
    def __init__(self, name, entrance, exit):
        """
        Initialize a circuit element.
        
        Args:
            name (str): Unique identifier for the element
            entrance (int): Positive terminal node number
            exit (int): Negative terminal node number
        """
        self.name = name
        self.entrance = entrance
        self.exit = exit
    
    def stamp(self, matrix, vector, node_map, vsrc_map):
        """
        Contribute to the MNA matrix equation.
        
        Args:
            matrix: The complete MNA matrix [G B; C D]
            vector: The RHS vector [i; e]
            node_map: Dictionary mapping node numbers to matrix indices
            vsrc_map: Dictionary mapping voltage sources to matrix indices
        """
        raise NotImplementedError("Stamp method must be implemented by subclasses")


class Resistor(Component):
    """Resistor element for circuit simulation."""
    
    def __init__(self, name, entrance, exit, resistance):
        """
        Initialize a resistor.
        
        Args:
            name (str): Unique identifier for the resistor
            entrance (int): Positive terminal node number
            exit (int): Negative terminal node number
            resistance (float): Resistance value in ohms
        """
        super().__init__(name, entrance, exit)
        self.resistance = resistance
        self.conductance = 1.0 / resistance
    
    def stamp(self, matrix, vector, node_map, vsrc_map):
        """
        Add resistor contributions to the G submatrix.
        
        For a resistor between nodes i and j:
        - Add conductance to G[i,i] and G[j,j]
        - Subtract conductance from G[i,j] and G[j,i]
        
        The resistor only affects the G submatrix (conductances)
        and does not contribute to B, C, or D submatrices.
        """
        # Only stamp in the G submatrix (upper-left block)
        if self.entrance != 0:  # entrance is not ground
            i = node_map[self.entrance]
            matrix[i, i] += self.conductance
            if self.exit != 0:
                j = node_map[self.exit]
                matrix[i, j] -= self.conductance
                matrix[j, i] -= self.conductance
        
        if self.exit != 0:  # exit is not ground
            j = node_map[self.exit]
            matrix[j, j] += self.conductance


class VoltageSource(Component):
    """Independent voltage source element."""
    
    def __init__(self, name, entrance, exit, voltage):
        """
        Initialize a voltage source.
        
        Args:
            name (str): Unique identifier for the source
            entrance (int): Positive terminal node number
            exit (int): Negative terminal node number
            voltage (float): Source voltage in volts
        """
        super().__init__(name, entrance, exit)
        self.voltage = voltage
    
    def stamp(self, matrix, vector, node_map, vsrc_map):
        """
        Add voltage source contributions to the MNA matrix.
        
        For a voltage source between nodes i and j:
        1. In B matrix (and C = B^T):
           - Add +1 to B[i,k] and -1 to B[j,k]
           where k is the index of this voltage source
        2. In RHS vector:
           - Add voltage value to e[k]
        
        The voltage source contributes to:
        - B submatrix: Relates node voltages to source currents
        - C submatrix: Relates source currents to node voltages (C = B^T)
        - e vector: Contains the voltage source value
        """
        # Get the index for this voltage source in the extended part of the matrix
        k = len(node_map) + vsrc_map[self]
        
        # Stamp B and C matrices (B[i,k] and C[k,i])
        if self.entrance != 0:  # positive terminal not grounded
            i = node_map[self.entrance]
            matrix[i, k] += 1.0  # B matrix
            matrix[k, i] += 1.0  # C matrix
        
        if self.exit != 0:  # negative terminal not grounded
            j = node_map[self.exit]
            matrix[j, k] -= 1.0  # B matrix
            matrix[k, j] -= 1.0  # C matrix
        
        # Add voltage to RHS vector (e part)
        vector[k] = self.voltage


class CurrentSource(Component):
    """Independent current source element."""
    
    def __init__(self, name, entrance, exit, current):
        """
        Initialize a current source.
        
        Args:
            name (str): Unique identifier for the source
            entrance (int): Current entering node number
            exit (int): Current exiting node number
            current (float): Source current in amperes (positive means current flows
                           from entrance to exit)
        """
        super().__init__(name, entrance, exit)
        self.current = current
    
    def stamp(self, matrix, vector, node_map, vsrc_map):
        """
        Add current source contributions to the MNA matrix.
        
        For a current source between nodes i and j:
        - Add +I to RHS vector at node i
        - Add -I to RHS vector at node j
        
        The current source only contributes to the i vector (RHS)
        and does not affect the MNA matrix itself.
        """
        # Add current to RHS vector (i part)
        if self.entrance != 0:  # current entering node
            i = node_map[self.entrance]
            vector[i] -= self.current  # current flowing in adds negative current
        
        if self.exit != 0:  # current exiting node
            j = node_map[self.exit]
            vector[j] += self.current  # current flowing out adds positive current