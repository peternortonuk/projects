"""
examples:

https://maps.googleapis.com/maps/api/staticmap?center=Berkeley,CA&zoom=14&size=400x400&key=YOUR_API_KEY

https://maps.googleapis.com/maps/api/staticmap?center=63.259591,-144.667969&zoom=6&size=400x400
&markers=color:blue%7Clabel:S%7C62.107733,-145.541936&markers=size:tiny%7Ccolor:green%7CDelta+Junction,AK
&markers=size:mid%7Ccolor:0xFFFF00%7Clabel:C%7CTok,AK"&key=YOUR_API_KEY

https://maps.googleapis.com/maps/api/staticmap?center=Oxford%2CUK&zoom=13&size=600x600&maptype=roadmap
&markers=color:red%7C51.7520,-1.2577
&key=AIzaSyCq7HOPVyJf8dVGFqOjqNaffgFzoUujzto

"""
import pandas as pd
from crime.get_data import read_df_from_pickle, save_df_to_pickle
from crime.constants import all_raw_pkl_file_name, subset_raw_pkl_file_name, FALLS_WITHIN, filter_falls_within, raw_url, COLOR, CRIME_TYPE
from crime.create_map import map_dict, key_dict, latitude, longitude
import seaborn as sns
from urllib.parse import quote
import urllib.parse
import webbrowser


all_columns = ['Crime ID', 'Month', 'Reported by', 'Falls within', 'Longitude',
               'Latitude', 'Location', 'LSOA code', 'LSOA name', 'Crime type',
               'Last outcome category', 'Context']

selected_columns = ['Month', 'Longitude', 'Latitude', 'Crime type']


def get_date_from_string(df):
    df['Month'] = pd.to_datetime(df['Month'], format='%Y-%m')


def create_colors_for_items(items):
    palette = sns.color_palette(None, len(items)).as_hex()
    palette = ['0x'+ss[1:] for ss in palette]  # replace # with 0x
    zz = zip(items, palette)
    return dict(zz)


def build_string_for_location(row):
    return f'{row.Latitude},{row.Longitude}'


def build_string_for_marker(row):
    return f'markers=color:{row.Color}%7Csize:tiny'


if __name__ == '__main__':
    # get all the data
    data_selection = 'subset'

    if data_selection == 'all':
        df = read_df_from_pickle(all_raw_pkl_file_name)

        # filter for the required geographical area
        mask = df[FALLS_WITHIN] == filter_falls_within
        df = df[mask]

        # report period is expressed as string in the form yyyy-mm; convert to date
        get_date_from_string(df)

        # exclude rows that have any nan values in important columns
        mask = df[selected_columns].isnull().any(axis='columns')
        df = df[~mask]

        # filter for months
        month = pd.to_datetime('2020-11-1')
        mask = df['Month'] == month
        df = df[mask]

        # filter for area
        delta = 0.05
        condition1 = df['Latitude'].between(latitude-delta, latitude+delta)
        condition2 = df['Longitude'].between(longitude-delta, longitude+delta)
        mask = condition1 & condition2
        df = df[mask]

        # save it
        save_df_to_pickle(df, subset_raw_pkl_file_name)

    elif data_selection == 'subset':
        df = read_df_from_pickle(subset_raw_pkl_file_name)

    # ==================================================================================================================
    # the full-size df

    # create the url string for each data point
    df['string'] = df.apply(build_string_for_location, axis=1)

    # ==================================================================================================================
    # aggregate df for marker definition

    # get count of crimes per type and create df
    df_marker = df[CRIME_TYPE].value_counts().to_frame()

    # add a colour based on unique values of the index
    mapper = create_colors_for_items(df_marker.index)
    df_marker[COLOR] = df_marker.apply(lambda x: mapper[x.name], axis='columns')

    # create the url string
    df_marker['string'] = df_marker.apply(build_string_for_marker, axis=1)

    # ==================================================================================================================
    # top and tail the url

    map_params = urllib.parse.urlencode(map_dict)
    key_params = urllib.parse.urlencode(key_dict)

    # ==================================================================================================================
    # a subset df to deal with url size limit

    print(df_marker)
    print()
    crime_types = df_marker.index
    # crime_types = ['Burglary']
    for crime_type in crime_types:

        mask = df[CRIME_TYPE] == crime_type
        df_subset = df[mask]
        string_for_locations = '%7C'.join(df_subset['string'].values)

        # build string for marker
        mask = df_marker.index == crime_type
        string_for_marker = df_marker[mask]['string'].values[0]

        # the marker definition and all the locations
        big_string = string_for_marker + '%7C' + string_for_locations

        # connect it all together
        url = raw_url + '?' + map_params + '&' + big_string + '&' + key_params

        # check its not too big
        # https://developers.google.com/maps/documentation/maps-static/start#url-size-restriction
        assert len(url) <= 8192
        print(f'\n\n"{crime_type}"... has string length = {len(url)}')

        # and open the webpage
        input("Hit return...")
        webbrowser.open(url)

