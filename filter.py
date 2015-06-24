''' Filters taxi trip data based on parameters set in filter_config.py

Example:
    python filter.py trip_data_1_small.csv trip_data_1_small_filtered.csv
'''
from __future__ import print_function

import csv
import argparse
import config as cfg

from pdb import set_trace as T
from math import radians, cos, sin, asin, sqrt

parser = argparse.ArgumentParser()
parser.add_argument('in_filename', help='Filename for input trip data')
parser.add_argument('out_filename', help='Filename to output filtered trip data')
args = parser.parse_args()

def keep_row(row):
    keep = True
    try:
        trip_distance = float(row[' trip_distance'])
        trip_time = float(row[' trip_distance'])
        params = {}
        params['geodesic'] = \
          geodesic(row[' pickup_longitude'], row[' pickup_latitude'],
                   row[' dropoff_longitude'], row[' dropoff_latitude'])
        params['winding_factor'] = trip_distance / params['geodesic']
        params['pace'] = trip_time / trip_distance

        for param, value in params.items():
            low, high = cfg.FILTER_PARAMS[param]
            if not (low <= value <= high):
                keep = False

        for field, (low, high) in cfg.FILTER_FIELDS.items():
            if not (low <= float(row[field]) <= high):
                keep = False
        return keep
    except ValueError:
        return False
    except ZeroDivisionError:
        return False

def geodesic(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees) in miles
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, map(float, [lon1, lat1, lon2, lat2]))

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 3956 # Radius of earth in mi. Use 6371 for km
    return c * r

with open(args.in_filename) as in_file:
    with open(args.out_filename,'w') as out_file:
        reader = csv.DictReader(in_file)
        fieldnames = reader.fieldnames
        print(','.join(fieldnames), file=out_file)
        for row in reader:
            if keep_row(row):
                print(','.join(map(row.get, fieldnames)), file=out_file)
