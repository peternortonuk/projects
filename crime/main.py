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
from crime.create_map import map_params, key_params
import seaborn as sns
from urllib.parse import quote
import webbrowser


all_columns = ['Crime ID', 'Month', 'Reported by', 'Falls within', 'Longitude',
               'Latitude', 'Location', 'LSOA code', 'LSOA name', 'Crime type',
               'Last outcome category', 'Context']

selected_columns = ['Month', 'Longitude', 'Latitude', 'Crime type']


def get_date_from_string(df):
    df['Month'] = pd.to_datetime(df['Month'], format='%Y-%m')


def add_color_for_column(df, col):
    unique_vals = df[col].unique()
    palette = sns.color_palette(None, len(unique_vals)).as_hex()
    zz = zip(unique_vals, palette)
    value_to_color_dict = dict(zz)
    df[COLOR] = df.apply(lambda x: value_to_color_dict[x[col]], axis='columns')


def build_string_for_row(row):
    return f'markers=color:{row.Color}|{row.Latitude},{row.Longitude}'


if __name__ == '__main__':
    # get all the data
    df = read_giant_df_from_pickle(all_raw_pkl_file_name)

    # select the required geographical area
    mask = df[FALLS_WITHIN] == filter_falls_within
    df = df[mask]

    # report period is expressed as string in the form yyyy-mm; convert to date
    get_date_from_string(df)

    # exclude rows that have any nan values in important columns
    mask = df[selected_columns].isnull().any(axis='columns')
    df = df[~mask]

    # filter to manage size of url
    month = pd.to_datetime('2020-11-1')
    mask = df['Month'] == month
    df = df[mask]
    df = df[:5]

    # add a colour based on unique values of a column
    add_color_for_column(df, CRIME_TYPE)

    # build a string for each data point
    df['string'] = df.apply(build_string_for_row, axis=1)
    all_strings = '&'.join(df['string'].values)
    all_strings = quote(all_strings)

    url = raw_url + '?' + map_params + '&' + all_strings + '&' + key_params
    webbrowser.open(url)
    pass

