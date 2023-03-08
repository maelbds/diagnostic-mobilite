import pandas as pd


def dataset_txt_to_df(dataset_name):
    parser = pd.read_csv("data/" + dataset_name + "/datasets/txt/parser.csv",
                         usecols=["file", "position", "width", "name"], sep=";")
    parser = parser.dropna().astype({"position": "int", "width": "int"})

    dataset_dict = {}

    for file in ["persons", "households", "travels", "travels_parts"]:
        file_mask = parser["file"] == file
        colspecs = [(pos-1, pos-1+width) for pos, width in zip(parser[file_mask]["position"], parser[file_mask]["width"])]
        print(colspecs)
        txt_file = pd.read_fwf("data/" + dataset_name + "/datasets/txt/" + file + ".txt",
                               colspecs=colspecs, names=parser[file_mask]["name"], dtype=str)
        dataset_dict[file] = txt_file
        print(txt_file)

    return dataset_dict


def save_df_to_csv(dataset_dict, dataset_name):
    for name, df in dataset_dict.items():
        df.to_csv("data/" + dataset_name + "/datasets/" + name + ".csv", sep=";", index=False, float_format='%.12g')
    print(dataset_name + " saved")


if __name__ == '__main__':
    pd.set_option('display.max_columns', 65)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)
    dataset = dataset_txt_to_df("montpellier")
    #save_df_to_csv(dataset, "montpellier")
