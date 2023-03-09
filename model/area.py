import numpy as np

from model.functions.cluster import create_outline


class Area:
    """
    Area is a class used into the origin/destination matrix
    """
    counter_id = 1

    def __init__(self, name, coords, mass, category, category_fr, reason, reason_fr):
        """
        Constructor
        :param name: (String) Name of area
        :param coords: (List) [lat, lon] GPS coordinates of area
        :param mass: (Int) Visitors/population/mass of the area
        """
        self.id = Area.counter_id
        Area.counter_id += 1
        self.name = name
        self.coords = coords
        self.mass = mass
        self.category = category
        self.category_fr = category_fr
        self.reason = reason
        self.reason_fr = reason_fr

    def presentation(self):
        print(f"Area | {self.name} - {self.coords} - {self.mass} - {self.category} ")

    def to_dict_output(self):
        return {
            "id": self.id,
            "name": self.name,
            "coords": list(np.array(self.coords)),
            "mass": self.mass,
            "category": self.category,
            "category_fr": self.category_fr,
            "reason": self.reason,
            "reason_fr": self.reason_fr
        }

    def to_dict_distance_matrix(self):
        return {
            "id": self.id,
            "name": self.name,
            "coords": list(np.array(self.coords)),
            "mass": self.mass,
            "category": self.category,
        }


class ResidentialArea(Area):
    """
    ResidentialArea is an Area dedicated to residential : where people live.
    """

    def __init__(self, name, coords, mass, commune, outline):
        """
        Constructor
        :param name: see above
        :param coords: see above
        :param mass: (Int) Population of the residential area
        :param outline: (List) [[lat, lon]] of the outline of the residential area
        """
        Area.__init__(self, name, coords, mass, "residential", "résidentiel", "residential", "résidentiel")
        self.outline = outline
        self.households = []

    def get_min_max_lat_outline(self):
        lat = np.array(self.outline)[:, 0]
        return [min(lat), max(lat)]

    def get_min_max_lon_outline(self):
        lon = np.array(self.outline)[:, 1]
        return [min(lon), max(lon)]


class WorkArea(Area):
    """
    WorkArea is an Area dedicated to work places : where people work.
    """

    def __init__(self, name, coords, mass, commune):
        """
        Constructor
        :param name: see above
        :param coords: see above
        :param mass: (Int) Employees of the work area
        """
        Area.__init__(self, name, coords, mass, "work", "travail", "work", "travail")
        self.jobs_nb = mass


class ClusterArea(Area):
    """
    ClusterArea is a cluster of Places.
    """

    def __init__(self, places, commune):
        """
        Constructor
        :param name: see above
        :param coords: see above
        :param mass: (Int) Visitors of the zones area
        :param places: (List) of (Zone) which composed the zones area
        """
        places_types = [p.type_fr for p in places]
        types = {t: places_types.count(t) for t in places_types}
        names = [f"{type_count} {type_name}" for type_name, type_count in types.items()]
        name = " - ".join(names)

        mass = sum([p.mass for p in places])
        coords = np.mean([p.coords for p in places], axis=0)
        outline = create_outline([p.coords for p in places]) if len(set([p.coords[0] for p in places])) > 3 \
                                                               and len(set([p.coords[1] for p in places])) > 3 \
                                                             else [p.coords for p in places]
        category = places[0].category
        category_fr = places[0].category_fr
        reason = places[0].reason
        reason_fr = places[0].reason_fr
        Area.__init__(self, name, coords, mass, category, category_fr, reason, reason_fr)
        self.places = places
        self.outline = outline
        self.level = None

    def contains_type(self, type):
        return any([p.type == type for p in self.places])

    def to_dict_output(self):
        return {
            "id": self.id,
            "name": self.name,
            "coords": list(np.array(self.coords)),
            "mass": self.mass,
            "category": self.category,
            "category_fr": self.category_fr,
            "reason": self.reason,
            "reason_fr": self.reason_fr,
            "outline": self.outline,
            "level": self.level
        }
