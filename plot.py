''' Plots figures showing initial statistics from the taxi data

Example:
    python analyze.py trip_data_1_small.csv
'''

import matplotlib
matplotlib.use('Agg') # plotting without graphics

from pdb import set_trace as T
from django.contrib.gis.geos import Polygon, Point
from time import strptime, mktime
from datetime import datetime

import matplotlib.pyplot as plt
import argparse
import csv
import sys
import shapefile
import pickle


def save(filename):
    plt.savefig(filename, format="pdf", transparent=True, bbox_inches="tight")

parser = argparse.ArgumentParser()
parser.add_argument("input_file", help="Filename for input trip data ")
args = parser.parse_args()

lat_min, lat_max = 40.76041, 40.76507
lon_min, lon_max = -73.98164, -73.97653
hr_min, hr_max = 19, 21 # 11, 14 #

keys = { 'medallion'          : 0
       , 'hack_license'       : 1
       , 'vendor_id'          : 2
       , 'rate_code'          : 3
       , 'store_and_fwd_flag' : 4
       , 'pickup_datetime'    : 5
       , 'dropoff_datetime'   : 6
       , 'passenger_count'    : 7
       , 'trip_time_in_secs'  : 8
       , 'trip_distance'      : 9
       , 'pickup_longitude'   : 10
       , 'pickup_latitude'    : 11
       , 'dropoff_longitude'  : 12
       , 'dropoff_latitude'   : 13
       }

with open(args.input_file) as f:
    reader = csv.reader(f)
    trip_time = []
    trip_dist = []
    passengers = []
    pickup_times = []
    reader.next() # Skip fields row
    for row in reader:
        lat = float(row[keys['pickup_latitude']])
        lon = float(row[keys['pickup_longitude']])

        if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
            t = strptime(row[keys['pickup_datetime']], '%Y-%m-%d %H:%M:%S')
            if hr_min <= t.tm_hour <= hr_max:
                pickup_times.append(datetime.fromtimestamp(mktime(t)))

        trip_time.append(int(row[keys['trip_time_in_secs']]))
        trip_dist.append(float(row[keys['trip_distance']]))
        passengers.append(int(row[keys['passenger_count']]))

pickup_times.sort()

cur_time = pickup_times[0]
deltas = []
for i in range(1, len(pickup_times)):
    delta = (pickup_times[i] - cur_time).total_seconds()
    assert delta >= 0, 'Pickup times not sorted!'
    if delta < 3600 * (hr_max - hr_min): # Remove gaps across days
        deltas.append(delta)
    cur_time = pickup_times[i]

pickle.dump(deltas, open('figures/deltas.pkl', 'wb'))

plt.hist(trip_time, bins = 1000)
save('figures/trip_time_histogram.pdf')
plt.clf()

plt.hist(trip_dist, bins = 1000)
save('figures/trip_dist_histogram.pdf')
plt.clf()

plt.hist(passengers, bins = 1000)
save('figures/trip_passengers_histogram.pdf')
plt.clf()
