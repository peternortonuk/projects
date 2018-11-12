from requests import HTTPError
from gazprom.mt.pricing.interfaces.arc import get_forward_curve_history, \
    get_forward_curve, get_price_history
from gmt.foit.core import logger
from collections import namedtuple
import pandas as pd
import datetime as dt
import shelve
import os

file_name = 'flows_dict.db'
path_name = r'c:\temp'
pathfile = os.path.join(path_name, file_name)

input_data = namedtuple('input_data',
                        'arc_curve_name, arc_function, raw_data_df, indexer, clean_data_df')


def get_price_history_from_arc(name, env='PROD'):
    try:
        curve = get_price_history(name, attribution=False, env=env)
        return curve
    except HTTPError:
        logger.warning('HTTPError occurred for curve %s' % name)


def get_forward_curve_history_from_arc(name, env='PROD'):
    start_date = dt.date(2018, 11, 1)
    try:
        curve = get_forward_curve_history(name, start_date, env=env)
        return curve
    except HTTPError:
        logger.warning('HTTPError occurred for curve %s' % name)


def _iter_flow_indexer(df, offset=7):
    effective_date = df.columns[-1]
    ts = df.loc[:effective_date, effective_date]
    point_dates = ts.index
    for d in point_dates:
        try:
            # for every observation date, get a date in the past
            # because by then it should be a known, actual value
            ts = df.loc[d, :]
            yield ts.index[0], ts.values[0]
        except IndexError:
            pass


def _iter_price_indexer(df, offset=1):
    effective_dates = df.columns
    offset = dt.timedelta(days=offset)
    for d in effective_dates:
        try:
            # for every observation date, get all the curve
            ts = df.loc[d:, d]
            # select the first row
            row = ts.first(offset)
            # return date and value
            yield d, row.values[0]
        except IndexError:
            pass



def _get_indexed_value_from_arc_forward_curve_history(df, _iter_indexer):
    if not _iter_indexer:
        return df
    df = pd.DataFrame(_iter_indexer(df), columns=['obs_date', 'values'])
    df.set_index('obs_date', inplace=True)
    return df


flows_dict = {
    'NordStream': input_data('Russia Flow Forecast - Supply - Nord Stream', get_forward_curve_history_from_arc, None, _iter_flow_indexer, None),
    'VelkeKapusany': input_data('Russia Flow Forecast - Supply - Velke Kapusany', get_forward_curve_history_from_arc, None, _iter_flow_indexer, None),
    'Mallnow': input_data('Russia Flow Forecast - Supply - Mallnow', get_forward_curve_history_from_arc, None, _iter_flow_indexer, None),
    'MallnowReverse': input_data('Russia Flow Forecast - Supply - Mallnow Reverse', get_forward_curve_history_from_arc, None, _iter_flow_indexer, None),
    'Tarvisio': input_data('Russia Flow Forecast - Supply - Tarvisio', get_forward_curve_history_from_arc, None, _iter_flow_indexer, None),
    'TTF_MA1': input_data('G_ARGUS_TTF_M_MID.EUR', get_forward_curve_history_from_arc, None, _iter_price_indexer, None),
    'PSV_DA': input_data('G_ARGUS_PSV_DA_MID.EUR', get_price_history_from_arc, None, None, None),
}


def load_curves_from_arc(flows_dict):
    for k, v in flows_dict.items():
        # get the raw data
        raw_data_df = v.arc_function(v.arc_curve_name)
        raw_data_df.dropna(inplace=True)
        # clean it
        clean_data_df = _get_indexed_value_from_arc_forward_curve_history(raw_data_df, v.indexer)
        # update the dict
        flows_dict[k] = input_data(v.arc_curve_name, v.arc_function, raw_data_df, v.indexer, clean_data_df)
    return flows_dict


def save_curves_to_local(flows_dict):
    d = shelve.open(pathfile)
    for k, v in flows_dict.items():
        d[k] = v
    d.close()


def load_curves_from_local():
    return shelve.open(pathfile)


if __name__ == '__main__':
    effectivedate = dt.date.today()
    refresh = True

    shelf = load_curves_from_local()
    if refresh or len(shelf) == 0:
        flows_dict = load_curves_from_arc(flows_dict)
        save_curves_to_local(flows_dict)
    else:
        flows_dict = shelf

    import pdb; pdb.set_trace()
