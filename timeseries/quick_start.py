from tsfresh.examples.robot_execution_failures import download_robot_execution_failures, \
    load_robot_execution_failures
from tsfresh import extract_features
from tsfresh import select_features
from tsfresh.utilities.dataframe_functions import impute
from multiprocessing import Process, freeze_support

import matplotlib.pyplot as plt


def main():

    # download and load the data
    download_robot_execution_failures()
    timeseries, y = load_robot_execution_failures()

    # plot healthy example
    timeseries[timeseries['id'] == 3].plot(subplots=True, sharex=True, figsize=(10,10))
    plt.show()

    # plot failure example
    timeseries[timeseries['id'] == 21].plot(subplots=True, sharex=True, figsize=(10,10))
    plt.show()

    # extract features
    extracted_features = extract_features(timeseries, column_id="id", column_sort="time")
    print('shape of extracted features: {},{}'.format(*extracted_features.shape))

    # fill NaNs based on rules
    impute(extracted_features)

    # filter for significant features
    features_filtered = select_features(extracted_features, y)
    print('shape of selected features: {},{}'.format(*features_filtered.shape))


if __name__ == '__main__':
    freeze_support()
    main()