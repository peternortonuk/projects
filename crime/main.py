"""
this module filters the police data and builds the url and then builds the html


https://developers.google.com/maps/documentation/maps-static/overview
http://www.compciv.org/guides/python/how-tos/creating-proper-url-query-strings/

"""
import pandas as pd
import seaborn as sns
from urllib.parse import quote
import urllib.parse
import webbrowser
from enum import Enum, auto
from datetime import datetime
import os
from collections import namedtuple

from crime.get_data import read_df_from_pickle, save_df_to_pickle
from crime.constants import all_raw_pkl_file_name, subset_raw_pkl_file_name, raw_url, \
    MONTH, LONGITUDE, LATITUDE, CRIME_TYPE, FALLS_WITHIN, COLOR
from crime.html_template import html_header, html_template_body, html_footer
from crime.credentials import api_key

# ======================================================================================================================
# setup


class RunType(Enum):
    SUBSET = auto()
    REFRESH = auto()

Location = namedtuple('Location', 'latitude, longitude')

selected_columns = [MONTH, LONGITUDE, LATITUDE, CRIME_TYPE]

# ======================================================================================================================
# user selection

# data
filter_falls_within = 'Thames Valley Police'
filter_month = '2020-11-01'
filter_month = datetime.strptime(filter_month, '%Y-%m-%d')

# Oxford,UK
centre = Location(latitude=51.7520, longitude=-1.2577)
delta = 0.05  # filter data for this area around the map centre

# map size
width = 600
height = 600
zoom = 12

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


def apply_filters(df, filter_falls_within, filter_month, centre, delta):
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
    condition1 = df[LATITUDE].between(centre.latitude-delta, centre.latitude+delta)
    condition2 = df[LONGITUDE].between(centre.longitude-delta, centre.longitude+delta)
    mask = condition1 & condition2
    df = df[mask]



def build_df_marker(df):
    # get count of crimes per type and create aggregate df
    df_marker = df[CRIME_TYPE].value_counts().to_frame()

    # add a colour based on unique values of the index
    mapper = create_colors_for_items(df_marker.index)
    df_marker[COLOR] = df_marker.apply(lambda x: mapper[x.name], axis='columns')

    # create the url string
    df_marker['string'] = df_marker.apply(build_string_for_marker, axis=1)
    return df_marker



def build_string_for_url(df, crime_type):
    # build string for location
    mask = df[CRIME_TYPE] == crime_type
    string_for_locations = '%7C'.join(df.loc[mask, 'string'].values)

    # build string for marker
    mask = df_marker.index == crime_type
    string_for_marker = df_marker.loc[mask, 'string'].values[0]

    # the marker definition and all the locations
    return string_for_marker + '%7C' + string_for_locations



if __name__ == '__main__':

    if data_selection == RunType.REFRESH:
        # read it
        df = read_df_from_pickle(all_raw_pkl_file_name)

        # clean and filter
        apply_filters(df, filter_falls_within, filter_month, centre, delta)

        # save the subset
        save_df_to_pickle(df, subset_raw_pkl_file_name)

    elif data_selection == RunType.SUBSET:
        # read the subset
        df = read_df_from_pickle(subset_raw_pkl_file_name)

    else:
        raise NotImplementedError

    # create the url string for each data point
    df['string'] = df.apply(build_string_for_location, axis=1)

    # create an aggregate df for the marker definition
    df_marker = build_df_marker(df)

    # top and tail the url
    map_dict = {'center': f'{centre.latitude},{centre.longitude}',
                'zoom': zoom,
                'size': f'{width}x{height}',
                'maptype': 'roadmap'}

    key_dict = {'key': api_key}

    map_params = urllib.parse.urlencode(map_dict)
    key_params = urllib.parse.urlencode(key_dict)

    # ==================================================================================================================
    # a subset df to deal with url size limit

    print(df_marker)
    print()
    html = ''
    for crime_type in df_marker.index:

        # build string for location
        big_string = build_string_for_url(df, crime_type)

        # connect it all together
        url = raw_url + '?' + map_params + '&' + big_string + '&' + key_params

        # check its not too big
        # https://developers.google.com/maps/documentation/maps-static/start#url-size-restriction
        print(f'\n\n"{crime_type}"... has string length = {len(url)}')
        if len(url) <= 8192:
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
