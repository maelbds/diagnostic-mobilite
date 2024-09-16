from flask import request
from marshmallow import Schema, fields, ValidationError, post_load, validate


def check_geocodes(geocodes):
    def is_geocode(geo_code):
        return (len(geo_code) == 5) & geo_code.isalnum()
    return [g for g in geocodes if is_geocode(g)]


class Perimeter:
    def __init__(self, geo_codes, year=None, mesh=None):
        self.geo_codes = geo_codes
        self.year = year
        self.mesh = mesh


class PerimeterSchema(Schema):
    geo_codes = fields.List(fields.String())
    mesh = fields.String(validate=validate.OneOf(["com", "epci", "dep"]))
    year = fields.Integer()

    @post_load
    def make_perimeter(self, data, **kwargs):
        return Perimeter(**data)


class PerimeterRequest:
    def __init__(self):
        self.schema = PerimeterSchema()

    def parse(self):
        json_data = request.get_json()
        if not json_data:
            return {"message": "No input data provided"}, 400
        # Validate and deserialize input
        try:
            args = self.schema.load(request.get_json())
        except ValidationError as err:
            return err.messages, 422
        return args


perimeter_request = PerimeterRequest()


class BeneficiariesAdresses:
    def __init__(self, code_postal, nom_commune):
        self.postal_codes = code_postal
        self.names = nom_commune


class BeneficiariesAdressesSchema(Schema):
    code_postal = fields.List(fields.String())
    nom_commune = fields.List(fields.String())

    @post_load
    def make_perimeter(self, data, **kwargs):
        return BeneficiariesAdresses(**data)


class BeneficiariesAdressesRequest:
    def __init__(self):
        self.schema = BeneficiariesAdressesSchema()

    def parse(self):
        json_data = request.get_json()
        if not json_data:
            return {"message": "No input data provided"}, 400
        # Validate and deserialize input
        try:
            args = self.schema.load(request.get_json())
        except ValidationError as err:
            return err.messages, 422
        return args


beneficaries_adresses_request = BeneficiariesAdressesRequest()
