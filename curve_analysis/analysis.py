# import the DAO and connect to the database
import pandas as pd
import numpy as np
from collections import deque
from gmt.curvelab.dao import CurveLabDAO, CurvePublishLogDocument
from gmt.orc.run_config_dao import ConfigTemplateDAO, CurveLabDefDocument
from gmt.db import endur
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure


# create connection
CurveLabDAO(env='prod')

# query the data returning the full document each time
results = CurvePublishLogDocument.objects.order_by('-_id').limit(5)

# create a dictionary of curves indexed by timestamps
data_dict = {result.updated_datetime: result.curves_df for result in results}

# create collection of dataframes with multiindex columns
dfs_curve = []
dfs_spot = {}
for timestamp, curves_df in data_dict.items():
    # define a multiindex
    timestamps = [timestamp]
    markets = curves_df.columns
    columns = pd.MultiIndex.from_product([timestamps, markets])
    curves_df = pd.DataFrame(curves_df.values, index=curves_df.index, columns=columns)
    dfs_curve.append(curves_df)

# # build spot fx data
# spot_fx = [i[1] for i in data_dict.values()]
# markets = [u'GBPUSD', u'EURGBP']
# timestamps = data_dict.keys()
# spot_df = pd.DataFrame(data=spot_fx, index=timestamps, columns=markets)

# concatenate dataframes horizontally
df_all = pd.concat(dfs_curve, axis=1)

# sort columns
df_all = df_all.T.sort_index().T

# filter the data
root_location = 'NBP'
latest_publication = max(data_dict.keys())
All = slice(None)

# create two distinct dataframes
df_location = df_all.loc[All, (All, root_location)]
df_publication = df_all.loc[All, (latest_publication, All)]


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

# flatten the dfs
location, df_location = get_flat_df_from_2d_multi(df_location, 1, 0)
timestamp, df_publication = get_flat_df_from_2d_multi(df_publication, 0, 1)


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
df_diff = diff[~mask]

# plot timeshifted diff
lines[1] = axes1[1].plot(df_diff.index, df_diff.values)
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

fig1.savefig('foo')
# ================================


# ================================================================
# ================================================================
# many locations for latest publication


# start by normalising NBP & ZEE to effective eur/mwh
NBP = df_publication.loc[All, 'NBP']
TTF = df_publication.loc[All, 'TTF']
norm = TTF/NBP
norm = norm.iloc[0]  # scalar spot fx value ie not the curve
df_publication.loc[:,['NBP', 'ZEE']] = df_publication.loc[:,['NBP', 'ZEE']] * norm

# filter a subset of columns
columns = [u'NBP', u'ZEE', u'ZTP', u'TTF', u'GPL', u'NCG', u'PSV']
df_publication = df_publication[columns]


lines = {}
# plot the raw data
lines[0] = axes2[0].plot(df_publication.index, df_publication.values)
axes2[0].legend(df_publication.columns)
axes2[0].set_title('Curve')


# calc location shift
df_diff = df_publication - df_publication.shift(periods=1, axis='columns')

# build new column names that describe the basis
columns = df_publication.columns
shifted = deque(columns)
shifted.rotate(1)
legend_array = zip(columns, shifted)
legend_array = [pair[0]+'-'+pair[1] for pair in legend_array[1:]]


# plot location shifted diff
lines[1] = axes2[1].plot(df_diff.index, df_diff.values)
axes2[1].set_title('Differential across locations')
axes2[1].legend(legend_array)

# calc standard deviation across axis
df_std = df_publication.std(axis=1)

# plot standard deviation
lines[2] = axes2[2].plot(df_std.index, df_std.values)
axes2[2].set_title('StDev across publish time')



# location of maximum
loc = df_std.idxmax()
# boolean of matches
mask = loc == df_std.index
# find index
iloc = np.where(mask)[0][0]
# define range of index to provide focussed chart
range = 10
df_focus = df_publication.iloc[max(iloc - range, 0):min(iloc + range, df_publication.shape[0])]

# plot focussed original data
lines[3] = axes1[3].plot(df_focus.index, df_focus.values)
axes1[3].legend(df_publication.columns)
axes1[3].set_title('Focussed curve chart')

fig2.canvas.draw()
xlabels = axes1[3].get_xticklabels()
axes1[3].set_xticklabels(xlabels, rotation=90.0)

fig2.savefig('bar')



import pdb; pdb.set_trace()
pass

