import subprocess
import time
from numba import njit
from numba.typed import Dict
import psutil
import os
import signal

UTILITY_SIM_PATH = "/home/liam/installs/virtual_home_exe/linux_exec.v2.2.4.x86_64"

def start_sim():
    subp = subprocess.Popen(f"{UTILITY_SIM_PATH} &", shell = True)
    time.sleep(5)
    print(f"Sub process: {subp.communicate()}")
    return subp

def stop_sim(sim):
    try:
        sim_exe = UTILITY_SIM_PATH.split("/")[-1]
        print(f"here 1 {sim_exe}")
        psutil.process_iter()
        print("here2")
        if sim_exe in (i.name() for i in psutil.process_iter() if i is not None):
            print("here?>")
            sim_proc = [i for i in psutil.process_iter() if i.name() == sim_exe][0]
            os.kill(sim_proc.pid, signal.SIGTERM)
            time.sleep(5)
            if sim_exe in (i.name() for i in psutil.process_iter()):
                os.kill(sim_proc.pid, signal.SIGKILL)
    except Exception as e:
        print(f"Failed to end simulation: {e}")

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