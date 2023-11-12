from copy import deepcopy, copy
import spacy

from llm_task_planning.problem.utils import parse_instantiated_predicate


nlp = spacy.load('en_core_web_md')
MOVE_ACTION = "walk"
N_ROOMS = 3
N_OBJECTS = 5


def check_close(goal_object, object_relations):
    return any([parse_instantiated_predicate(literal)[0] == "CLOSE"
                    and "character_1" in parse_instantiated_predicate(literal)[1]
                    and f"{goal_object}" in parse_instantiated_predicate(literal)[1] for literal in object_relations])

def check_holding(goal_object, object_relations):
    return any([(parse_instantiated_predicate(literal)[0] == "HOLDS_RH" or parse_instantiated_predicate(literal)[0] == "HOLDS_LH")
                and "character" in parse_instantiated_predicate(literal)[1]
                and f"{goal_object.split('_')[0]}" in parse_instantiated_predicate(literal)[1] for literal in object_relations])

def get_obj_in_hand(object_relations):
    holding =  [parse_instantiated_predicate(literal)[1][1] 
                for literal in object_relations 
                if (parse_instantiated_predicate(literal)[0] == "HOLDS_RH" or
                    parse_instantiated_predicate(literal)[0] == "HOLDS_LH")
                and "character" in parse_instantiated_predicate(literal)[1]]
    return holding[0] if len(holding) > 0 else None

def get_surfaces(objects):
    for object in objects:
        if "SURFACE" in object["properties"]:
            return object
    return None

def get_top_n(d, n):
    top_list = []
    for i in range(n):
        top_list.append(max(d, key=d.get))
        d.pop(top_list[-1])
    return top_list


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

MAX_OBJ_HOLD = 2

def resolve_not_holding(goal, obj_preds, rooms):
    actions = []
    if len(obj_preds["HOLDS"]) == MAX_OBJ_HOLD:
        return resolve_place_object(obj_preds, rooms)
    if goal not in obj_preds["CLOSE"]:
        return resolve_nonvisible(goal, obj_preds, rooms)
    return [f"grab {goal}"]

def resolve_not_inside(obj1, obj2, obj_preds, rooms):
    if obj1 not in obj_preds["HOLDS"]:
        return resolve_not_holding(obj1, obj_preds, rooms)
    if obj2 not in obj_preds["CLOSE"]:
        return resolve_nonvisible(obj2, obj_preds, rooms)
    if obj2 in obj_preds["CAN_OPEN"] and obj2 not in obj_preds["OPEN"]:
        return [f"open {obj2}"]
    return [f"putin {obj1} {obj2}"]

def resolve_not_ontop(obj1, obj2, obj_preds, rooms):
    if obj1 not in obj_preds["HOLDS"]:
        return resolve_not_holding(obj1, obj_preds, rooms)
    if obj2 not in obj_preds["CLOSE"]:
        return resolve_nonvisible(obj2, obj_preds, rooms)
    if obj2 in obj_preds["CAN_OPEN"] and obj2 not in obj_preds["OPEN"]:
        return [f"open {obj2}"]
    return [f"put {obj1} {obj2}"]

def resolve_off(obj1, obj_preds, rooms):
    if obj1 not in obj_preds["CLOSE"]:
        return resolve_nonvisible(obj1, obj_preds, rooms)
    return [f"switchon {obj1}"]

def resolve_on(obj1, obj_preds, rooms):
    if obj1 not in obj_preds["CLOSE"]:
        return resolve_nonvisible(obj1, obj_preds, rooms)
    return [f"switchoff {obj1}"]

def resolve_closed(obj1, obj_preds, rooms):
    if obj1 not in obj_preds["CLOSE"]:
        return resolve_nonvisible(obj1, obj_preds, rooms)
    return [f"open {obj1}"]


def resolve_open(obj1, obj_preds, rooms):
    if obj1 not in obj_preds["CLOSE"]:
        return resolve_nonvisible(obj1, obj_preds, rooms)
    return [f"close {obj1}"]


def add_to_dict(d, key, val_type=set):
    if key not in d:
        d[key] = val_type()
    return d


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
    "ON",
    "OFF",
    "OPEN",
    "CLOSED"
    "FAR",
    "CLOSE"
)

def get_object_properties_and_states(state):
    object_properties_states = {}
    object_properties_states["HOLDS"] = set()
    object_properties_states["CLOSE"] = set()

    for predicate in PREDICATES:
        object_properties_states[predicate] = set()
    for edge in state["object_relations"]:
        relation, params = parse_instantiated_predicate(edge)
        if "HOLDS" in relation:
            if relation not in object_properties_states:
                object_properties_states[relation] = set()
            object_properties_states["HOLDS"].add(params[1])
        if relation == "ON" and len(params) == 2:
            if "ON_TOP" not in object_properties_states:
                object_properties_states["ON_TOP"] = set()
            object_properties_states["ON_TOP"].add(tuple(params))
    for object in state["objects"]:
        is_close = check_close(f"{object['name']}_{object['id']}", state["object_relations"])
        if is_close:
            object_properties_states["CLOSE"].add(f"{object['name']}_{object['id']}")

            for property in object["properties"]:
                if property not in object_properties_states:
                    object_properties_states[property] = set()
                object_properties_states[property].add(f"{object['name']}_{object['id']}")
            for s in object["state"]:
                if s not in object_properties_states:
                    object_properties_states[s] = set()
                object_properties_states[s].add(f"{object['name']}_{object['id']}")
        else:
            if "FAR" not in object_properties_states:
                object_properties_states["FAR"] = set()
            object_properties_states["FAR"].add(f"{object['name']}_{object['id']}")
    return object_properties_states

