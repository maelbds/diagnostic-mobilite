import requests
import zipfile
import os
import py7zr


def download_url(url, save_path, chunk_size=128):
    """
    Download File from URL and save it to given save_path
    :param url: (String) URL where to download ZIP file
    :param save_path: (String) Path to save the downloaded path
    :param chunk_size:
    :return:
    """
    r = requests.get(url, stream=True)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, 'w+b') as fd:
        for chunk in r.iter_content(chunk_size=chunk_size):
            fd.write(chunk)


def unzip(zip_path, to_directory):
    """
    Unzip the ZIP filename to directory
    :return:
    """
    zip = zipfile.ZipFile(zip_path, 'r')
    file_paths = [f"{to_directory}/{name}" for name in zip.namelist()]
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(to_directory)

    return file_paths


def unzip7z(zip_path, to_directory):
    """
    Unzip the ZIP filename to directory
    :return:
    """
    try:
        zip = py7zr.SevenZipFile(zip_path, mode='r')
        file_paths = [f"{to_directory}/{name}" for name in zip.getnames()]
        with py7zr.SevenZipFile(zip_path, mode='r') as z:
            z.extractall(to_directory)
    except py7zr.Bad7zFile:
        print(f"{zip_path} - Bad 7z File")
    except FileNotFoundError as e:
        print(f"{zip_path} - not found")
    return file_paths


def load_file(name, url, dir, zip_name, file_name):
    file_path = f"{dir}/{file_name}"
    if not os.path.isfile(file_path):
        zip_path = f"{dir}/{zip_name}"
        print(f"{name} - downloading")
        # 1 - download ZIP GTFS file
        download_url(url, zip_path)
        # 2 - unzip ZIP
        try:
            unzip_paths = unzip(zip_path, dir)
            #print(unzip_paths)
        except zipfile.BadZipFile:
            unzip_paths = []
            print("This dataset is not a zip file.")
        except FileNotFoundError as e:
            print(f"zip at {zip_path} doesn't exist")
        # 3 - delete ZIP file
        try:
            os.remove(zip_path)
        except FileNotFoundError as e:
            print(f"zip at {zip_path} doesn't exist")
    else:
        print(f"{name} - already downloaded")


def load_file_ign(name, url, dir, zip_name, file_name):
    file_path = f"{dir}/{file_name}"
    if not os.path.isfile(file_path):
        zip_path = f"{dir}/{zip_name}"
        print(f"{name} - downloading")
        # 1 - download ZIP GTFS file
        download_url(url, zip_path)
        # 2 - unzip ZIP
        unzip_paths = unzip7z(zip_path, dir)
        #print(unzip_paths)
        # 3 - delete ZIP file
        try:
            os.remove(zip_path)
        except FileNotFoundError as e:
            print(f"zip at {zip_path} doesn't exist")
    else:
        print(f"{name} - already downloaded")


def load_file_gridded_pop(name, url, dir, zip_name1, zip_name2, file_name):
    file_path = f"{dir}/{file_name}"
    if not os.path.isfile(file_path):
        zip_path = f"{dir}/{zip_name1}"
        zip_path2 = f"{dir}/{zip_name2}"
        print(f"{name} - downloading")
        # 1 - download ZIP GTFS file
        download_url(url, zip_path)
        # 2 - unzip ZIP
        try:
            unzip_paths = unzip(zip_path, dir)
            unzip_paths = unzip7z(zip_path2, dir)
            #print(unzip_paths)
        except zipfile.BadZipFile:
            unzip_paths = []
            print("This dataset is not a zip file.")
        # 3 - delete ZIP file
        os.remove(zip_path)
        os.remove(zip_path2)
    else:
        print(f"{name} - already downloaded")