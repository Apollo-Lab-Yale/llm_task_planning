from copy import deepcopy, copy
import spacy

from llm_task_planning.problem.utils import parse_instantiated_predicate


nlp = spacy.load('en_core_web_md')
MOVE_ACTION = "walk"
N_ROOMS = 3
N_OBJECTS = 5


def check_close(goal_object, object_relations):
    return any([parse_instantiated_predicate(literal)[0] == "CLOSE"
                    and "?character" in parse_instantiated_predicate(literal)[1]
                    and f"?{goal_object}" in parse_instantiated_predicate(literal)[1] for literal in object_relations])

def check_holding(goal_object, object_relations):
    return any([parse_instantiated_predicate(literal)[0] == "HOLDS_RH"
                and "?character" in parse_instantiated_predicate(literal)[1]
                and f"?{goal_object}" in parse_instantiated_predicate(literal)[1] for literal in object_relations])

def get_obj_in_hand(object_relations):
    holding =  [parse_instantiated_predicate(literal)[1][1] 
                for literal in object_relations 
                if parse_instantiated_predicate(literal)[0] == "HOLDS_RH"
                and "?character" in parse_instantiated_predicate(literal)[1]]
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

def resolve_holding(goal_object, state):
    print(state)
    print(goal_object)
    obj_in_hand = get_obj_in_hand(state["object_relations"])
    if obj_in_hand is not None:
        print(obj_in_hand)
        if obj_in_hand == goal_object:
            return None
        return [f"put ?{obj_in_hand} ?{get_surfaces(state)[0]}"]
    if not any(goal_object == object["name"] for object in state["objects"]):
        print("should be looking for visible")
        return resolve_nonvisible(goal_object, state)
    if not check_close(goal_object, state["object_relations"]):
        return [f"walk ?character ?{goal_object}"]

    return [f"grab ?character ?{goal_object}"]

def resolve_open(goal_object, state):
    if not any(goal_object == object["name"] for object in state["objects"]):
        return resolve_nonvisible(goal_object, state)
    if not check_close(goal_object, state["object_relations"]):
        return [f"walk ?character ?{goal_object}"]
    return [f"open ?character ?{goal_object}"]

def resolve_close(goal_object, state):
    if not any(goal_object == object["name"] for object in state["objects"]):
        return resolve_nonvisible(goal_object, state)
    if not check_close(goal_object, state["object_relations"]):
        return [f"walk ?character ?{goal_object}"]
    return [f"close ?character ?{goal_object}"]

def resolve_obj1_on_obj2(goal_object, goal_location, state):
    holding_res = resolve_holding(goal_object, state)
    if holding_res is not None:
        return holding_res
    if not any(goal_location == object["name"] for object in state["objects"]):
        return resolve_nonvisible(goal_object, state)
    if not check_close(goal_location, state["object_relations"]):
        return [f"walk ?character ?{goal_location} "]
    return [f"put ?{goal_object} ?{goal_location}"]

def resolve_obj1_in_obj2(goal_object, goal_location, state):
    holding_res = resolve_holding(goal_object, state)
    if holding_res is not None:
        return holding_res
    if not any(goal_location == object["name"] for object in state["objects"]):
        return resolve_nonvisible(goal_object, state)
    if not check_close(goal_location, state["object_relations"]):
        return [f"walk ?character ?{goal_location} "]
    obj2 = [object for object in state["objects"] if object["name"] == goal_location][0]
    if "CAN_OPEN" in obj2["properties"] and "OPEN" not in obj2["state"]:
        return resolve_open(goal_location, state)
    return [f"put ?{goal_object} ?{goal_location}"]

def resolve_obj_on(goal_object, state):
    if not any(goal_object == object["name"] for object in state["objects"]):
        return resolve_nonvisible(goal_object, state)
    if not check_close(goal_object, state["object_relations"]):
        return [f"walk ?character ?{goal_object} "]
    return ["switchon ?character ?{goal_object}"]

def resolve_obj_off(goal_object, state):
    if not any(goal_object == object["name"] for object in state["objects"]):
        return resolve_nonvisible(goal_object, state)
    if not check_close(goal_object, state["object_relations"]):
        return [f"walk ?character ?{goal_object} "]
    return [f"switchon ?character ?{goal_object}"]

def resolve_nonvisible(goal_object, state):
    # validate_location -> move to most likely location
    room_literal = [literal for literal in state["object_relations"] if parse_instantiated_predicate(literal)[0] == "INSIDE" and "character" in parse_instantiated_predicate(literal)[1]][0]
    current_room = str(parse_instantiated_predicate(room_literal)[1][1])
    current_room = current_room.replace('?', '')
    rooms = state.get("rooms", [])
    resolution_actions = [f"scanroom ?character ?{current_room}"]
    can_open = []
    can_move = []
    for room in rooms:
        if room != current_room:
            resolution_actions.append(f"walk ?character ?{room}")
    for object in state["objects"]:
        if not object["type"] == "object":
            continue
        is_close = check_close(object["name"], state["object_relations"])
        action = None

        if not is_close:
            resolution_actions.append(f"walk ?character ?{object['name']}")
            continue
        if "CAN_OPEN" in object["properties"]:
            can_open.append(object)
            if is_close:
                action = f"open ?character ?{object['name']}"
            resolution_actions.append(action)
        if "MOVABLE" in object["properties"]:
            can_move.append(object)
            if is_close:
                resolution_actions.append(f"move ?character ?{object}")
    return resolution_actions


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

