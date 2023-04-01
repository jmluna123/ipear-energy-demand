from shapely.geometry import Polygon, Point
from shapely.ops import nearest_points
from collections import deque


def obtain_coords_charges(points_charge):
    coords = []

    for point in points_charge:
        coord = point['geometry']['coordinates']
        coords.append(Point((coord[0], coord[1])))
    return coords


def obtain_coords_crops(crops):
    polygons = []

    for crop in crops:
        coords = crop['poligono'][0]
        polygon = []
        for coord in coords:
            polygon.append((coord[0], coord[1]))
        polygons.append(Polygon(polygon))
    return polygons


def obtain_terrain_available(coord_terrain, coords_crops):
    crop_coord_terrain = coord_terrain

    for crop in coords_crops:
        crop_coord_terrain = crop_coord_terrain.difference(crop)

    return crop_coord_terrain


def obtain_geometric_center(coords_crops, coords_charges=[]):
    coords_x = []
    coords_y = []

    for coord in coords_crops:
        coords_x.append(coord.centroid.x)
        coords_y.append(coord.centroid.y)

    for coord in coords_charges:
        coords_x.append(coord.x)
        coords_y.append(coord.y)

    return (sum(coords_x)/len(coords_x), sum(coords_y)/len(coords_y))


def obtain_location(coords_terrain, coords_crop, crop_polygons, coords_terrain_available):
    location = obtain_location_rc(
        coords_terrain[0], coords_terrain[1], coords_crop[0], coords_crop[1], coords_terrain_available)

    if location[0] == -1:
        point = coords_terrain_available.centroid
        near = None
        for crop in crop_polygons:
            tmp = nearest_points(crop.boundary, point)[0]
            if near is None or tmp.distance(point) < near.distance(point):
                near = tmp
        return near

    return Point(location)
    # return location


def obtain_location_rc(x_ground, y_ground, x_crop, y_crop, coords_terrain_available, i=10):
    x_mid, y_mid = ((x_ground + x_crop)/2, ((y_ground + y_crop)/2))
    is_terrain = coords_terrain_available.contains(Point(x_mid, y_mid))

    # search left
    x, y = (-1, -1)
    if i > 0 and is_terrain:
        x, y = obtain_location_rc(
            x_mid, y_mid, x_crop, y_crop, coords_terrain_available, i-1)
    # search right
    elif i > 0 and not is_terrain:
        x, y = obtain_location_rc(
            x_ground, y_ground, x_mid, y_mid, coords_terrain_available, i-1)
    elif is_terrain:
        return (x_mid, y_mid)
    else:
        return (-1, -1)

    if x == -1 and not is_terrain:
        return (-1, -1)
    if x != -1:
        return (x, y)
    return (x_mid, y_mid)


def range_coords(coords_prop, crops):
    coords_prop_polygons = []
    coords_crops_polygons = []

    lngs_coords_prop = []
    lats_coords_prop = []

    for coords in coords_prop:
        if coords[0] not in lngs_coords_prop:
            lngs_coords_prop.append(coords[0])
        if coords[1] not in lats_coords_prop:
            lats_coords_prop.append(coords[1])
    coords_prop_polygons.append([lngs_coords_prop, lats_coords_prop])

    for item in crops:
        for crop in item['poligono']:
            lngs_crops = []
            lats_crops = []
            for coords in crop:
                if coords[0] not in lngs_crops:
                    lngs_crops.append(coords[0])
                if coords[1] not in lats_crops:
                    lats_crops.append(coords[1])
            coords_crops_polygons.append([lngs_crops, lats_crops])

    return coords_prop_polygons, coords_crops_polygons


def valid_coords(coords, range_coords_prop, range_coords_crops):
    lng = coords[0]
    lat = coords[1]
    valid = []

    for item in range_coords_prop:
        if (lng > min(item[0]) and lng < max(item[0]) and lat > min(item[1]) and lat < max(item[1])):
            if True not in valid:
                valid.append(True)

    for item in range_coords_crops:
        if (lng > min(item[0]) and lng < max(item[0]) and lat > min(item[1]) and lat < max(item[1])):
            if True not in valid:
                valid.append(False)

    if False in valid:
        return False
    else:
        return True


