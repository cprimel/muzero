class Card:
    values = {
        "2": 2,
        "3": 3,
        "4": 4,
        "5": 5,
        "6": 6,
        "7": 7,
        "8": 8,
        "9": 9,
        "10": 10,
        "J": 10,
        "Q": 10,
        "K": 10,
        "A": 11,
    }

    def __init__(self, face: str):
        self.face = face
        self.value = self.values[face]

    def __eq__(self, other):
        return self.face == other

    def __str__(self):
        return self.face

    def __repr__(self):
        return str(self.face)
