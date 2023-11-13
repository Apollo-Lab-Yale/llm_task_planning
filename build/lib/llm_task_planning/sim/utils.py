import subprocess
import threading
import time
from numba import njit
from numba.typed import Dict
import psutil
import os
import signal
from threading import Thread
import sys
from copy import deepcopy

UTILITY_SIM_PATH = "/home/liam/installs/virtual_home_exe/linux_exec.v2.2.4.x86_64"

class SimThread(threading.Thread):
    def __init__(self, *args, **keywords):
        threading.Thread.__init__(self, *args, **keywords)
        self.killed = False

    def start(self):
        self.__run_backup = self.run
        self.run = self.__run
        threading.Thread.start(self)

    def __run(self):
        sys.settrace(self.globaltrace)
        self.__run_backup()
        self.run = self.__run_backup

    def globaltrace(self, frame, event, arg):
        if event == 'call':
            return self.localtrace
        else:
            return None

    def localtrace(self, frame, event, arg):
        if self.killed:
            if event == 'line':
                raise SystemExit()
        return self.localtrace

    def kill(self):
        self.killed = True


def start_sim():
    subp = SimThread(target=run_sim)
    subp.run()
    time.sleep(5)
    return subp

def run_sim():
    subp = subprocess.Popen([f"{UTILITY_SIM_PATH}"])


def stop_sim(sim: SimThread):
    print("killing?")
    sim.kill()
    time.sleep(1.0)

# @njit
def get_characters_vhome(graph):
    return [node for node in graph["nodes"] if node["category"].lower() == "characters"]

# @njit
def get_object(graph, object_class):
    return [node for node in graph["nodes"] if node["class_name"] == object_class]

# @njit
def get_object_by_category(graph, object_category):
    return [node for node in graph["nodes"] if node["category"] == object_category]

# @njit
def is_point_in_bounding_box(point, center, size):
    """
    Check if a 3D point is within a bounding box defined by its minimum and maximum coordinates.

    Args:
    point (tuple or list): The 3D point as a tuple or list of (x, y, z) coordinates.
    min_coords (tuple or list): The minimum coordinates of the bounding box.
    max_coords (tuple or list): The maximum coordinates of the bounding box.

    Returns:
    bool: True if the point is inside the bounding box, False otherwise.
    """
    return (
        center[0] - size[0] <= point[0] <= center[0] + size[0] and
        center[1] - size[1] <= point[1] <= center[1] + size[1] and
        center[2] - size[2] <= point[2] <= center[2] + size[2]
    )

# @njit
def filter_state_by_index(graph, index_dict):
    indexes = index_dict.keys()
    return [node for node in graph["nodes"] if f"{node['id']}" in indexes]

# @njit
def build_state(state, edges):
    new_state = []
    formatted_state = {}
    for obj in state:
        new_object = {}
        obj_type = obj["category"].lower()[:-1]
        if obj_type not in ["character", "room"]:
            obj_type = "object"
        new_object["type"] = obj_type
        position = (obj["obj_transform"]["position"], obj['obj_transform']["rotation"])
        predicates = obj["properties"] + obj["states"]
        new_object["position"] = position
        new_object["bounding_box"] = obj["bounding_box"]
        new_object["id"] = obj["id"]
        new_object["name"] = obj["class_name"]
        new_object["predicates"] = predicates
        new_object["relational_predicates"] = {}
        for edge in edges:
            if edge["from_id"] != new_object["id"]:
                continue
            if edge not in new_object["relational_predicates"]:
                new_object["relational_predicates"][edge] = []
            new_object["relational_predicates"][edge].append(edge["to_id"])
        new_state.append(new_object)
    return new_state

