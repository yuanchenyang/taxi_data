import sys
import os
import subprocess
import requests
import json
import xml.etree.ElementTree as ET

from polyline.codec import PolylineCodec
from pdb import set_trace as T

cfg = dict(

    GRAPH_LIB_PATH = '/home/chenyang/src/megacell/expose_data',

    # Default PIF parameters
    MAX_PROJS = 3    , # maximum number of projections allowed
    MAX_PATHS = 1    , # maximum number of paths between projections
    GPS_PEN   = 1.0  , # penalization coefficient of distance from GPS trace to network
    PATH_PEN  = 10.0 , # penalization coefficient of length of path between projections

    # Maximum distance to search between gps points
    DEFAULT_THRESHOLD = 55000
)

GRAPH_LIB_PATH = cfg['GRAPH_LIB_PATH']
PYTHON_PATH    = os.path.join(GRAPH_LIB_PATH, 'python_wksp')
CYTHON_PATH    = os.path.join(PYTHON_PATH, 'Tr_lib/cython')

subprocess.call('cd %s && python2 setup.py build_ext --inplace' % CYTHON_PATH,
                shell=True)
sys.path.append(PYTHON_PATH)

from Tr_lib.containers.TrafficGraph import TrafficGraph
from Tr_lib.cython._tr_lib import *

def decode_polyline(geom):
    ''' Polyline library returns 6 decimal places, so we divide each coord
    by 10 here
    '''
    return [(x / 10, y / 10) for x, y in PolylineCodec().decode(geom)]

def reverse_path(path):
    return [(y, x) for x, y in path]

def to_geojson(path):
    path = map(list, reverse_path(path))
    return json.dumps({'type': 'Feature',
                       'geometry': {
                           'type':'LineString',
                           'coordinates': path},
                       'properties': {}})

def make_graph(graph_name):
    return TrafficGraph(graph_name)

class Pathfinder:
    def pathfind(self, locs):
        raise NotImplementedError

class PIFPathfinder(Pathfinder):
    def __init__(self, graph,
                 n_projs=cfg['MAX_PROJS'], n_paths=cfg['MAX_PATHS'],
                 sigma=cfg['GPS_PEN'], penalty=cfg['PATH_PEN']):

        self.graph = graph
        self.all_vertex_states = \
          np.asarray([(s['lon'], s['lat']) for s in graph.get_vertex_states().values()],
                     dtype='f8,f8')
        self.sp_layout = self.create_spatial_layout()
        self.pif = PathInferenceFilter(self.graph, self.sp_layout,
                                       n_projs, n_paths, sigma, penalty)

    def create_spatial_layout(self):
        return SpatialLayout(self.graph.vertex_ids, self.all_vertex_states,
                             self.graph.link_ids,   self.graph.link_coords)

    def pathfind(self, locs, thresholds=None):
        thresholds = thresholds or [cfg['DEFAULT_THRESHOLD']] * len(locs)
        locs = [(y, x) for x, y in locs] # PIF takes reversed lat-lon

        inferred_paths, inferred_coords, _ = self.pif.run(locs, thresholds)
        return sum(inferred_paths, [])

    def create_interpolator(self):
        return TrajectoryInterpolator(self.graph, self.sp_layout)

class OSRMPathfinder(Pathfinder):
    def __init__(self, baseurl):
        self.baseurl = baseurl

    def pathfind(self, locs):
        waypoints = '&'.join(['loc={},{}'.format(lat, lon) for lat, lon in locs])
        url = self.baseurl + '/viaroute?output=wayid&' + waypoints
        root = ET.fromstring(requests.get(url).text)
        return [int(i.text) for i in root[1]]

    def pathfind_coords(self, locs):
        waypoints = '&'.join(['loc={},{}'.format(lat, lon) for lat, lon in locs])
        url = self.baseurl + '/viaroute?' + waypoints
        res = requests.get(url).json()
        return decode_polyline(res['route_geometry'])

def test():
    # Test path inference filter
    locs = [(40.763287, -73.979823), (40.711471, -74.010413)]
    delta = 20
    graph = make_graph('central_ny')

    pif = PIFPathfinder(graph)
    ip = pif.create_interpolator()

    print to_geojson(ip.interpolate(pif.pathfind(locs), delta))

    osrm = OSRMPathfinder('http://127.0.0.1:5000')
    print to_geojson(osrm.pathfind_coords(locs))

if __name__ == '__main__':
    test()
