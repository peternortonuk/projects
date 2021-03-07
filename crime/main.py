"""
examples:

https://maps.googleapis.com/maps/api/staticmap?center=Berkeley,CA&zoom=14&size=400x400&key=YOUR_API_KEY

https://maps.googleapis.com/maps/api/staticmap?center=63.259591,-144.667969&zoom=6&size=400x400
&markers=color:blue%7Clabel:S%7C62.107733,-145.541936&markers=size:tiny%7Ccolor:green%7CDelta+Junction,AK
&markers=size:mid%7Ccolor:0xFFFF00%7Clabel:C%7CTok,AK"&key=YOUR_API_KEY


"""
import pandas as pd
from crime.get_data import read_giant_df_from_pickle
from crime.constants import all_raw_pkl_file_name, FALLS_WITHIN, filter_falls_within, raw_url, COLOR, CRIME_TYPE
import seaborn as sns

all_columns = ['Crime ID', 'Month', 'Reported by', 'Falls within', 'Longitude',
               'Latitude', 'Location', 'LSOA code', 'LSOA name', 'Crime type',
               'Last outcome category', 'Context']

selected_columns = ['Month', 'Longitude', 'Latitude', 'Crime type']
selected_columns = selected_columns + [COLOR]


def get_parameters_from_df(df):
    df['Month'] = pd.to_datetime(df['Month'], format='%Y-%m')
    return df[selected_columns]


def add_color_for_column(df, col):
    unique_vals = df[col].unique()
    palette = sns.color_palette(None, len(unique_vals)).as_hex()
    zz = zip(unique_vals, palette)
    value_to_color_dict = dict(zz)
    df[COLOR] = df.apply(lambda x: value_to_color_dict[x[col]], axis='columns')
    return df


def build_params_for_month(df, month):
    mask = df['Month'] == month
    df = df[mask]
    df = df[:5]
    dd = {}
    for row in df.iterrows():
        pass
        # dd = markers=color:blue%7Clabel:S%7C62.107733
    return dd


if __name__ == '__main__':
    # get all the data
    df = read_giant_df_from_pickle(all_raw_pkl_file_name)

    # select the required geographical area
    mask = df[FALLS_WITHIN] == filter_falls_within
    df = df[mask]

    # add a colour based on unique values of a column
    df = add_color_for_column(df, CRIME_TYPE)

    # select columns required for url
    parameters_df = get_parameters_from_df(df)

    # exclude rows that have any nan values
    mask = parameters_df.isnull().any(axis='columns')
    parameters = parameters_df[~mask]

    # build a set of url parameters
    month = pd.to_datetime('2020-11-1')
    dd = build_params_for_month(parameters_df, month)
    pass

