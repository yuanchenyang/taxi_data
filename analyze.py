import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import csv

from pdb import set_trace as T

with open('trip_data_1_small.csv') as f:
    reader = csv.DictReader(f)
    trip_time = []
    trip_dist = []
    passengers = []
    for row in reader:
        trip_time.append(int(row[' trip_time_in_secs']))
        trip_dist.append(float(row[' trip_distance']))    
        passengers.append(int(row[' passenger_count']))

plt.hist(trip_time, bins = 100)
plt.savefig('figures/trip_time_histogram.pdf', format="pdf", transparent=True, bbox_inches="tight")
plt.clf()

plt.hist(trip_dist, bins = 100)
plt.savefig('figures/trip_dist_histogram.pdf', format="pdf", transparent=True, bbox_inches="tight")
plt.clf()

plt.hist(passengers, bins = 100)
plt.savefig('figures/trip_passengers_histogram.pdf', format="pdf", transparent=True, bbox_inches="tight")
plt.clf()
