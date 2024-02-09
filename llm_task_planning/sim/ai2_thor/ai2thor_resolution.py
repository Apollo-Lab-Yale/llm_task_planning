from llm_task_planning.problem.utils import parse_instantiated_predicate
from llm_task_planning.sim.ai2_thor.utils import CLOSE_DISTANCE, get_vhome_to_thor_dict
from llm_task_planning.problem.virtualhome.vh_resolution_tree import resolve_not_holding

MAX_OBJ_HOLD = 1
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
    object_properties_states['CAN_OPEN'] = {}
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

def resolve_no_placement(target, object_preds):
    contained = [objs[0] for objs in object_preds.get("IN", set()).union(object_preds.get("ON_TOP", set())).intersection(object_preds.get("GRABBABLE", set())) if objs[1] == target]
    if len(contained) == 0:
        return None
    return f"HOLDS character {contained[0]}"