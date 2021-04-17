"""
using this data
https://data.police.uk/data/
"""

import zipfile
import pandas as pd
import os

from crime.constants import data_folder_name, all_raw_pkl_file_name, FALLS_WITHIN, filter_falls_within


def extract_from_zip(data_folder_name, zip_file_name):
    zip_filepath_name = os.path.join(data_folder_name, zip_file_name)
    with zipfile.ZipFile(zip_filepath_name, 'r') as zip_ref:
        zip_ref.extractall(data_folder_name)


def read_all_csv_to_df(data_folder_name):
    dfs = []
    for root, dirs, files in os.walk(data_folder_name):
        filepaths = [os.path.join(root, filename) for filename in files
                     if filename.endswith('csv')]
        if filepaths:
            # concat all csvs in a folder
            df = pd.concat(map(pd.read_csv, filepaths))
            dfs.append(df)
    # concat all dfs in the list
    return pd.concat(dfs, axis='rows')


def save_df_to_pickle(df, filename):
    df.to_pickle(os.path.join(data_folder_name, filename))


def read_df_from_pickle(filename):
    return pd.read_pickle(os.path.join(data_folder_name, filename))


if __name__ == '__main__':
    if False:
        extract_from_zip(data_folder_name, zip_file_name)
        df = read_all_csv_to_df(data_folder_name)
        save_giant_df_to_pickle(df, all_raw_pkl_file_name)

    if True:
        df = read_giant_df_from_pickle(all_raw_pkl_file_name)
        mask = df[FALLS_WITHIN] == filter_falls_within
        df = df[mask]

