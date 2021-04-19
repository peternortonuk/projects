"""
this module filters the police data and builds the url

"""
import pandas as pd
import seaborn as sns
from urllib.parse import quote
import urllib.parse
import webbrowser
from enum import Enum, auto
from datetime import datetime
import os

from crime.get_data import read_df_from_pickle, save_df_to_pickle
from crime.constants import all_raw_pkl_file_name, subset_raw_pkl_file_name, raw_url, \
    MONTH, LONGITUDE, LATITUDE, CRIME_TYPE, FALLS_WITHIN, COLOR
from crime.create_map import map_dict, key_dict, latitude, longitude
from crime.html_template import html_header, html_template_body, html_footer

# ======================================================================================================================
# setup


class RunType(Enum):
    SUBSET = auto()
    REFRESH = auto()


selected_columns = [MONTH, LONGITUDE, LATITUDE, CRIME_TYPE]

# ======================================================================================================================
# user selection

filter_falls_within = 'Thames Valley Police'
filter_month = '2020-11-01'
filter_month = datetime.strptime(filter_month, '%Y-%m-%d')
delta = 0.05  # filter the area around the map centre

# either refresh and filter the full dataset (REFRESH) or use the saved subset (SUBSET)
data_selection = RunType.SUBSET

# ======================================================================================================================
# function definitions


def get_date_from_string(df):
    df[MONTH] = pd.to_datetime(df[MONTH], format='%Y-%m')


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

    if data_selection == RunType.REFRESH:
        df = read_df_from_pickle(all_raw_pkl_file_name)

        # report period is expressed as string in the form yyyy-mm; convert to date
        get_date_from_string(df)

        # filter for the required geographical area
        mask = df[FALLS_WITHIN] == filter_falls_within
        df = df[mask]

        # exclude rows that have any nan values in important columns
        mask = df[selected_columns].isnull().any(axis='columns')
        df = df[~mask]

        # filter for months
        month = pd.to_datetime(filter_month)
        mask = df[MONTH] == month
        df = df[mask]

        # filter for area
        condition1 = df[LATITUDE].between(latitude-delta, latitude+delta)
        condition2 = df[LONGITUDE].between(longitude-delta, longitude+delta)
        mask = condition1 & condition2
        df = df[mask]

        # save it
        save_df_to_pickle(df, subset_raw_pkl_file_name)

    elif data_selection == RunType.SUBSET:
        df = read_df_from_pickle(subset_raw_pkl_file_name)

    else:
        raise NotImplementedError

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
    html = ''
    for crime_type in df_marker.index:

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

        # create the body html
        pagedict = {'filter_month': filter_month.strftime('%b-%Y'),
                    'crime_type': crime_type,
                    'url': url}
        html = html + html_template_body.format(**pagedict)

    # create a html file, write to it and close it
    f = open('madness.html', 'w')
    f.write(html_header + html + html_footer)
    f.close()
    filename = 'file:///'+os.getcwd()+'/' + 'madness.html'

    # open the html file in a browser
    webbrowser.open_new_tab(filename)
