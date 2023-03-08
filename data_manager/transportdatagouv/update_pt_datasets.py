"""
This file enables to update the public transport datasets saved into database from transport.datagouv API
"""

import requests
import pprint
import pickle
import zipfile
import os
from datetime import date

from data_manager.database_connection.sql_connect import mariadb_connection
from data_manager.transportdatagouv.save_gtfs_to_db import save_gtfs_to_db

from data_manager.ign.save_data_from_shp_to_db_commune_outline import read_shp_outlines_to_shapely


def get_transportdatagouv_datasets():
    """
    Function to get all Transport.DataGouv datasets from API
    :return: (List) of datasets
    """
    r = requests.get("https://transport.data.gouv.fr/api/datasets",
                     headers={
                         "accept": "application/json",
                         "x-csrf-token": "dwIdICcXEEMUDSZ4bhkYIAMeIQAnLUhy4HOmlxb-XRH6ZcrWR3omhT-A"
                     }, )

    datasets = r.json()
    return datasets


def filter_datasets_pt(datasets, modes):
    """
    From all Transport.DataGouv datasets, filter those which are currently valid and give info about Public Transport
    :param modes: (List) of desired transport modes
    :param datasets: (List) of Transport.DataGouv datasets
    :return: (List) of GTFS public transport datasets currently valid
    """
    mode_datasets = []
    for d in datasets:
        try:
            for r in d["resources"]:
                try:
                    r_modes = r["metadata"]["modes"]
                    is_in_modes = any([m in r_modes for m in modes])
                    if is_in_modes and r["format"] == "GTFS":
                        r_id = r["datagouv_id"]
                        end_date = r["metadata"]["end_date"]
                        end_date = date.fromisoformat(end_date) if end_date is not None else date.today()
                        if date.today() <= end_date:
                            mode_datasets.append({
                                'url': r["original_url"],
                                'datagouv_id': r_id,
                                'name': d["title"],
                                'file_name': d["title"].replace(" ", "_").replace("/", "") + "-" + r_id[:8],
                                'end_calendar_validity': end_date
                            })
                except KeyError as e:
                    pass
        except KeyError:
            pass
    return mode_datasets


def download_url(url, save_path, chunk_size=128):
    """
    Download File from URL and save it to given save_path
    :param url: (String) URL where to download ZIP file
    :param save_path: (String) Path to save the downloaded path
    :param chunk_size:
    :return:
    """
    r = requests.get(url, stream=True)
    with open(save_path, 'w+b') as fd:
        for chunk in r.iter_content(chunk_size=chunk_size):
            fd.write(chunk)


def unzip(directory, filepath):
    """
    Unzip the ZIP filename stored into directory
    :param directory:
    :param filename:
    :return:
    """
    with zipfile.ZipFile(filepath, 'r') as zip_ref:
        zip_ref.extractall(directory)
    return


def get_pt_datasets_bdd():
    """
    Function to get all datasets saved into database
    :return:
    """
    conn = mariadb_connection()
    cur = conn.cursor()
    cur.execute("""SELECT datagouv_id, name, file_name 
                FROM datagouv_pt_datasets 
                """, [])
    result = list(cur)
    conn.close()
    return result


def save_pt_datasets_bdd(dataset):
    """
    Function to save a public transport dataset into database
    :param dataset:
    :return:
    """
    conn = mariadb_connection()
    cur = conn.cursor()
    cur.execute("""INSERT INTO datagouv_pt_datasets 
                        (datagouv_id,
                            name, 
                            file_name, 
                            url, 
                            end_calendar_validity, 
                            saved_on) VALUES (?,?,?,?,?,CURRENT_TIMESTAMP)""",
                [dataset["datagouv_id"],
                 dataset["name"],
                 dataset["file_name"],
                 dataset["url"],
                 dataset["end_calendar_validity"].isoformat()]
                )
    conn.commit()
    conn.close()
    print("Dataset " + dataset["name"] + " saved into database")
    return


def update_pt_datasets():
    """
    This function check all datasets from transport.datagouv and add the missing public transport datasets to database
    :return:
    """
    MODES = ["rail", "bus", "coach"]
    current_datasets = get_transportdatagouv_datasets()
    pt_datasets = filter_datasets_pt(current_datasets, MODES)

    saved_datasets = get_pt_datasets_bdd()

    saved_datasets_id = set([d[0] for d in saved_datasets])
    current_pt_datasets_id = set([d["datagouv_id"] for d in pt_datasets])

    missing_datasets_id = current_pt_datasets_id - saved_datasets_id
    missing_datasets = [d for d in pt_datasets if d["datagouv_id"] in missing_datasets_id]

    print(missing_datasets)

    communes_outline = read_shp_outlines_to_shapely()

    DIRECTORY = "pt"

    for d in missing_datasets:
        print(f'Load dataset {d["name"]}')
        filename = d["file_name"]
        filepath = DIRECTORY + "/" + filename + ".zip"
        # 1 - download ZIP GTFS file
        download_url(d["url"], filepath)
        # 2 - unzip ZIP
        try:
            unzip(DIRECTORY + "/" + filename, filepath)
        except zipfile.BadZipFile:
            print("This dataset is not a zip file.")
            d["file_name"] = None  # to handle bad file later during GTFS processing
        # 3 - delete unzipped ZIP file
        os.remove(filepath)
        # 4 - insert dataset into database
        save_pt_datasets_bdd(d)
        # 5 - handle GTFS and store txt files into database
        save_gtfs_to_db(DIRECTORY + "/" + filename, d["datagouv_id"], communes_outline)

    print("Update done")
    return


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    update_pt_datasets()
