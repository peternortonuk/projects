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
                        'arc_curve_name, function, raw_data_df, clean_data_df')


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
        curve = _get_actual_flow_from_arc_forward_curve_history(curve, offset=7)
        return curve
    except HTTPError:
        logger.warning('HTTPError occurred for curve %s' % name)


def _get_actual_flow_from_arc_forward_curve_history(df, offset):
    obs_dates = df.columns
    def iter_price():
        for d in obs_dates:
            try:
                # for every observation date, get a date in the past
                # because by then it should be a known actual value
                yield (d, df.loc[:d, d].iloc[-offset])
            except IndexError:
                pass
    df = pd.DataFrame(iter_price(), columns=['obs_date', 'values'])
    df.set_index('obs_date', inplace=True)
    return df


flows_dict = {
    'NordStream': input_data('Russia Flow Forecast - Supply - Nord Stream', get_forward_curve_history_from_arc, None, None),
    'Velke Kapusany': input_data('Russia Flow Forecast - Supply - Velke Kapusany', get_forward_curve_history_from_arc, None, None),
    'Mallnow': input_data('Russia Flow Forecast - Supply - Mallnow', get_forward_curve_history_from_arc, None, None),
    'MallnowReverse': input_data('Russia Flow Forecast - Supply - Mallnow Reverse', get_forward_curve_history_from_arc, None, None),
    'Tarvisio': input_data('Russia Flow Forecast - Supply - Tarvisio', get_forward_curve_history_from_arc, None, None),
    'TTF_MA1': input_data('G_ARGUS_TTF_M_MID.EUR', get_forward_curve_history_from_arc, None, None),
    'PSV_DA': input_data('G_ARGUS_PSV_DA_MID.EUR', get_price_history_from_arc, None, None),
}


def load_curves_from_arc(flows_dict):
    for k, v in flows_dict.items():
        df = v.function(v.arc_curve_name)
        df.dropna(inplace=True)
        flows_dict[k] = input_data(v.function, v.arc_curve_name, df, None)
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
    refresh = False

    shelf = load_curves_from_local()
    if refresh or not shelf:
        flows_dict = load_curves_from_arc(flows_dict)
        save_curves_to_local(flows_dict)
    else:
        flows_dict = shelf

    import pdb; pdb.set_trace()
