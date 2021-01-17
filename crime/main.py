"""
examples:

https://maps.googleapis.com/maps/api/staticmap?center=Berkeley,CA&zoom=14&size=400x400&key=YOUR_API_KEY

https://maps.googleapis.com/maps/api/staticmap?center=63.259591,-144.667969&zoom=6&size=400x400
&markers=color:blue%7Clabel:S%7C62.107733,-145.541936&markers=size:tiny%7Ccolor:green%7CDelta+Junction,AK
&markers=size:mid%7Ccolor:0xFFFF00%7Clabel:C%7CTok,AK"&key=YOUR_API_KEY


"""

from crime.get_data import read_giant_df_from_pickle
from crime.constants import all_raw_pkl_file_name, FALLS_WITHIN, filter_falls_within, raw_url


def get_parameters_from_df(df):
    return []


def build_full_url(url, parameters):
    return url


if __name__ == '__main__':
    df = read_giant_df_from_pickle(all_raw_pkl_file_name)
    mask = df[FALLS_WITHIN] == filter_falls_within
    df = df[mask]
    parameters = get_parameters_from_df(df)
    url = build_full_url(raw_url, parameters)

