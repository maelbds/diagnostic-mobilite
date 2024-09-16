import pandas as pd

from data_manager.emd.read_emd_datasets import read_emd_dataset
from data_manager.emd.read_emd_geo import read_emd_geo_geojson


def read_emd_montpellier(pool):
    emd_id = "montpellier"
    emd_name = "Enquête Déplacements Grand Territoire (EDGT) de l’Aire Métropolitaine de Montpellier (2013-2014)"
    emd_link = "https://data.montpellier3m.fr/dataset/enquete-menages-deplacements-archive"
    emd_year = "2014"

    dataset = pd.DataFrame({
        "emd_id": emd_id,
        "emd_name": emd_name,
        "emd_link": emd_link,
        "emd_year": emd_year,
    }, index=[0])

    persons, travels, modes_dict, reasons_dict = read_emd_dataset(emd_id)

    geo = read_emd_geo_geojson(emd_id)

    return emd_id, dataset, persons, travels, modes_dict, reasons_dict, geo


if __name__ == '__main__':
    pd.set_option('display.max_columns', 65)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)
    read_emd_montpellier(None)

