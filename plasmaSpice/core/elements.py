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
    
    def stamp(self, matrix, vector):
        """
        Contribute to the MNA matrix equation (Ax = b).
        
        Args:
            matrix: The MNA matrix (A)
            vector: The right-hand side vector (b)
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
    
    def stamp(self, matrix, vector):
        """
        Add resistor contributions to the MNA matrix.
        
        For a resistor between nodes i and j:
        - Add conductance to matrix[i][i] and matrix[j][j]
        - Subtract conductance from matrix[i][j] and matrix[j][i]
        """
        if self.entrance != 0:  # entrance is not ground
            matrix[self.entrance-1][self.entrance-1] += self.conductance
            if self.exit != 0:  # exit is not ground
                matrix[self.entrance-1][self.exit-1] -= self.conductance
        
        if self.exit != 0:  # exit is not ground
            matrix[self.exit-1][self.exit-1] += self.conductance
            if self.entrance != 0:  # entrance is not ground
                matrix[self.exit-1][self.entrance-1] -= self.conductance


class VoltageSource(Component):
    """Independent voltage source element."""
    
    def __init__(self, name, entrance, exit, voltage, internal_resistance=1e-6):
        """
        Initialize a voltage source.
        
        Args:
            name (str): Unique identifier for the source
            entrance (int): Positive terminal node number
            exit (int): Negative terminal node number
            voltage (float): Source voltage in volts
            internal_resistance (float): Internal resistance in ohms (default: 1µΩ)
        """
        super().__init__(name, entrance, exit)
        self.voltage = voltage
        self.internal_resistance = internal_resistance
        self.conductance = 1.0 / internal_resistance
    
    def stamp(self, matrix, vector):
        """
        Add voltage source contributions to the MNA matrix.
        Refer to https://lpsa.swarthmore.edu/Systems/Electrical/mna/MNA3.html
        
        For an ideal voltage source:
        - Add conductance to account for internal resistance
        - Add voltage to the RHS vector
        """
        # Add internal resistance contribution
        if self.entrance != 0:
            matrix[self.entrance-1][self.entrance-1] += self.conductance
            if self.exit != 0:
                matrix[self.entrance-1][self.exit-1] -= self.conductance
        
        if self.exit != 0:
            matrix[self.exit-1][self.exit-1] += self.conductance
            if self.entrance != 0:
                matrix[self.exit-1][self.entrance-1] -= self.conductance
        
        # Add voltage source contribution
        if self.entrance != 0:
            vector[self.entrance-1] += self.voltage * self.conductance
        if self.exit != 0:
            vector[self.exit-1] -= self.voltage * self.conductance