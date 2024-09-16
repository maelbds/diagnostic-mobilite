import requests



# service WFS : sélection d'objets vectoriels de la BD TOPO ou autres
# voir les filtres possibles ici (Filter_Capabilities) : https://data.geopf.fr/wfs/ows?SERVICE=WFS&VERSION=2.0.0&REQUEST=GetCapabilities
# doc ici : https://enterprise.arcgis.com/fr/server/latest/publish-services/windows/communicating-with-a-wfs-service-in-a-web-browser.htm
# et là https://geoservices.ign.fr/documentation/services/services-geoplateforme/diffusion#70070


test_region_nouvelle_aquitaine = "https://data.geopf.fr/wfs/ows?SERVICE=WFS&REQUEST=GetFeature&VERSION=2.0.0&typeName=BDTOPO_V3:region&OUTPUTFORMAT=json&FILTER=%3Cogc:Filter%20xmlns:ogc=%27http://www.opengis.net/ogc%27%3E%3Cogc:PropertyIsEqualTo%3E%3Cogc:PropertyName%3Ecode_insee%3C/ogc:PropertyName%3E%3Cogc:Literal%3E75%3C/ogc:Literal%3E%3C/ogc:PropertyIsEqualTo%3E%3C/ogc:Filter%3E"

parameters = {
    "SERVICE": "WFS",
    "REQUEST": "GetFeature",
    "VERSION": "2.0.0",
    "OUTPUTFORMAT": "json",
    "typeName": "BDTOPO_V3:route_numerotee_ou_nommee",
    "FILTER": """<ogc:Filter xmlns:ogc='http://www.opengis.net/ogc'>
                    <ogc:PropertyIsEqualTo>
                      <ogc:PropertyName>code_insee</ogc:PropertyName>
                      <ogc:Literal>79048</ogc:Literal>
                    </ogc:PropertyIsEqualTo>
                </ogc:Filter>"""
}

e = requests.get("https://data.geopf.fr/wfs/ows?" + "&".join([f"{key}={value}" for key, value in parameters.items()]))

print(e)
print(e.content)