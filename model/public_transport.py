class PublicTransport:
    """
    PublicTransport is a class which describes a public transport service based on GTFS standard
    """
    counter_id = 1

    def __init__(self, route_id, route_short_name, route_long_name, route_type, stops_name, stops_lat, stops_lon):
        """Constructor of class"""
        """
        stops_name : (List) of main trip stops name
        stops_lat : (List) of main trip stops latitude
        stops_lon : (List) of main trip stops longitude
        """
        self.id = PublicTransport.counter_id
        PublicTransport.counter_id += 1
        self.route_id = route_id
        self.route_name = route_short_name + " - " + route_long_name
        self.route_type = route_type
        self.stops_name = stops_name
        self.stops_lat = stops_lat
        self.stops_lon = stops_lon

    def presentation(self):
        print(f"Public Transport | {self.route_name}")

    def plot_route(self):
        from matplotlib import pyplot as plt
        plt.plot(self.stops_lon, self.stops_lat)
        plt.title(self.route_name)
        plt.axis('equal')
        plt.show()

    def to_dict(self):
        return {
            "name": self.route_name,
            "type": int(self.route_type),
            "stops_name": self.stops_name.to_list(),
            "stops_lat": self.stops_lat.to_list(),
            "stops_lon": self.stops_lon.to_list(),
            "stops": [{"name": name,
                       "coords": [lat, lon]} for name, lat, lon in zip(self.stops_name, self.stops_lat, self.stops_lon)]
        }
