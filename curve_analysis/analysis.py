# import the DAO and connect to the database
import pandas as pd
import numpy as np
from collections import deque, OrderedDict
from gmt.curvelab.dao import CurveLabDAO, CurvePublishLogDocument
from gmt.orc.run_config_dao import ConfigTemplateDAO, CurveLabDefDocument
from gmt.db import endur
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter


# create connection
CurveLabDAO(env='prod')

# query the data returning the full document each time
results = CurvePublishLogDocument.objects(commodities='gas').order_by('-_id').limit(3)

# create a dictionary of curves indexed by timestamps
data_dict = {result.updated_datetime: result.curves_df for result in results}


# create collection of dataframes with multiindex columns
dfs_curve = []
dfs_spot = {}
for timestamp, curves_df in data_dict.items():
    # define a multiindex
    timestamps = [timestamp]
    markets = curves_df.columns
    columns = pd.MultiIndex.from_product([timestamps, markets], names=['timestamps', 'markets'])
    curves_df = pd.DataFrame(curves_df.values, index=curves_df.index, columns=columns)
    dfs_curve.append(curves_df)

# concatenate dataframes horizontally
df_all = pd.concat(dfs_curve, axis=1)

# filter criteria
markets_subset = [u'NBP', u'ZEE', u'ZTP', u'TTF', u'GPL', u'NCG', u'PSV']
markets_subset = [u'NBP', u'ZEE', u'TTF', u'NCG']
root_location = 'NBP'
All = slice(None)
latest_publication = max(data_dict.keys())
markets = markets_subset


def reorder_for_filtering(df, markets):
    # sort columns; this breaks geographical location order
    return df.T.sort_index(level=('timestamps', markets)).T


def reorder_by_geographical_location(df, markets, match=True, names=['timestamps', 'markets']):
    timestamps = list(set(df.columns.get_level_values(level='timestamps')))
    timestamps.sort()
    tt = [(timestamp, market) for timestamp in timestamps for market in markets]
    index = pd.MultiIndex.from_tuples(tt, names=names)
    if match:
        return df.T.loc[index].T
    else:
        return pd.DataFrame(data=df.values, index=df.index, columns=index)


def get_flat_df_from_2d_multi(df, single_index_number, multi_index_number):
    single_index = list(set(df.columns.get_level_values(single_index_number)))
    assert len(single_index) == 1
    multi_index = df.columns.get_level_values(multi_index_number)
    df.columns = multi_index
    return single_index, df


def format_weekday_time(lst):
    return [x.strftime('%a %H:%M:%S') for x in lst]


def format_weekday_day_month(lst):
    return [x.strftime('%a %d-%b') for x in lst]


def format_weekday_day_month_str(x, pos):
    return '%a %d-%b' % x


def highlight_latest_publication(lines):
    line = lines[-1]
    line.set_linewidth(2)
    line.set_color('black')


def add_subplots(fig, subplot_cols, subplot_rows=1):
    axes = {}
    for col in range(subplot_cols):
        axes[col] = fig.add_subplot(subplot_rows, subplot_cols, col + 1)
    return fig, axes


# create figures and axes
fig1 = Figure(figsize=(16, 12))
fig2 = Figure(figsize=(16, 12))
FigureCanvas(fig1)
FigureCanvas(fig2)
fig1, axes1 = add_subplots(fig=fig1, subplot_cols=4)
fig2, axes2 = add_subplots(fig=fig2, subplot_cols=4)


# reorder column index
df_all = reorder_for_filtering(df_all, 'markets')

# create filtered dataframes; filtering requires columns to be sorted
df_all = df_all.loc[All, (All, markets)]
df_location = df_all.loc[All, (All, root_location)]
df_publication = df_all.loc[All, (latest_publication, All)]

# flatten the dfs
location, df_location = get_flat_df_from_2d_multi(df_location, 1, 0)
timestamp, df_publication = get_flat_df_from_2d_multi(df_publication, 0, 1)

# reorder column index
df_all = reorder_by_geographical_location(df_all, markets)

# ================================================================
# ================================================================
# use df having a single location and all publication dates

# plot the raw data
lines = {}
lines[0] = axes1[0].plot(df_location.index, df_location.values)
highlight_latest_publication(lines[0])
legend_array = format_weekday_time(df_location.columns)
axes1[0].legend(legend_array)
axes1[0].set_title('Curve')



# calc time shift along axis of curve
diff = df_location - df_location.shift(periods=1, axis='rows')
mask = (diff == 0).all(axis=1)
df_diff_latest = diff[~mask]

# plot timeshifted diff
lines[1] = axes1[1].plot(df_diff_latest.index, df_diff_latest.values)
highlight_latest_publication(lines[1])
axes1[1].set_title('Differential along curve time')



# calc standard deviation across axis
df_std = df_location.std(axis=1)

