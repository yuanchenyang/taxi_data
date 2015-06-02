''' Plots figures showing initial statistics from the taxi data

Example:
    python analyze.py trip_data_1_small.csv
'''

import matplotlib
matplotlib.use('Agg') # plotting without graphics

from pdb import set_trace as T

import matplotlib.pyplot as plt
import argparse
import csv
import sys

def save(filename):
    plt.savefig(filename, format="pdf", transparent=True, bbox_inches="tight")

parser = argparse.ArgumentParser()
parser.add_argument("input_file", help="Filename for input trip data ")
args = parser.parse_args()

with open(args.input_file) as f:
    reader = csv.DictReader(f)
    trip_time = []
    trip_dist = []
    passengers = []
    for row in reader:
        trip_time.append(int(row[' trip_time_in_secs']))
        trip_dist.append(float(row[' trip_distance']))
        passengers.append(int(row[' passenger_count']))

plt.hist(trip_time, bins = 100)
save('figures/trip_time_histogram.pdf')
plt.clf()

plt.hist(trip_dist, bins = 100)
save('figures/trip_dist_histogram.pdf')
plt.clf()

plt.hist(passengers, bins = 100)
save('figures/trip_passengers_histogram.pdf')
plt.clf()
