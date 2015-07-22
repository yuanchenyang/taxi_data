''' Tools for kernel inference
'''
from collections import defaultdict, namedtuple

Rect = namedtuple('Rect', ['xmin', 'xmax', 'ymin', 'ymax'])

# This does not take into account curvature of the Earth
class Bins:
    def __init__(self, rect, binsize):
        self.rect = rect
        self.xoffset = rect.xmin
        self.yoffset = rect.ymin
        self.binsize = float(binsize)
        self.bins = defaultdict(list)

    def add(self, x, y, item):
        self.bins[self.get_bin(x, y)].append(item)

    def get_bin(self, x, y):
        nx = int((x - self.xoffset) / self.binsize)
        ny = int((y - self.yoffset) / self.binsize)
        return nx, ny

    def get_coords(self, nx, ny):
        return self.xoffset + self.binsize * nx, self.yoffset + self.binsize * ny

    def get_rect(self, nx, ny):
        xmin, ymin = self.get_coords(nx, ny)
        xmax, ymax = xmin + self.binsize, ymin + self.binsize
        return Rect(xmin, xmax, ymin, ymax)

    def clear_bins(self):
        self.bins = defaultdict(list)

def uniq(seq, key=None):
    '''Remove duplicates from item stream, assumes it doesn't start with None'''
    key = key or (lambda x: x)
    prev = None
    for i in seq:
        x = key(i)
        if x != prev:
            prev = x
            yield i