def get_all_valid_actions(state, goals, current_room="", didScanRoom=False):
    goal_objects = set()
    valid_actions = ["turnleft character", "turnright character"]
    goal_actions = []
    rooms = [f"{room['class_name']}_{room['id']}" for room in state["rooms"]]
    for goal in goals:
        relation, params = parse_instantiated_predicate(goal)
        for param in params:
            if param not in rooms and "character" not in param:
                goal_objects.add(param)

    object_properties_states = get_object_properties_and_states(state)
    for object in object_properties_states["HOLDS"]:
        is_goal = object in goal_objects
        for surface in object_properties_states["SURFACES"].intersection(object_properties_states["CLOSE"]).difference(object_properties_states["HOLDS"]).difference(object_properties_states["CLOSED"]):
            valid_actions.append(f"put {object} {surface}")
            if is_goal:
                goal_actions.append(valid_actions[-1])
    for object in object_properties_states.get("CLOSE", set()):
        is_goal = object in goal_objects
        if object in object_properties_states["HOLDS"]:
            for surface in object_properties_states["SURFACES"].intersection(object_properties_states["CLOSE"]).difference(object_properties_states["CLOSED"]):
                valid_actions.append(f"put {object} {surface}")
                if is_goal:
                    goal_actions.append(valid_actions[-1])
            for storage in object_properties_states["CONTAINERS"].intersection(object_properties_states["CLOSE"]).difference(object_properties_states["CLOSED"]):
                valid_actions.append(f"putin {object} {storage}")
                if is_goal:
                    goal_actions.append(valid_actions[-1])
        if object in object_properties_states["GRABBABLE"].difference(object_properties_states["HOLDS"]):
            valid_actions.append(f"grab character {object}")
            if is_goal:
                goal_actions.append(valid_actions[-1])
        if object in object_properties_states["CAN_OPEN"]:
            if object in object_properties_states["OPEN"]:
                valid_actions.append(f"close character {object}")
            else:
                valid_actions.append(f"open character {object}")
            if is_goal:
                goal_actions.append(valid_actions[-1])
        if object in object_properties_states["HAS_SWITCH"]:
            if object in object_properties_states["ON"]:
                valid_actions.append(f"switchoff character {object}")
            elif object in object_properties_states.get("CLOSED", set()):
                valid_actions.append(f"switchon character {object}")
            if is_goal:
                goal_actions.append(valid_actions[-1])

    for object in object_properties_states.get("FAR", set()):
        is_goal = object in goal_objects
        valid_actions.append(f"walk character {object}")
        if is_goal:
            goal_actions.append(valid_actions[-1])

    for room in rooms:
        if room != current_room:
            valid_actions.append(f"walk character {room}")
    goals_in_close = []
    goals_in_far = []
    # for goal in goals:
    #     relation, params = parse_instantiated_predicate(goal)
    #     for param in params:
    #         if param not in rooms and param not in object_properties_states.get("CLOSE", set()).union(object_properties_states["FAR"]).union(object_properties_states["HOLDS"]):
    #             valid_actions.append(f"scanroom character {param}")
    #             if not didScanRoom:
    #                 goal_actions.append(valid_actions[-1])
    return valid_actions, goal_actions




class ResolutionNode:
    def __init__(self, action=None, children=[], parent=None, literals=[], lit_param_types=[], action_str = ""):
        assert len(literals) == len(lit_param_types)
        self.action = action
        self.children = children
        self.parent = parent
        self.literals = literals
        self.action_str = action_str
        self.lit_param_types = lit_param_types


# TODO: Need to add all the predicates associated with the litteral into the state

def resolution_tree(goal_node, start_literals, start_param_types, actions, predicate_map):
    tree = []
    frontier = [goal_node]  # Convert set to list for modification
    leaf_nodes = []
    while frontier:
        parent = frontier.pop()
        satisfied = []
        for i, literal in enumerate(parent.literals):
            if literal in start_literals:
                satisfied.append(literal)
                continue  # Literal is already satisfied in the start state
            # Find actions that can satisfy the current goal literal
            for action in actions:
                if action.satisfies(literal, parent.lit_param_types[i], predicate_map):
                    action_str = f"{action.name}"
                    for j, param in enumerate(literal.split()[1:]):
                        if action.param_types[j] == parent.lit_param_types[i][j]:
                            action_str += f" {param}"
                        elif "char" in action.param_types[j]:
                            action_str += ""
                    if parent.action_str == action_str:
                        continue
                    new_node = ResolutionNode(parent=parent, action=action, action_str=action_str)
                    parent.children.append(new_node)
                    # Check if action's preconditions are satisfied by start_literals
                    success = True
                    new_unresolved = copy(parent.literals)
                    new_unresolved.remove(literal)
                    for precond in action.precondition:
                        string_literal = f"{precond[1]}"
                        for arg in precond[2]:
                            string_literal += f" {arg}"
                        active = any(precond[1] == literal[0:min(len(precond[1]), len(literal))] and len(precond[2]) == len(literal.split()[1:]) for literal in start_literals)
                        if (active and not precond[0]) or (not active and precond[0]):
                            new_unresolved.append(string_literal)
                            success = False
                    new_node.literals = new_unresolved
                    if success:
                        leaf_nodes.append(new_node)
                        continue
                    # Otherwise, add unsatisfied preconditions to the list of literals to be resolved

    return leaf_nodes

