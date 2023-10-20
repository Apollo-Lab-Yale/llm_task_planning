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

def format_state(state, edges):
    new_state = []
    formatted_state = {}
    formatted_state["objects"] = []
    formatted_state["character"] = state[0]
    formatted_state["predicates"] = []
    formatted_state["object_relations"] = []
    id_map = {}
    for obj in state:
        new_object = {}
        obj_type = obj["category"].lower()[:-1]
        if obj_type not in ["character", "room"]:
            obj_type = "object"
        new_object["type"] = obj_type
        position = (obj["obj_transform"]["position"], obj['obj_transform']["rotation"])
        predicates = []
        for pred in obj["properties"]+obj["states"]:
            predicates.append(f"{pred} {obj['class_name']}")
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
        if edge["to_id"] not in id_map or edge["from_id"] not in id_map:
            continue
        relation = f"{edge['relation_type']} {id_map[edge['from_id']]} {id_map[edge['to_id']]}"
        formatted_state["predicates"].append(relation)
        formatted_state["object_relations"].append(relation)
    return formatted_state