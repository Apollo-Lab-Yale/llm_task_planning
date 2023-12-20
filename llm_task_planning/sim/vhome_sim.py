# from virtualhome.simulation.unity_simulator.comm_unity import UnityCommunication
from simulation.unity_simulator.comm_unity import UnityCommunication
from llm_task_planning.sim.utils import start_sim, stop_sim, get_characters_vhome, get_object, get_object_by_category, build_state, format_state, UTILITY_SIM_PATH
import sys
import time
import numpy as np


class VirtualHomeSimEnv:
    def __init__(self, env_idm=1, host="127.0.0.1", port="8080", sim=None, no_graphics=False):
        if sim is None:
            sim = start_sim()
        self.no_graphics = no_graphics
        self.character_added = False
        self.sim = sim
        # if not no_graphics:
        self.comm = UnityCommunication(port=port, no_graphics=no_graphics)#, file_name=UTILITY_SIM_PATH)
        # else:
        #     self.comm = UnityCommunication(port=port, no_graphics=no_graphics, file_name=UTILITY_SIM_PATH)
        self.object_waypoints = {}
        self.comm.fast_reset(env_idm)
        print(env_idm)
        self.env_id = env_idm
        self.add_character()
        self.camera_index = self.get_camera_index()
        self.set_view(self.camera_index)

    def __del__(self):
        if not self.no_graphics:
            stop_sim(self.sim)

    def get_camera_index(self, camera_name="Character_Camera_Fwd"):
        camera_indexes = [item for item in range(1, self.comm.camera_count()[1] - 1)]
        success, camera_data = self.comm.camera_data(camera_indexes)
        if not success:
            raise "failed to get camera data."
        for camera in camera_data:
            if camera["name"] == camera_name:
                return camera["index"]
        return -1

    def get_item_state_full(self, item_name = "salmon"):
        graph = self.get_graph()
        salmon = [obj for obj in graph["nodes"] if obj['class_name']==item_name][0]
        salmon_id = salmon['id']
        relations = [relation for relation in graph["edges"] if salmon_id in relation.values()]
        print("*****************")
        print(salmon)
        print(relations)
        print("*****************")

    def add_character(self, model='Chars/Male1', room=None):
        ROOMS = ["kitchen", "bedroom", "bathroom", "livingroom"]
        # if not self.character_added:
        #     self.comm.add_character_camera()
        if room is None:
            room = np.random.choice(ROOMS)
        self.comm.add_character(model, initial_room=room)
        self.character_added = True

    def get_graph(self):
        s, graph = self.comm.environment_graph()
        return graph

    def get_agents(self, graph=None):
        if graph is None:
            graph = self.get_graph()
        get_characters_vhome(graph)

    def get_object_instances(self, object_class, graph=None):
        if graph is None:
            graph = self.get_graph()
        return get_object(graph, object_class)

    def set_view(self, camera=None):
        return
        if camera is None:
            camera = self.comm.camera_count()[1] - 1
        self.comm.camera_image([camera])

    def get_rooms(self, graph=None):
        if graph is None:
            graph = self.get_graph()
        return get_object_by_category(graph, "Room")

    def get_state(self, graph=None, goal_objs=()):
        if graph is None:
            graph = self.get_graph()
        chars = [graph["nodes"][0]]
        rooms = [obj for obj in graph["nodes"] if obj["category"].lower()[:-1] == "room"]
        visible = self.comm.get_visible_objects(self.camera_index)[1]
        visible_ids = set([int(id) for id in visible])
        add_ids = set()
        room_ids = [node["id"] for node in graph["nodes"] if node["category"]=="Rooms"]
        for goal in goal_objs:
            goal_edges = []
            name, id = goal.split("_")
            id = int(id)
            for edge in graph["edges"]:
                relation = edge["relation_type"]
                if id in edge.values() and ((relation == "INSIDE" and edge["to_id"] not in room_ids) or (relation == "CLOSE" and 1 in edge.values())):
                    goal_edges.append(edge)
                if any(edge["relation_type"] == "INSIDE" for edge in goal_edges) and any(edge["relation_type"] == "CLOSE" for edge in goal_edges):
                    container_id = [edge["to_id"] for edge in goal_edges if edge["relation_type"] == "INSIDE"][0]
                    container = [node for node in graph["nodes"] if node["id"] == container_id][0]
                    if "OPEN" in container["states"]:
                        visible_ids.add(int(id))
                        break
        for obj in self.object_waypoints:
            class_name, obj_id = obj.split("_")
            obj_id = int(obj_id)
            waypoint_ids = [int(item.split("_")[1]) for item in self.object_waypoints[obj]]
            if any(w_id in visible_ids for w_id in waypoint_ids):
                visible_ids.add(obj_id)

        visible = [node for node in graph["nodes"] if node['id'] in visible_ids or node["class_name"] == chars[0]["class_name"]]
        edges = [edge for edge in graph["edges"] if edge['from_id'] in visible_ids or edge['to_id'] in visible_ids or chars[0]["id"] == edge['from_id']]
        state = list(visible)
        formatted_state = format_state(state, edges, graph)
        formatted_state["rooms"] = rooms
        formatted_state["room_names"] = [f"{room['class_name']}_{room['id']}" for room in rooms]
        return formatted_state

    def handle_scan_room(self, goal_object, memory):
        for i in range(12):
            self.comm.render_script(["<char0> [turnleft]"], frame_rate=60)
            time.sleep(0.5)
            state = self.get_state()
            memory.update_memory(state)
            if any([f"{object['name']}_{object['id']}" == goal_object or f"{object['name']}_{object['id']}" in self.object_waypoints.get(goal_object, set()) for object in state["objects"]]):
                return True
        return False

    def check_cooked(self):
        state = self.get_graph()
        microwave = [node for node in state["nodes"] if node["class_name"] == "microwave"][0]
        stove = [node for node in state["nodes"] if node["class_name"] == "stove"][0]
        cooked = []
        for edge in state["edges"]:
            if edge["relation_type"] == "INSIDE":
                if edge["to_id"] == stove["id"] and "ON" in stove["states"] and "CLOSED" in stove["states"]:
                    cooked.append(edge["from_id"])
                elif edge["to_id"] == microwave["id"] and "ON" in microwave["states"] and "CLOSED" in microwave["states"]:
                    cooked.append(edge["from_id"])
        return [node for node in state["nodes"] if node["id"] in cooked]

    def add_item(self, class_name="spoon"):
        print("in add item")
        graph = self.get_graph()
        new_node = {
            'id': 1000,
            'class_name': class_name,
            'states': []
        }
        graph["nodes"].insert(0, new_node)
        print("adding id")
        self.comm.expand_scene(graph)
        print("id added")
        return [node for node in self.get_graph()["nodes"] if node["class_name"] == class_name][-1]


    def add_object_waypoint(self, object, waypoint):
        if object not in self.object_waypoints:
            self.object_waypoints[object] = set()
        self.object_waypoints[object].add(waypoint)

    def create_waypoint(self, node, offset=(-0.017001, 1, -0.43), class_name="bellpepper", pose=None):
        graph = self.get_graph()
        new_node = {
            'id': 1000,
            'class_name': class_name,
            'states': []
        }
        graph["nodes"].append(new_node)
        print("adding id")
        self.comm.fast_reset(self.env_id)
        success, msg = self.comm.expand_scene(graph, randomize=True)
        print(f"Expand graph :{success}, msg: {msg}")
        graph = self.get_graph()
        index = [i for i in range(len(graph["nodes"])) if graph["nodes"][i]["class_name"] == class_name]
        index = index[-1]
        new_pose = node["obj_transform"]["position"]
        new_pose = (new_pose[0] + offset[0], new_pose[1] + offset[1], new_pose[2] + offset[2])
        if pose is None:
            pose = new_pose
        graph["nodes"][index]["obj_transform"]["position"] = pose
        self.comm.fast_reset(self.env_id)
        success, msg = self.comm.expand_scene(graph)
        print(f"Expand graph :{success}, msg: {msg}")
        return graph["nodes"][index]

    def put_node1_on_node2(self, node1, node2):
        graph = self.get_graph()
        new_edge = {
            "from_id": node2["id"],
            "to_id": node1["id"],
            'relation_type': "ON"
        }
        graph["edges"].append(new_edge)
        self.comm.expand_scene(graph)

    def set_up_cereal_env(self):
        self.comm.fast_reset(self.env_id)

        graph = self.get_graph()
        new_node = {
            'id': 1000,
            'class_name': "dishbowl",
            'states': []
        }
        cabinet_node = [node for node in graph["nodes"] if node["class_name"] == "microwave"][0]
        new_edge = {
            "from_id": 1000,
            "to_id": cabinet_node["id"],
            'relation_type': "ON"
        }

        graph["nodes"].insert(0, new_node)
        graph["edges"].append(new_edge)
        # time.sleep(5)
        print("adding bowl to graph!")
        self.comm.expand_scene(graph)
        self.add_character()

        return [node for node in self.get_graph()["nodes"] if node["class_name"] == "dishbowl"][-1]