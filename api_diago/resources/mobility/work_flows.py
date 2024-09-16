import pandas as pd
import numpy as np
from shapely.geometry import shape, mapping
from data_manager.insee_general.source import SOURCE_EPCI

from api_diago.resources.common.db_request import db_request

from flask_restful import Resource

from api_diago.resources.common.log_message import message_request
from api_diago.resources.common.schema_request import perimeter_request
from api_diago.resources.common.utilities import wkb_to_geojson


def get_work_flows(geo_codes):
    result = db_request(
        """ SELECT  f.CODGEO_home, c1.chflieu_lat, c1.chflieu_lon, cog1.LIBELLE, 
                    f.CODGEO_work, c2.chflieu_lat, c2.chflieu_lon, cog2.LIBELLE, 
                    f.TRANS, f.SEXE, f.CS1, f.TYPMR, f.flow, f.DIST
            FROM insee_flows_mobpro_distance AS f
            LEFT JOIN ign_commune_center AS c1 ON f.CODGEO_home = c1.geo_code
            LEFT JOIN insee_cog_communes AS cog1 ON f.CODGEO_home = cog1.COM
            LEFT JOIN ign_commune_center AS c2 ON f.CODGEO_work = c2.geo_code
            LEFT JOIN insee_cog_communes AS cog2 ON f.CODGEO_work = cog2.COM
            WHERE f.CODGEO_home IN :geo_codes
            AND f.year_data = :year_mobpro
        """,
        {
            "geo_codes": geo_codes,
            "year_mobpro": "2019",
        }
    )

    flows = pd.DataFrame(result, columns=["home_geo_code", "home_lat", "home_lon", "home_name",
                                          "work_geo_code", "work_lat", "work_lon", "work_name",
                                          "mode", "gender", "csp", "typmr", "flow", "distance"])
    mask_typmr_1 = flows["mode"] == "1"
    flows.loc[mask_typmr_1, "work_geo_code"] = flows.loc[mask_typmr_1, "home_geo_code"]
    flows.loc[mask_typmr_1, "work_lat"] = flows.loc[mask_typmr_1, "home_lat"]
    flows.loc[mask_typmr_1, "work_lon"] = flows.loc[mask_typmr_1, "home_lon"]
    flows.loc[mask_typmr_1, "work_name"] = flows.loc[mask_typmr_1, "home_name"]

    flows = flows.groupby(by=[e for e in flows.columns if e not in ["flow", "dist"]], as_index=False).agg(**{
        "flow": pd.NamedAgg(column="flow", aggfunc="sum"),
        "distance": pd.NamedAgg(column="distance", aggfunc="mean"),
    })

    flows["mesh"] = "com"
    flows_com = flows

    # ---------- EPCI
    result = db_request(
        """ SELECT  epci_h.EPCI, 
                    epci_w.EPCI, 
                    f.TRANS, f.SEXE, f.CS1, f.TYPMR, f.flow, f.DIST
            FROM insee_flows_mobpro_distance AS f
            LEFT JOIN insee_epci_communes AS epci_h ON f.CODGEO_home = epci_h.CODGEO
            LEFT JOIN insee_epci_communes AS epci_w ON f.CODGEO_work = epci_w.CODGEO
            WHERE epci_h.EPCI IN (
                SELECT epci2.EPCI
                FROM insee_epci_communes AS epci2
                WHERE epci2.CODGEO IN :geo_codes 
                AND epci2.year_data = :year_epci
              ) 
            AND f.year_data = :year_mobpro
        """,
        {
            "geo_codes": geo_codes,
            "year_mobpro": "2019",
            "year_epci": SOURCE_EPCI
        }
    )
    flows = pd.DataFrame(result, columns=["home_geo_code",
                                          "work_geo_code",
                                          "mode", "gender", "csp", "typmr", "flow", "distance"])
    result = db_request(
        """ SELECT epci.EPCI, epci.LIBEPCI, ign_epci.outline
            FROM insee_epci AS epci
            LEFT JOIN ign_epci_outline AS ign_epci ON epci.EPCI = ign_epci.epci_siren
        """,
        {}
    )
    epcis = pd.DataFrame(result, columns=["code",
                                          "name",
                                          "outline"]).dropna()

    concerned_epcis = list(set(flows["home_geo_code"].to_list() + flows["work_geo_code"].to_list()))
    epcis = epcis[epcis["code"].isin(concerned_epcis)]

    epcis["outline"] = [wkb_to_geojson(outline) for outline in epcis["outline"]]
    epcis["center"] = [list(reversed(shape(outline).centroid.coords[0])) for outline in epcis["outline"]]
    epcis.drop(columns=["outline"], inplace=True)
    epcis.dropna(inplace=True)

    flows = pd.merge(flows, epcis, left_on="home_geo_code", right_on="code", how="inner")
    flows = pd.merge(flows, epcis, left_on="work_geo_code", right_on="code", how="inner", suffixes=(None, "_work"))

    flows.drop(columns=["code", "code_work"], inplace=True)
    flows.rename(columns={
        "center": "home_center", "name": "home_name",
        "center_work": "work_center", "name_work": "work_name"
    }, inplace=True)

    flows["home_lat"] = [c[0] for c in flows["home_center"]]
    flows["home_lon"] = [c[1] for c in flows["home_center"]]
    flows["work_lat"] = [c[0] for c in flows["work_center"]]
    flows["work_lon"] = [c[1] for c in flows["work_center"]]
    flows.drop(columns=["home_center", "work_center"], inplace=True)

    def compute_grouped(group):
        return pd.Series({
            "flow": group["flow"].sum(),
            "distance": (group["flow"] * group["distance"]).sum() / group["flow"].sum(),
        })
    flows = flows.groupby(by=[e for e in flows.columns if e not in ["flow", "distance"]], as_index=False).apply(compute_grouped)

    flows["mesh"] = "epci"
    flows_epci = flows

    flows = pd.concat([flows_com, flows_epci])

    flows = flows.replace({np.nan: None})

    flows["gender"] = flows["gender"].replace({"1": "m", "2": "f"})
    flows["typmr"] = flows["typmr"].replace({
        "11": "1",
        "12": "1",
        "31": "2",
        "32": "2",
        "42": "3",
        "43": "3",
        "41": "4",
        "ZZ": "5",
        "20": "5",
        "44": "5",
    })

    return {
        "work_flows": flows.to_dict(orient="list")
    }


