class Place:
    """
    Place is a class which describes a place of interest
    """
    counter_id = 1

    def __init__(self, name, mass, coords, type, type_fr, category, category_fr, reason, reason_fr, characteristic=False):
        """Constructor of class"""
        self.id = Place.counter_id
        Place.counter_id += 1
        self.name = name
        self.mass = mass + 1
        self.coords = coords
        self.type = type
        self.type_fr = type_fr
        self.category = category
        self.category_fr = category_fr
        self.reason = reason
        self.reason_fr = reason_fr
        self.characteristic = characteristic

    def presentation(self):
        print(f"Place | {self.name} - {self.coords} - {self.mass} - {self.type} ")