# plot standard deviation
lines[2] = axes1[2].plot(df_std.index, df_std.values)
axes1[2].set_title('StDev across publish time')



# location of maximum
loc = df_std.idxmax()
# boolean of matches
mask = loc == df_std.index
# find index
iloc = np.where(mask)[0][0]
# define range of index to provide focussed chart
range_ = 10
df_focus = df_location.iloc[max(iloc - range_, 0):min(iloc + range_, df_location.shape[0])]

# plot focussed original data
lines[3] = axes1[3].plot(df_focus.index, df_focus.values)
highlight_latest_publication(lines[3])
legend_array = format_weekday_time(df_focus.columns)
axes1[3].legend(legend_array)
axes1[3].set_title('Focussed curve chart')

# get and set the tick labels
fig1.canvas.draw()
xlabels = axes1[3].get_xticklabels()
axes1[3].set_xticklabels(xlabels, rotation=90.0)

# formatter = FuncFormatter(format_weekday_day_month_str)
# axes1[3].xaxis.set_major_formatter(formatter)

fig1.savefig('foo')
# ================================





# ================================================================
# ================================================================
# many locations for all publications

# normalise NBP & ZEE to effective eur/mwh
# need to sort in order to filter
df_all = reorder_for_filtering(df_all, 'markets')
# first point date and all publication dates
ZEE = df_all.loc[All, (All, 'ZEE')].iloc[0]
TTF = df_all.loc[All, (All, 'TTF')].iloc[0]
# remove the markets index level
ZEE.index = ZEE.index.get_level_values(level='timestamps')
TTF.index = TTF.index.get_level_values(level='timestamps')
# calculate ratio as a series with timestamp as the index
norm = TTF/ZEE
# transpose to a dataframe having one row; and timestamps as columns
norm = norm.to_frame().T
# extend vertically to same size as df
norm = norm.reindex(df_all.index, method='ffill')
# finally, normalise the p/therm locations
df_all.loc[All, (All, ['NBP', 'ZEE'])] = df_all.loc[All, (All, ['NBP', 'ZEE'])] * norm
# filter for the latest publication
df_publication = df_all.loc[All, (latest_publication, All)]
# and sort again to return to geographical order
df_all = reorder_by_geographical_location(df_all, markets)
df_publication = reorder_by_geographical_location(df_publication, markets)


lines = {}
# plot the raw data
lines[0] = axes2[0].plot(df_publication.index, df_publication.values)
axes2[0].legend(df_publication.columns.get_level_values(level='markets'))
axes2[0].set_title('Curve')

# calc location shift for all publications
# pandas can't shift column multiindex so transpose and shift row multiindex
df_all_shifted = df_all.T.groupby(level='timestamps').shift(periods=1, axis='rows').T
df_diff_all = df_all - df_all_shifted
df_diff_all.dropna(axis='columns', how='all', inplace=True)


# build new column names that describe the basis
basis_list = [pair[0]+'-'+pair[1] for pair in zip(markets[1:], markets[:-1])]
df_diff_all = reorder_by_geographical_location(df_diff_all, basis_list, match=False, names=['timestamps', 'basis'])

# need to sort in order to filter
df_diff_all = reorder_for_filtering(df_diff_all, 'basis')
# basis for just the latest publication
df_diff_latest = df_diff_all.loc[All, (latest_publication, All)]
# and sort again to return to geographical order
df_diff_latest = reorder_by_geographical_location(df_diff_latest, basis_list)

# plot location shifted diff
lines[1] = axes2[1].plot(df_diff_latest.index, df_diff_latest.values)
axes2[1].set_title('Location spreads for latest publication')
axes2[1].legend(basis_list)

# calc standard deviation across axis
df_std = df_diff_all.T.groupby(level='timestamps').std().T

# plot standard deviation
lines[2] = axes2[2].plot(df_std.index, df_std.values)
axes2[2].set_title('StDev across publish time per location spread')

# location of maximum
max = df_std.max().max()
# boolean of matches
mask = df_std.values == max
# earliest point of maximum
idx = df_std[mask].index.min()
# dataframe to plot
df_focus = df_all.loc[idx, All]
# unstack pivot last column of multiindex
df_focus = df_focus.unstack(-1)

# plot focussed original data
lines[3] = axes2[3].plot(df_focus.index, df_focus.values)
axes2[3].legend(df_focus.columns)
axes2[3].set_title('Curve evolution')
axes2[3].text(1, 1, idx.strftime("%d-%b-%y"))

fig2.canvas.draw()
xlabels = axes2[3].get_xticklabels()
#xlabels = format_weekday_time(xlabels)
axes2[3].set_xticklabels(xlabels, rotation=90.0)

fig2.savefig('bar')
import pdb; pdb.set_trace()
pass

