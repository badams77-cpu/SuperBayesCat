class intPair:

    def __init__(self,a,b):
        self.a = a
        self.b = b

    def set_values(self, a, b):
        self.a = a
        self.b = b

    def __eq__(self, other):
        return self.a == other.a & self.b == other.b

    def __hash__(self):
        return 13*7*41* self.a + self.b

