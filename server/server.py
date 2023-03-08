# -*- coding: utf-8 -*-

from flask import Flask, jsonify, request, Response
from flask_cors import CORS, cross_origin

import json
import pandas as pd

from data_manager.insee_general.adjacent import get_adjacent
from model.territory import Territory
from model.territory_output import TerritoryOutput


def launch_server():
    app = Flask(__name__)
    CORS(app)
    app.config['CORS_HEADERS'] = 'Content-Type'

    @app.route('/territory', methods=['GET', 'POST', 'OPTIONS'])
    @cross_origin()
    def territory():
        # handling request from interface
        if request.method == 'POST':
            print(request.content_type)
            request_json = request.get_json(force=False)

            title = request_json["title"]
            geo_codes = request_json["geo_codes"]
            zones = request_json["zones"]
            print(geo_codes)

            # influence communes are adjacent communes
            influence_communes = [i for i in set(sum([get_adjacent(None, g) for g in geo_codes], [])) if i not in geo_codes]

            if 2 not in zones:
                zones = [2 if z==3 else z for z in zones]
            if 1 not in zones:
                zones = [z-1 for z in zones]

            # create territory & territory_output objects
            territory = Territory(title,
                                  geo_codes,
                                  zones,
                                  influence_communes)
            territory_output = TerritoryOutput(territory)

            # save results locally into json file
            with open('territory-' + title.replace(" ", "-") + '.json', 'w') as f:
                json.dump(territory_output.__dict__, f)

            # send results as request response
            response = jsonify(territory_output.__dict__)
            return response
        elif request.method == 'OPTIONS':
            return "", 200

    print()
    print("-- starting server")
    app.run(debug=False)


if __name__ == '__main__':
    pd.set_option('display.max_columns', 100)
    pd.set_option('display.max_rows', 60)
    pd.set_option('display.width', 4000)
    launch_server()



