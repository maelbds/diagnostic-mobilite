class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class UnknownGeocodeError(Error):
    """Exception raised if the given geocode returns a 404 response with INSEE API.

    Attributes:
        expression -- given geocode
        message -- explanation of the error
    """

    def __init__(self, expression):
        self.expression = expression
        self.message = "No data found for given geocode : " + str(expression)


class UnknownPostalcodeError(Error):
    """Exception raised if the given postal code & associated name does not correspond to any geo_code inside
    insee_communes database.

    Attributes:
        expression -- given geocode
        message -- explanation of the error
    """

    def __init__(self, expression):
        self.expression = expression
        self.message = "No data found for given postal code and name : " + str(expression)