class WorkFlows(Resource):
    def post(self):
        perimeter = perimeter_request.parse()
        geo_codes = perimeter.geo_codes

        message_request("work flows", geo_codes)
        return get_work_flows(geo_codes)


if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 4000)

    cc_haut_lignon = ["43069", "43244", "43129", "43199", "43130", "43051"]
    cc_chamonix_mt = ["74290", "74056", "74143", "74266"]
    cc_rives_haut_allier = ["43006", "43009", "43011", "43015", "43027", "43031", "43044", "43054", "43056", "43060",
                            "43063", "43065", "43067", "43068", "43070", "43075", "43079", "43082", "43083", "43085",
                            "43086", "43090", "43094", "43104", "43106", "43107", "43029", "43072", "43112", "43118",
                            "43131", "43132", "43133", "43139", "43148", "43149", "43151", "43155", "43232", "43234",
                            "43239", "43167", "43169", "43171", "43175", "43178", "43188", "43202", "43214", "43219",
                            "43222", "43183", "43208", "43242", "43245", "43250", "43252", "43256", "43264", "43013"]
    ca_puy_en_velay = ["43002", "43003", "43010", "43018", "43021", "43023", "43026", "43030", "43032", "43035",
                       "43036", "43039", "43041", "43043", "43045", "43046", "43048", "43049", "43057", "43059",
                       "43061", "43062", "43071", "43073", "43076", "43078", "43080", "43084", "43089", "43093",
                       "43095", "43108", "43116", "43119", "43122", "43124", "43126", "43128", "43134", "43136",
                       "43138", "43140", "43150", "43152", "43157", "43164", "43165", "43174", "43181", "43187",
                       "43189", "43190", "43194", "43196", "43197", "43201", "43216", "43217", "43220", "43221",
                       "43228", "43229", "43230", "43233", "43237", "43241", "43251", "43254", "43257", "43259",
                       "43260", "43267"]
    flows = get_work_flows(ca_puy_en_velay)
