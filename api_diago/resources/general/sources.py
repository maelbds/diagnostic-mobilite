from data_manager.main import get_sources

from flask_restful import Resource


class Sources(Resource):
    def post(self):
        return get_sources()
