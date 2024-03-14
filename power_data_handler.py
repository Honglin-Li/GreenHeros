"""
Data Structure

8 CSV file
each contains the power consumption and CPU Utilization data of one server/cluster

"""
import pandas as pd
import os
import re
import altair as alt

WATT_METRICS = ['Average', 'Minimum', 'Peak', 'CpuWatts', 'DimmWatts']

def read_one_csv(csv_name):
    """
    Read one server power data

    :param csv_name: the name of a csv file
    :return: DataFrame
    """
    # read data while setting time as index
    # df = pd.read_csv(os.path.join('data', csv_name), index_col=[0])

    df = pd.read_csv(os.path.join('data', csv_name), encoding='ISO-8859-1')

    # change Watts to KWatts
    if df.shape[0] > 0:
        df[WATT_METRICS] = df[WATT_METRICS] / 1000

    return df


def read_csv_in_list():
    """
    Read 8 server power data into a list
    :return: List of DataFrame
    """
    list_df = []

    for csv_name in os.listdir('data'):
        df = read_one_csv(csv_name)
        if df.shape[0] > 0:
            list_df.append(df)

    return list_df


def get_overview_power_data(list_df):
    """
    Get overview data of all servers by minutes

    :param list_df: list of DataFrame
    :return: DataFrame
    """
    # processing each server power data df
    df_processed_list = []

    for df in list_df:
        # process data to MINUTE level
        df = df.copy()
        df['Time'] = df['Time'].str[:16]
        df = df.groupby('Time').agg({
            'CpuUtil': 'mean',
            'CpuWatts': 'mean',
            'DimmWatts': 'mean',
            'Minimum': 'min',
            'Peak': 'max',
            'Average': 'mean'
        })

        df[WATT_METRICS] = df[WATT_METRICS] * 60

        df_processed_list.append(df)

    # to get OVERVIEW data
    df = pd.concat(df_processed_list) # .sort_index()

    # group by time, then aggregation
    df_overview = df.groupby('Time').agg({
        'CpuUtil': 'mean',
        'CpuWatts': 'sum',
        'DimmWatts': 'sum',
        'Minimum': 'sum',
        'Peak': 'sum',
        'Average': 'sum'
    })

    # shorten the index
    df_overview.index = df_overview.index.str[11:]

    return df_overview


def get_df_start_index_by_seconds(record_number, minute):
    # calculate the index (for 10 seconds)
    records_per_minute = 6
    selected_record_number = records_per_minute * minute

    index_start = record_number - selected_record_number

    return index_start


def get_selected_overview(df, minute):
    record_number = df.shape[0]

    index_start = record_number - minute

    # get the latest records
    return df[index_start:].copy()

def check_time(time):
    reg_pattern = re.compile(r'\d{2}:\d{2}')

    return reg_pattern.match(time)


def get_compare_data(df, time_start, time_end, improve_time):
    data = df.copy()

    # limit time period
    if not check_time(time_start):
        time_start = '19:45'

    if not check_time(time_end):
        time_end = '20:30'

    if not check_time(improve_time):
        improve_time = '20:08'


    # one hour KWatts Consumption
    improve_index = data.index.get_loc(improve_time)
    avg_column_index = data.columns.get_loc('Average')
    kw_before = data.iloc[improve_index-60: improve_index, avg_column_index].sum()
    kw_after = data.iloc[improve_index: improve_index+60, avg_column_index].sum()
    kw_delta = kw_before - kw_after

    # calculate CO2 and Trees
    co2 = kw_delta * 380 / 1000 * 24 * 100 # 100 days kg co2
    trees = co2 / 500

    data = data.loc[time_start: time_end, :]

    # get min and max
    y_min = min(data['Average'].min(), data['Minimum'].min())
    y_max = max(data['Average'].max(), data['Minimum'].max())

    return data, y_min, y_max, round(co2, 2), int(trees)



"""
def get_selected_overview(df, minute, series):
    record_number = df.shape[0]

    index_start = record_number - minute

    # prepare columns
    df_columns = [key for key, value in series.items() if value]

    # if not selected, show all series
    if len(df_columns) == 0:
        df_columns = series.keys()

    # get the latest records
    return df[index_start:][df_columns + ['CpuUtil']].copy()
"""


def get_nivo_data(df):
    data = []

    # loop series: {'col1': {'index1': v1, 'index2': v2}, 'col2': {'index1': v1, 'index2': v2}}
    for key, value in df.to_dict().items():
        # loop cell: {'index1': v1, 'index2': v2}
        data_nested = []

        for k, v in value.items():
            data_nested.append({
                'x': k,
                'y': v
            })

        data.append({
            'id': key,
            'data': data_nested
        })

    return data


def get_bump_chart(df, title):
    data = get_nivo_data(df)

    bump_chart = {
        "data": data,
        "layout": {
            "title": title,
            "type": "bump",
            #"height": 360,
            #"width": 640,
            "colors": {"scheme": "spectral"},
            "lineWidth": 3,
            "activeLineWidth": 6,
            "inactiveLineWidth": 3,
            "inactiveOpacity": 0.15,
            "pointSize": 10,
            "activePointSize": 16,
            "inactivePointSize": 0,
            "pointColor": {"theme": "background"},
            "pointBorderWidth": 3,
            "activePointBorderWidth": 3,
            "pointBorderColor": {"from": "serie.color"},
            "axisTop": {
                "tickSize": 5,
                "tickPadding": 5,
                "tickRotation": 0,
                "legend": "",
                "legendPosition": "middle",
                "legendOffset": -36,
            },
            "axisBottom": {
                "tickSize": 5,
                "tickPadding": 5,
                "tickRotation": 0,
                "legend": "",
                "legendPosition": "middle",
                "legendOffset": 32,
            },
            "axisLeft": {
                "tickSize": 5,
                "tickPadding": 5,
                "tickRotation": 0,
                "legend": "ranking",
                "legendPosition": "middle",
                "legendOffset": -40,
            },
            "margin": {"top": 40, "right": 100, "bottom": 40, "left": 60},
            "axisRight": None,
        }
    }

    return bump_chart


