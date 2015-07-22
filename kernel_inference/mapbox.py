import cartopy.crs as ccrs
from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle
from cartopy.io.img_tiles import MapboxTiles

# Load my mapbox map
mapbox_token = 'pk.eyJ1IjoiY2hlbnlhbmciLCJhIjoiNjAwYTI1MDExNDdmYzVkZWY0M2NkNjQyMDJkZjhkOTMifQ.G7P8sFypgRqFW2QNaEZocQ'
mapbox_mapid = 'chenyang.e39eae3e'

def get_plot(rect, **figargs):
    mapbox_tiles = MapboxTiles(mapbox_token, mapbox_mapid)

    # Create new axes, using the tiles' projection for the underlying map.
    fig = plt.figure(**figargs)
    ax = plt.axes(projection=mapbox_tiles.crs)

    # Specify a region of interest
    ax.set_extent(tuple(rect), ccrs.PlateCarree())

    # Add the tiles at zoom level 13.
    ax.add_image(mapbox_tiles, 13)

    return fig, ax

def add_rect(ax, rect, **kwargs):
    ax.add_patch(Rectangle(
        (rect.xmin,  rect.ymin),
        rect.xmax - rect.xmin, rect.ymax - rect.ymin,
        transform=ccrs.PlateCarree(), **kwargs))
    return ax
