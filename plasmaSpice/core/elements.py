"""
Circuit elements for Modified Nodal Analysis (MNA) and DAE systems.

For DC analysis (MNA):
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

For DAE system A * dx/dt = B * x + C:
State vector order: x = [v1,...,vn, iV1,...,iVm, iL1,...,iLk]
where:
- v1 to vn: node voltages (from node_map)
- iV1 to iVm: voltage source currents (from vsrc_map)
- iL1 to iLk: inductor currents (from vsrc_map)

Index mapping:
- node_map: maps node numbers to voltage indices [0, n-1]
- vsrc_map: maps voltage sources and inductors to current indices [n, n+m+k-1]
  - Voltage source currents: [n, n+m-1]
  - Inductor currents: [n+m, n+m+k-1]
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
        """DC Analysis"""
        raise NotImplementedError
        
    def stamp_dae(self, A, B, C, node_map, vsrc_map):
        """DAE Analysis"""
        raise NotImplementedError


class Resistor(Component):
    """Resistor element for circuit simulation."""
    
    def __init__(self, name, entrance, exit, resistance):
        """
        Initialize a resistor.
        
        Args:
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
    
    def stamp_dae(self, A, B, C, node_map, vsrc_map):
        """Resistor contribution to DAE system."""
        
        if self.entrance != 0:
            i = node_map[self.entrance]
            B[i,i] += self.conductance
            if self.exit != 0:
                j = node_map[self.exit]
                B[i,j] -= self.conductance
                B[j,i] -= self.conductance
        
        if self.exit != 0:
            j = node_map[self.exit]
            B[j,j] += self.conductance


class VoltageSource(Component):
    """Independent voltage source element."""
    
    def __init__(self, name, entrance, exit, voltage):
        """
        Initialize a voltage source.
        
        Args:
            name (str): Unique identifier for the source
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
        k = vsrc_map[self]
        
        if self.entrance != 0:
            i = node_map[self.entrance]
            matrix[i, k] += 1.0
            matrix[k, i] += 1.0
        
        if self.exit != 0:
            j = node_map[self.exit]
            matrix[j, k] -= 1.0
            matrix[k, j] -= 1.0
        
        # Add voltage to RHS vector (e part)
        vector[k] = self.voltage
    
    def stamp_dae(self, A, B, C, node_map, vsrc_map):
        """Voltage source contribution to DAE system."""
        i_idx = vsrc_map[self]
        
        if self.entrance != 0:
            i = node_map[self.entrance]
            B[i_idx, i] = 1.0
            B[i, i_idx] = -1.0
        
        if self.exit != 0:
            j = node_map[self.exit]
            B[i_idx, j] = -1.0
            B[j, i_idx] = 1.0
        
        C[i_idx] = -self.voltage


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

    def stamp_dae(self, A, B, C, node_map, vsrc_map):
        """
        Current source only contributes to C vector
        Adds current to KCL equations:
        - Positive current entering node i
        - Negative current leaving node j
        """
        
        if self.entrance != 0:
            i = node_map[self.entrance]
            C[i] -= self.current
        
        if self.exit != 0:
            j = node_map[self.exit]
            C[j] += self.current


class Capacitor(Component):
    """Capacitor element for circuit simulation."""
    
    def __init__(self, name, entrance, exit, capacitance):
        """
        Initialize a capacitor.
        
        Args:
            name (str): Unique identifier for the capacitor
            capacitance (float): Capacitance value in farads
        """
        super().__init__(name, entrance, exit)
        self.capacitance = capacitance
    
    def stamp(self, matrix, vector, node_map, vsrc_map):
        """DC Analysis: Capacitor as large resistance."""
        r = 1e9  # 1GΩ
        
        if self.entrance != 0:
            i = node_map[self.entrance]
            matrix[i, i] += 1/r
            if self.exit != 0:
                j = node_map[self.exit]
                matrix[i, j] -= 1/r
                matrix[j, i] -= 1/r
                matrix[j, j] += 1/r
        elif self.exit != 0:
            j = node_map[self.exit]
            matrix[j, j] += 1/r
    
    def stamp_dae(self, A, B, C, node_map, vsrc_map):
        """
        Capacitor only contribute for the A matrix
        i = C * d(vi - vj)/dt
        """
        if self.entrance != 0:
            i = node_map[self.entrance]
            A[i,i] += self.capacitance
            if self.exit != 0:
                j = node_map[self.exit]
                A[i,j] -= self.capacitance
                A[j,i] -= self.capacitance
        
        if self.exit != 0:
            j = node_map[self.exit]
            A[j,j] += self.capacitance


class Inductor(Component):
    """Inductor element for circuit simulation."""
    
    def __init__(self, name, entrance, exit, inductance):
        """
        Initialize an inductor.
        
        Args:
            name (str): Unique identifier for the inductor
            inductance (float): Inductance value in henries
        """
        super().__init__(name, entrance, exit)
        self.inductance = inductance
    
    def stamp(self, matrix, vector, node_map, vsrc_map):
        """
        Add inductor contributions to the MNA matrix.
        For DC analysis, inductor is treated as a short circuit.
        """
        # In DC analysis, inductor is a short circuit
        # Use a very small resistance to approximate short circuit
        r = 1e-6  # 1 μΩ
        
        if self.entrance != 0:
            i = node_map[self.entrance]
            matrix[i, i] += 1/r
            if self.exit != 0:
                j = node_map[self.exit]
                matrix[i, j] -= 1/r
                matrix[j, i] -= 1/r
                matrix[j, j] += 1/r
        elif self.exit != 0:
            j = node_map[self.exit]
            matrix[j, j] += 1/r
    
    def stamp_dae(self, A, B, C, node_map, vsrc_map):
        """Inductor contribution to DAE system."""
        iL_idx = vsrc_map[self]
        
        A[iL_idx, iL_idx] = -self.inductance
        
        if self.entrance != 0:
            i = node_map[self.entrance]
            B[iL_idx, i] = 1.0
            B[i, iL_idx] = 1.0
        
        if self.exit != 0:
            j = node_map[self.exit]
            B[iL_idx, j] = -1.0
            B[j, iL_idx] = -1.0