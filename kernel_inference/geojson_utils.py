import json
import copy

class FeatureCollection:
    def __init__(self):
        self.features = []

    def __str__(self):
        json.dumps(self.export())

    def export(self):
        return {'type': 'FeatureCollection',
                'features': self.features}

    def dump(self, file_name):
        json.dump(self.export(), open(file_name, 'wb'))

    def add(self, geom, props):
        try:
            geom = json.loads(geom)
        except:
            pass
        self.features.append({'type': 'Feature',
                              'geometry': geom,
                              'properties': props})

    def add_polygon(self, points, props=None):
        self.add({'type' : 'Polygon',
                  'coordinates': [points + [points[0]]]}, props or {})

    def deepcopy(self):
        fc = FeatureCollection()
        fc.features = copy.deepcopy(self.features)
        return fc
