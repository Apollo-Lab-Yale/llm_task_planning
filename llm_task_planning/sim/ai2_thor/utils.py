

AI2THOR_PREDICATES = [
    'visible',
    'isInteractable',
    'receptacle',
    'toggleable',
    'isToggled',
    'breakable',
    'isBroken',
    'canFillWithLiquid',
    'isFilledWithLiquid',
    'dirtyable',
    'isDirty',
    'canBeUsedUp',
    'isUsedUp',
    'cookable',
    'isCooked',
    'isHeatSource',
    'isColdSource',
    'sliceable',
    'isSliced',
    'openable',
    'isOpen',
    'pickupable',
    'isPickedUp',
    'moveable'
]

AI2THOR_TO_VHOME = {
    'receptacle': 'SURFACES',
    'toggleable': 'HAS_SWITCH',
    'isToggled': 'ON',
    'isDirty': 'DIRTY',
    'isCooked': 'COOKED',
    'openable': 'CAN_OPEN',
    'pickupable': 'GRABBABLE',
    'isPickedUp': 'HOLDS',
    'onTop': 'ON_TOP',
    'moveable': "MOVEABLE"
}

CLOSE_DISTANCE = 1

def get_vhome_to_thor_dict():
    vhome_to_thor = {}
    for key, val in AI2THOR_PREDICATES:
        vhome_to_thor[val] = key
    vhome_to_thor["CONTAINER"] = 'receptacle'
    return vhome_to_thor

def get_visible_objects(object_meta):
    visible = []
    for object in object_meta:
        if object["visible"]:
            visible.append(object)
    return visible

def get_predicates(objects):
    predicates = []
    for object in objects:
        for pred in AI2THOR_PREDICATES:
            if object[pred]:
                predicates.append(f"{pred} {object['assetId']}")
        if object['distance'] < CLOSE_DISTANCE:
            predicates.append(f"close {object['assetId']}")
    return predicates

def is_in_room(point, polygon):
    """
    Determine if the point is in the polygon.

    Args:
    point -- A tuple (x, y) representing the point to check.
    polygon -- A list of tuples [(x, y), (x, y), ...] representing the vertices of the polygon.

    Returns:
    True if the point is in the polygon; False otherwise.
    """

    x, z, y = point['x'], point['y'], point['z']
    inside = False

    for i in range(len(polygon)):
        point = polygon[i]
        x1, z1, y1 = point['x'], point['y'], point['z']
        point = polygon[(i + 1) % len(polygon)]
        x2, Z2, y2 = point['x'], point['y'], point['z']
        xinters = 0
        if y > min(y1, y2) and y <= max(y1, y2) and x <= max(x1, x2):
            if y1 != y2:
                xinters = (y - y1) * (x2 - x1) / (y2 - y1) + x1
            if x1 == x2 or x <= xinters:
                inside = not inside

    return inside


def find_closest_position(point, positions):
    """
    Find the closest position to a reference point.

    Args:
    point -- A dict {'x': x_value, 'y': y_value, 'z': z_value} representing the reference point.
    positions -- A list of dicts [{'x': x_value, 'y': y_value, 'z': z_value}, ...] representing the valid positions.

    Returns:
    A dict representing the closest position.
    """

    def distance(p1, p2):
        """Calculate Euclidean distance ignoring y coordinate."""
        return ((p1['x'] - p2['x']) ** 2 + (p1['z'] - p2['z']) ** 2) ** 0.5

    min_distance = float('inf')
    closest_position = None

    for pos in positions:
        dist = distance(point, pos)
        if dist < min_distance:
            min_distance = dist
            closest_position = pos

    return closest_position
