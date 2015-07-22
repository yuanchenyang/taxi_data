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
CYTHON_PATH    = os.path.join(PYTHON_PATH, 'CoreGraph/Cython')

subprocess.call('cd %s && python2 setup.py build_ext --inplace' % CYTHON_PATH,
                shell=True)
sys.path.append(PYTHON_PATH)

from CoreGraph.OSMGraph import OSMGraph
from CoreGraph.Cython._CoreGraph import *

def create_spatial_projector(graph):
    vertex_coord_dict = dict(zip(graph.vertex_ids, graph.vertex_coords))
    source_coords = np.asarray([vertex_coord_dict[i]
                                for i in graph.source_ids], dtype = 'f8,f8')
    target_coords = np.asarray([vertex_coord_dict[i]
                                for i in graph.target_ids], dtype = 'f8,f8')
    return Projector(graph.vertex_ids, graph.vertex_coords, graph.source_ids,
                     source_coords, graph.target_ids, target_coords)

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
    return OSMGraph(graph_name)

class Pathfinder:
    def pathfind(self, locs):
        raise NotImplementedError

class PIFPathfinder(Pathfinder):
    def __init__(self, graph,
                 n_projs=cfg['MAX_PROJS'], n_paths=cfg['MAX_PATHS'],
                 sigma=cfg['GPS_PEN'], penalty=cfg['PATH_PEN']):

        self.graph = graph
        self.projector = create_spatial_projector(self.graph)
        self.pif = PathInferenceFilter(self.graph, self.projector,
                                       n_projs, n_paths, sigma, penalty)

    def pathfind(self, locs, thresholds=None):
        thresholds = thresholds or [cfg['DEFAULT_THRESHOLD']] * len(locs)
        locs = [(y, x) for x, y in locs] # PIF takes reversed lat-lon

        _, path = self.pif.run(locs, thresholds)
        return  sum(path, [])

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

class Interpolator:
    def __init__(self, graph):
        self.graph = graph
        self.vert2xy = graph.vertex_coord_dict
        self.ip = TrajectoryInterp(graph)

    def coords(self, vertex_ids):
        return reverse_path([self.vert2xy[p] for p in vertex_ids
                                             if p in self.vert2xy])

    def interpolate(self, vertex_ids, step):
        return self.ip.interpolate(vertex_ids, step)

def test():
    # Test path inference filter
    locs = [(40.763287, -73.979823), (40.711471, -74.010413)]
    graph = make_graph('central_ny')
    ip = Interpolator(graph)

    pif = PIFPathfinder(graph)
    print to_geojson(ip.interpolate(pif.pathfind(locs)))

    osrm = OSRMPathfinder('http://127.0.0.1:5000')
    print to_geojson(osrm.pathfind_coords(locs))

if __name__ == '__main__':
    test()