def obtain_panels_polygon(n_panels, location, terrain_available, panel_size=(1.134, 2.279), padding=0.5, rate=0.00001):
    x_lenght = rate * panel_size[0]
    y_lenght = rate * panel_size[1]
    location = Point((round(location.x, 12), round(location.y, 12)))
    # print(location)

    pad = rate * padding
    panels_ref = set()
    panels = []
    queue = deque([location])

    # Verificar si el punto de origen está dentro del terreno disponible
    if not terrain_available.contains(location):
        # print('CONTAIN')
        return []

    # Calcular las coordenadas de los puntos vecinos
    coord_dwn = Point((round(location.x, 12), round(location.y + y_lenght, 12)))
    coord_lft = Point((round(location.x + x_lenght, 12), round(location.y, 12)))
    coord_dgnl = Point((round(location.x + x_lenght, 12), round(location.y + y_lenght, 12)))

    # count = 0
    while len(queue) > 0 and len(panels) < n_panels:
        # count = count + 1
        origin = queue.popleft()
        x, y = round(origin.x ,12), round(origin.y, 12)
        # print(x,y)
        # print(queue)
        # print(panels)
        # print('AAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
        if (x, y) not in panels_ref:
            # print(x,y)
            # print("origin: ", origin, terrain_available.contains(origin))
            # print("coord_dwn: ", coord_dwn, terrain_available.contains(coord_dwn))
            # print("coord_lft: ", coord_lft, terrain_available.contains(coord_lft))
            # print("coord_dgnl: ", coord_dgnl, terrain_available.contains(coord_dgnl))
            # print('BBBBBBBBBBBBBBBBBBBBBBBBBB')
            # Verificar si todos los puntos del panel están dentro del terreno disponible
            if terrain_available.contains(origin) and terrain_available.contains(coord_dwn) and terrain_available.contains(coord_lft) and terrain_available.contains(coord_dgnl):
                # print(x,y)
                # print('CCCCCCCCCCCCCCCCCCCCCCCCCCCC')
                panels_ref.add((x, y))
                panels.append([(round(x - x_lenght, 12), y), (x, y),(x, round(y - y_lenght, 12)), (round(x - x_lenght, 12), round(y - y_lenght, 12))])

            # Agregar puntos vecinos a la cola
            coord_up = Point((x, round(y + y_lenght + pad, 12)))
            coord_dwn = Point((x, round(y - y_lenght - pad, 12)))
            coord_lft = Point((round(x - x_lenght - pad, 12), y))
            coord_rght = Point((round(x + x_lenght + pad, 12), y))

            if (coord_up.x, coord_up.y) not in panels_ref and terrain_available.contains(coord_up):
                # print("coord_up: ", coord_up)
                queue.append(coord_up)
            if (coord_dwn.x, coord_dwn.y) not in panels_ref and terrain_available.contains(coord_dwn):
                # print("coord_dwn: ", coord_dwn)
                queue.append(coord_dwn)
            if (coord_lft.x, coord_lft.y) not in panels_ref and terrain_available.contains(coord_lft):
                # print("coord_lft: ", coord_lft)
                queue.append(coord_lft)
            if (coord_rght.x, coord_rght.y) not in panels_ref and terrain_available.contains(coord_rght):
                # print("coord_rght: ", coord_rght)
                queue.append(coord_rght)
    return panels


def obtain_panels_polygon1(n_panels, location, terrain_available, panel_size=(1.134, 2.279), padding=0.5, rate=0.00001):
    x_lenght = rate * panel_size[0]
    y_lenght = rate * panel_size[1]

    pad = rate * padding
    panels_ref = set()
    panels = []
    queue = deque([location])

    # Verificar si el punto de origen está dentro del terreno disponible
    if not terrain_available.contains(location):
        return []

    # Calcular las coordenadas de los puntos vecinos
    coord_dwn = Point((location.x, location.y - y_lenght))
    coord_lft = Point((location.x - x_lenght, location.y))
    coord_dgnl = Point((location.x - x_lenght, location.y - y_lenght))

    coord_up = Point((location.x, location.y + y_lenght + pad))
    coord_dwn = Point((location.x, location.y - y_lenght - pad))
    coord_lft = Point((location.x - x_lenght - pad, location.y))
    coord_rght = Point((location.x + x_lenght + pad, location.y))

    while queue and len(panels) < n_panels:
        origin = queue.popleft()
        x, y = origin.x, origin.y

        if (x, y) in panels_ref:
            continue

        # Verificar si todos los puntos del panel están dentro del terreno disponible
        if terrain_available.contains(origin) and terrain_available.contains(coord_dwn) and terrain_available.contains(coord_lft) and terrain_available.contains(coord_dgnl):
            panels_ref.add((x, y))
            panels.append([(x - x_lenght, y), (x, y), (x, y - y_lenght), (x - x_lenght, y - y_lenght)])
            panels_to_extend = [(coord_up.x, coord_up.y), (coord_dwn.x, coord_dwn.y), (coord_lft.x, coord_lft.y), (coord_rght.x, coord_rght.y)]
            panels_to_extend = [panel for panel in panels_to_extend if panel not in panels_ref and terrain_available.contains(Point(panel))]
            queue.extend([Point(panel) for panel in panels_to_extend])
    print(panels)
    return panels