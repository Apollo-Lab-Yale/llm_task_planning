from llm_task_planning.problem.utils import parse_instantiated_predicate
from llm_task_planning.sim.ai2_thor.utils import CLOSE_DISTANCE, get_vhome_to_thor_dict


PREDICATES = (
    "CAN_OPEN",
    "CLOTHES",
    "CONTAINERS",
    "COVER_OBJECT",
    "CREAM",
    "CUTTABLE",
    "DRINKABLE",
    "EATABLE",
    "GRABBABLE",
    "HANGABLE",
    "HAS_PAPER",
    "HAS_PLUG",
    "HAS_SWITCH",
    "LIEABLE",
    "LOOKABLE",
    "MOVABLE",
    "POURABLE",
    "READABLE",
    "RECIPIENT",
    "SITTABLE",
    "SURFACES",
    "ON_TOP"
    "INSIDE",
    "ON",
    "OFF",
    "OPEN",
    "CLOSED"
    "FAR",
    "CLOSE"
)

GOAL_PREDICATES = (
    "ON_TOP <object1> <object1>" #indicates object1 is on top of object 2
    "INSIDE <character> <room>", # indicates character in room
    "INSIDE <object> <room>", # indicates object in room
    "INSIDE <object1> <object2>", # indicates object1 inside object2
    "ON <object>", # indicates object is switched on
    "OFF <object>", # indicates object is switched off
    "OPEN <object>", # indicates object is open
    "CLOSED <object>" # indicates object is closed,
    "COOKED <object1> <object2>" # indicates object1 was cooked in object2'
)

def check_close(object):
    return object["distance"] <= CLOSE_DISTANCE

def get_object_properties_and_states(state):
    global PREDICATES
    object_properties_states = {}
    object_properties_states["HOLDS"] = {}
    object_properties_states["CLOSE"] = {}
    object_properties_states["FAR"] = {}
    vhome_to_thor = get_vhome_to_thor_dict()
    for object in state["objects"]:
        is_close = check_close(object)
        if is_close:
            object_properties_states["CLOSE"][object["objectId"]] = object
        else:
            object_properties_states["FAR"][object["objectId"]] = object
        for pred in vhome_to_thor:
            if pred not in object_properties_states:
                object_properties_states[pred] = {}
            if object[vhome_to_thor[pred]]:
                object_properties_states[pred][object["objectId"]] = object

    return object_properties_states


def resolve_nonvisible(goal, obj_preds, rooms):
    if goal in obj_preds["FAR"]:
        return [f"walk {goal}"]

    actions = ["turnleft character", "turnright character"]
    for room in rooms:
        actions.append(f"walk {room}")
    for object in obj_preds['CLOSE'].intersection(obj_preds["CAN_OPEN"]):
        if object in obj_preds["OPEN"]:
            actions.append(f"close {object}")
        else:
            actions.append(f"open {object}")
    for object in obj_preds["FAR"].intersection(obj_preds["CAN_OPEN"]):
        actions.append(f"walk {object}")
    actions.append(f"scanroom {goal}")
    return actions

def resolve_place_object(obj_preds, rooms):
    actions = []
    for object in obj_preds["HOLDS"]:
        for surface in obj_preds["SURFACES"]:
            if surface in obj_preds["CLOSE"]:
                actions.append(f"put {object} {surface}")
            if surface in obj_preds["FAR"]:
                actions.append(f"walk {surface}")
    if len(actions) == 0:
        actions += ["turnleft character", "turnright character"]
    return actions

def resolve_not_holding(goal, obj_preds, rooms, memory = None):
    actions = []
    if len(obj_preds["HOLDS"]) == MAX_OBJ_HOLD:
        return resolve_place_object(obj_preds, rooms)
    if goal not in obj_preds["CLOSE"] :
        return resolve_nonvisible(goal, obj_preds, rooms, memory)
    goal_in = [pred[1] for pred in obj_preds["IN"] if goal == pred[0] and pred[1] in obj_preds["ON"]]
    if len(goal_in) > 0:
        return resolve_on(goal_in[0], obj_preds, rooms, memory)
    return [f"grab {goal}"]

def resolve_not_inside(obj1, obj2, obj_preds, rooms, memory = None):
    if obj1 not in obj_preds["HOLDS"]:
        return resolve_not_holding(obj1, obj_preds, rooms, memory)
    if obj2 not in obj_preds["CLOSE"]:
        return resolve_nonvisible(obj2, obj_preds, rooms, memory)
    if obj2 in obj_preds["CAN_OPEN"] and obj2 not in obj_preds["OPEN"]:
        return [f"open {obj2}"]
    return [f"putin {obj1} {obj2}"]

def resolve_not_ontop(obj1, obj2, obj_preds, rooms, memory = None):
    print("resolve not ontop")
    if obj1 not in obj_preds["HOLDS"]:
        return resolve_not_holding(obj1, obj_preds, rooms, memory)
    if obj2 not in obj_preds["CLOSE"]:
        return resolve_nonvisible(obj2, obj_preds, rooms, memory)
    if obj2 in obj_preds["CAN_OPEN"] and obj2 not in obj_preds["OPEN"]:
        return [f"open {obj2}"]
    return [f"put {obj1} {obj2}"]

def resolve_off(obj1, obj_preds, rooms, memory = None):
    print("resolve off")
    if obj1 not in obj_preds["CLOSE"]:
        return resolve_nonvisible(obj1, obj_preds, rooms, memory)
    return [f"switchon {obj1}"]

def resolve_on(obj1, obj_preds, rooms, memory = None):
    if obj1 not in obj_preds["CLOSE"]:
        return resolve_nonvisible(obj1, obj_preds, rooms, memory)
    return [f"switchoff {obj1}"]

def resolve_closed(obj1, obj_preds, rooms, memory = None):
    if obj1 not in obj_preds["CLOSE"]:
        return resolve_nonvisible(obj1, obj_preds, rooms, memory)
    return [f"open {obj1}"]

"""
"""
def resolve_cooked(obj1, obj2, obj_preds, rooms, memory = None):
    """Returns a set of actions for progressing through a cooking task

        Parameters:
        - obj1 (str): the object to be cooked
        - obj2 (str): the object to cook with (ie. stove, microwave)
        - obj_preds (dict): dictionary with keys predicates and values of sets of objects known to satisfy those predicates
        - rooms (list): list of strings of known rooms
        - memory (PlannerMemory): object instance of planner memory

        Returns:
        list:a list of strings indicating the valid actions for satisfying the current step

       """
    print("resolve not cooked")

    if (obj1, obj2) not in obj_preds["IN"]:
        return resolve_not_inside(obj1, obj2, obj_preds, rooms, memory)
    if obj2 in obj_preds["CLOSE"]:
        if obj2 not in obj_preds.get("CLOSED", set()) and obj2 in obj_preds.get("CAN_OPEN", set()):
            return [f"close {obj2}"]
        if obj2 not in obj_preds.get("ON", set()):
            print(obj_preds.get("ON", set()))
            return [f"switchon {obj2}"]
    return resolve_nonvisible(obj2, obj_preds, rooms, memory)

def resolve_wash_obj1_in_obj2(obj1, obj2, obj_preds, rooms, memory = None):
    print("resolve wash")
    if (obj1, obj2) not in obj_preds["IN"]:
        return resolve_not_inside(obj1, obj2, obj_preds, rooms, memory)
    if obj2 not in obj_preds["CAN_OPEN"].intersection(obj_preds["CLOSED"]):
        return [f"close {obj2}"]
    if obj2 not in obj_preds.get("ON", set()):
        return [f"switchon {obj2}"]