def format_state(state, edges, graph):
    new_state = []
    formatted_state = {}
    formatted_state["objects"] = []
    formatted_state["character"] = state[0]
    formatted_state["predicates"] = []
    formatted_state["object_relations"] = []
    id_map = {}
    for edge in edges:
        if (edge["to_id"] not in id_map or edge["from_id"] not in id_map) and (edge["to_id"] != formatted_state["character"]["id"] and edge["from_id"] != formatted_state["character"]["id"] and "HOLDS" not in edge["relation_type"]):
            continue
        new_node = None
        if edge["from_id"] not in id_map:
            new_node = get_node_from_id(graph, edge["from_id"])
            id_map[new_node["id"]] = new_node["class_name"]
        if new_node is not None and "HOLDS" in edge["relation_type"]:
            state.append(new_node)
            new_node = None
        if edge["to_id"] not in id_map:
            new_node = get_node_from_id(graph, edge["to_id"])
            id_map[new_node["id"]] = new_node["class_name"]
        if new_node is not None and "HOLDS" in edge["relation_type"]:
            state.append(new_node)
            new_node = None
        relation = f"{edge['relation_type']} {id_map[edge['from_id']]}_{edge['from_id']} {id_map[edge['to_id']]}_{edge['to_id']}"
        formatted_state["predicates"].append(relation)
        formatted_state["object_relations"].append(relation)
    for obj in state:
        new_object = {}
        obj_type = obj["category"].lower()[:-1]
        if obj_type not in ["character", "room"]:
            obj_type = "object"
        new_object["type"] = obj_type
        position = (obj["obj_transform"]["position"], obj['obj_transform']["rotation"])
        predicates = []
        for pred in obj["properties"]+obj["states"]:
            predicates.append(f"{pred} {obj['class_name']}_{obj['id']}")
        formatted_state["predicates"] += predicates
        new_object["position"] = position
        new_object["bounding_box"] = obj["bounding_box"]
        new_object["id"] = obj["id"]
        new_object["name"] = obj["class_name"]
        new_object["predicates"] = predicates
        new_object["properties"] = obj["properties"]
        new_object["state"] = obj["states"]
        new_object["relational_predicates"] = {}
        id_map[new_object["id"]] = new_object["name"]
        new_state.append(new_object)
    formatted_state["objects"] = new_state

    for edge in edges:
        if edge['from_id'] not in id_map or edge['to_id'] not in id_map:
            continue
        relation = f"{edge['relation_type']} {id_map[edge['from_id']]}_{edge['from_id']} {id_map[edge['to_id']]}_{edge['to_id']}"
        formatted_state["predicates"].append(relation)
        formatted_state["object_relations"].append(relation)
    return formatted_state

def get_node_from_id(graph, id):
    for node in graph["nodes"]:
        if id == node["id"]:
            return node
def get_sim_object(name, nodes, location=None):
    return [node for node in nodes if node["class_name"] == name][-1]


def translate_action_for_sim(action : str, state):
    action = action.replace("?", "").split(" ")
    if "look" in action[0]:
        action[0] = action[0].replace('look', 'turn')
    sim_action = f"<char0> [{action[0]}]"
    for param in action[1:]:
        if param == "character":
            continue
        split_param = param.split("_")
        obj_class, id = None, None
        if len(split_param) <= 1:
            matches = [object for object in state["objects"] if object["name"] == split_param[0]]
            obj_class, id = matches[0]["name"], matches[0]["id"]
        else:
            obj_class, id = split_param
        object_match = [object for object in state["objects"] if object["name"] == obj_class and object["id"] == int(id)]
        goal = object_match[0] if len(object_match) > 0 else None
        if goal is None:
            room_match = [room for room in state["rooms"] if room["class_name"] == obj_class]
            goal = room_match[0]
            goal["name"] = goal["class_name"]
        sim_action += f" <{goal['name'].split('_')[0]}> ({goal['id']})"
    action_list = [sim_action]
    if "turn" in sim_action:
        action_list *= 2

    return action_list

def get_relevant_relations(relations, not_relevant = ("CLOSE", "FACING"), rooms=()):
    filter_relations = [relation for relation in relations if relation.split()[0] in not_relevant or any(room in relation.split() for room in rooms)]
    filtered_relations = deepcopy(relations)
    for relation in filter_relations:
        filtered_relations.remove(relation)
    return filtered_relations

