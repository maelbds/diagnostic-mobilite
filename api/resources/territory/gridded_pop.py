import pandas as pd
import numpy as np
from pyproj import Transformer

from api.resources.common.cog import COG
from api.resources.common.log_stats import log_stats
from data_manager.sources.sources import get_years_for_source, get_label_link_for_source_year

from api.resources.common.db_request import db_request

from flask_restful import Resource

from api.resources.common.log_message import message_request
from api.resources.common.schema_request import context_get_request

source_label = "insee_filosofi_gridded_pop"

dataset_gridded_pop = {
    "endpoint": "territory/gridded_pop",
    "is_mesh_element": False,
    "meshes": None,
    "name_year": "INSEE Filosofi au carreau",
    "years": get_years_for_source(source_label),
}


# Legend : compute quantile
def compute_quantile():
    result = db_request(
        """ SELECT gp.ind, gp.men, gp.men_surf, gp.ind_snv
            FROM insee_filosofi_gridded_pop AS gp
        """,
        {}
    )
    gridded_population = pd.DataFrame(result, columns=["population", "households", "surface", "incomes"], dtype=float)
    gridded_population["pers/hh"] = gridded_population["population"] / gridded_population["households"]
    gridded_population["surf/hh"] = gridded_population["surface"] / gridded_population["households"]
    gridded_population["incomes/pers"] = gridded_population["incomes"] / gridded_population["population"]
    legend = gridded_population.dropna().quantile([0, .2, .4, .6, .8, 1]).round(1)
    print(gridded_population.max())
    print(legend)


def get_gridded_pop(geo_codes, year):
    sources = [get_label_link_for_source_year(name, year) for name in [source_label]]

    result = db_request(
        """ SELECT p.CODGEO_DES, gp.idGrid200, gp.ind, gp.men, gp.men_surf, gp.ind_snv
            FROM insee_filosofi_gridded_pop AS gp
            JOIN insee_passage_cog AS p ON gp.geo_code = p.CODGEO_INI
            WHERE p.CODGEO_DES IN :geo_codes 
            AND year_data = :year_data
            AND p.year_cog = :cog
        """,
        {
            "geo_codes": geo_codes,
            "year_data": year,
            "cog": COG
        }
    )
    gridded_population = pd.DataFrame(result, columns=["geo_code", "idGrid200", "population", "households", "surface", "incomes"],
                                      dtype=str)

    all_epsgs = set([g[3:7] for g in gridded_population["idGrid200"]])
    transformers = {epsg: Transformer.from_crs(f"epsg:{epsg}", "epsg:4326", always_xy=True) for epsg in all_epsgs}

    def to_geo(epsg, x, y):
        lon, lat = transformers[epsg].transform(x, y)
        return [lon, lat]

    def idToCoordsGeo(id):
        epsg = id[3:7]
        coords = id.split("N")[-1]
        y, x = coords.split("E")
        return to_geo(epsg, x, y)

    gridded_population["coords_geo"] = gridded_population["idGrid200"].apply(lambda id: idToCoordsGeo(id))
    gridded_population = gridded_population.astype({"population": "float",
                                                    "households": "float",
                                                    "incomes": "float",
                                                    "surface": "float"})

    gridded_population.drop(columns="idGrid200", inplace=True)
    gridded_population = gridded_population.replace({np.nan: None})

    return {
        "elements": {
            "gridded_pop": {
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "properties": {
                    "coordinates": coords,
                    "population": pop,
                    "households": hh,
                    "surface": surf,
                    "incomes": inc,
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": coords
                }
            } for coords, pop, hh, surf, inc in zip(
                gridded_population["coords_geo"],
                gridded_population["population"],
                gridded_population["households"],
                gridded_population["surface"],
                gridded_population["incomes"],
            )]
        }},
        #"legend": legend.to_dict(orient="list"),
        "sources": sources,
        "is_mesh_element": False
    }


class GriddedPop(Resource):
    def get(self):
        perimeter = context_get_request.parse()
        geo_codes = perimeter.geo_codes
        year = perimeter.year

        log_stats("gridded_pop", geo_codes, None, year)
        message_request("gridded_pop", geo_codes)
        return get_gridded_pop(geo_codes, year)


if __name__ == '__main__':
    pd.set_option('display.max_columns', 40)
    pd.set_option('display.max_rows', 100)
    pd.set_option('display.width', 1500)

    print(get_gridded_pop(["97209"], "2019"))

