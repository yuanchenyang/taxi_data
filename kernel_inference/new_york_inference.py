import json
import pandas as pd
import numpy as np
import datetime as dt
from collections import defaultdict
from pdb import set_trace as T

import pathfinder as pf
from kernel_inference import Bins, Rect, uniq


INPUT_FILE = '../data/trip_data_2_small.csv'
OUTPUT_FILE = 'filtered_paths2.txt'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
TRIP_TIME_CUTOFF = 3000 # Max trip time in seconds
FILTER_TIME_INTERVAL = (dt.time(18, 0), dt.time(20, 0)) # Time period to filter
DELTA = 10 # Step for interpolation
ORIGIN_RECT = (9, 12)
MANHATTAN_RECT = Rect(-74.025, -73.92, 40.70, 40.85)
BIN_SIZE = 0.0025

def process_df(df):
    df = df[df['trip_time_in_secs'] < TRIP_TIME_CUTOFF]
    df['pickup_datetime'] = pd.to_datetime(df['pickup_datetime'])
    df = df.set_index(pd.DatetimeIndex(df['pickup_datetime']))
    return df.between_time(*FILTER_TIME_INTERVAL)

def import_data(input_file):
    data_chunks = pd.read_csv(input_file, iterator=True, chunksize=10000)
    return pd.concat(process_df(df) for df in data_chunks)

def pif_row(row, pif, bins, delta):
    locs = [[row['pickup_latitude'], row['pickup_longitude']],
            [row['dropoff_latitude'], row['dropoff_longitude']]]
    path = pif.pathfind(locs)
    trip_time = row['trip_time_in_secs']
    if path == []: return
    interpolated = [bins.get_bin(x, y) for x, y in pif.interpolate(path, delta)]
    time = np.linspace(0, trip_time, len(interpolated))
    return {'pickup_time': str(row['pickup_datetime'].time()),
            'path': list(uniq(zip(interpolated, time), lambda x: x[0]))}

def load(paths_filename):
    kernel = defaultdict(lambda: defaultdict(list))
    for line in open(paths_filename):
        path = json.loads(line)['path']
        for start_index in range(len(path)):
            start, start_time = path[start_index]
            for end_index in range(start_index + 1, len(path)):
                end, end_time = path[end_index]
                kernel[tuple(start)][tuple(end)].append(end_time - start_time)
    return kernel

def dump_paths():
    bins = Bins(MANHATTAN_RECT, BIN_SIZE)
    data = import_data(INPUT_FILE)
    graph = pf.make_graph('central_ny')
    pif = pf.PIFPathfinder(graph)
    with open(OUTPUT_FILE, 'w') as outfile:
        for i, (_, row) in enumerate(data.iterrows()):
            if i % 1000 == 0: print i
            res = pif_row(row, pif, bins, DELTA)
            if res is None: continue
            print >>outfile, json.dumps(res)

if __name__ == '__main__':
    dump_paths()
