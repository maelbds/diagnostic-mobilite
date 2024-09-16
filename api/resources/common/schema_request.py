import pandas as pd

from flask import request
from marshmallow import Schema, fields, ValidationError, post_load, validate, exceptions

from api.resources.common.db_request import db_request


def check_geocodes(geocodes):
    def is_geocode(geo_code):
        return (len(geo_code) == 5) & geo_code.isalnum()
    return [g for g in geocodes if is_geocode(g)]


result = db_request(
    """ SELECT CODGEO_INI, CODGEO_DES 
        FROM insee_passage_cog
        WHERE year_cog = :year_cog
    """,
    {
        "year_cog": "2023",
    }
)
passage_cog2023 = pd.DataFrame(result, columns=["from", "to"]).set_index("from")


def geocodes_to_cog2023(geocodes):
    return passage_cog2023.loc[geocodes, "to"].drop_duplicates().to_list()


class DelimitedListField(fields.List):
    def _deserialize(self, value, attr, data, **kwargs):
        try:
            return value.split(",")
        except AttributeError:
            raise exceptions.ValidationError(
                f"{attr} is not a delimited list it has a non string value {value}."
            )


class Perimeter:
    def __init__(self, geo_codes, year=None, mesh=None):
        self.geo_codes = geocodes_to_cog2023(geo_codes) if mesh == "com" or mesh is None else geo_codes
        self.year = year
        self.mesh = mesh


class ContextGetSchema(Schema):
    geo_codes = DelimitedListField(fields.String())
    mesh = fields.String(validate=validate.OneOf(["com", "epci", "dep"]))
    year = fields.Integer()

    @post_load
    def make_perimeter(self, data, **kwargs):
        return Perimeter(**data)


class ContextPostSchema(Schema):
    geo_codes = fields.List(fields.String())
    mesh = fields.String(validate=validate.OneOf(["com", "epci", "dep"]))
    year = fields.Integer()

    @post_load
    def make_perimeter(self, data, **kwargs):
        return Perimeter(**data)


class ContextGetRequest:
    def __init__(self):
        self.schema = ContextGetSchema()

    def parse(self):
        try:
            args = self.schema.load(request.args.to_dict())
        except ValidationError as err:
            return err.messages, 422
        return args


class ContextPostRequest:
    def __init__(self):
        self.schema = ContextPostSchema()

    def parse(self):
        try:
            args = self.schema.load(request.get_json())
        except ValidationError as err:
            return err.messages, 422
        return args


context_get_request = ContextGetRequest()
context_post_request = ContextPostRequest()

