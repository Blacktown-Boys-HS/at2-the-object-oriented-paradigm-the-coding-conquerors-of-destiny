class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def multiply(self, scalar):
        return Position(self.x * scalar, self.y * scalar)
    
    def multiply_xy(self, x_scalar, y_scalar):
        return Position(self.x * x_scalar, self.y * y_scalar)
    
    def add(self, other):
        if isinstance(other, Position):
            return Position(self.x + other.x, self.y + other.y)
        raise TypeError("Can only add Position objects")
    
    def subtract(self, other):
        if isinstance(other, Position):
            return Position(self.x - other.x, self.y - other.y)
        raise TypeError("Can only subtract Position objects")
    
    def distance_to(self, other):
        if isinstance(other, Position):
            dx = self.x - other.x
            dy = self.y - other.y
            return (dx ** 2 + dy ** 2) ** 0.5
        raise TypeError("Can only calculate distance to Position objects")
    
    def to_tuple(self):
        return (self.x, self.y)
    
    def to_int_tuple(self):
        return (int(self.x), int(self.y))
    
    def __repr__(self):
        return f"Position({self.x}, {self.y})"
    
    def __str__(self):
        return f"({self.x}, {self.y})"