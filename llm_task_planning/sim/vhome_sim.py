# from virtualhome.simulation.unity_simulator.comm_unity import UnityCommunication
from simulation.unity_simulator.comm_unity import UnityCommunication
from llm_task_planning.sim.utils import start_sim, stop_sim, get_characters_vhome, get_object, get_object_by_category, build_state, format_state, UTILITY_SIM_PATH
import sys
import time


class VirtualHomeSimEnv:
    def __init__(self, env_idm=1, host="127.0.0.1", port="8080", sim=None, no_graphics=False):
        if sim is None and not no_graphics:
            sim = start_sim()
        self.no_graphics = no_graphics
        self.character_added = False
        self.sim = sim
        self.comm = UnityCommunication(port=port, no_graphics=no_graphics)#, file_name=UTILITY_SIM_PATH)
        self.comm.reset(env_idm)
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


    def add_character(self, model='Chars/Male1', room="bedroom"):
        if not self.character_added:
            self.comm.add_character_camera()

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
        if camera is None:
            camera = self.comm.camera_count()[1] - 1
        self.comm.camera_image([camera])

    def get_rooms(self, graph=None):
        if graph is None:
            graph = self.get_graph()
        return get_object_by_category(graph, "Room")

    def get_state(self, graph=None):
        if graph is None:
            graph = self.get_graph()
        chars = [graph["nodes"][0]]
        rooms = [obj for obj in graph["nodes"] if obj["category"].lower()[:-1] == "room"]
        visible = self.comm.get_visible_objects(self.camera_index)[1]
        visible_ids = set(visible)
        visible = [node for node in graph["nodes"] if f"{node['id']}" in visible_ids or node["class_name"] == chars[0]["class_name"]]
        edges = [edge for edge in graph["edges"] if f"{edge['from_id']}" in visible_ids or f"{edge['to_id']}" in visible_ids or chars[0]["id"] == edge['from_id'] or chars[0]["id"] == edge['to_id']]
        state = chars + list(visible)
        formatted_state = format_state(state, edges, graph)
        formatted_state["rooms"] = rooms
        formatted_state["room_names"] = [f"{room['class_name']}_{room['id']}" for room in rooms]
        return formatted_state

    def handle_scan_room(self, goal_object):
        for i in range(12):
            self.comm.render_script(["<char0> [turnleft]"])
            time.sleep(0.5)
            state = self.get_state()
            if any([f"{object['name']}_{object['id']}" == goal_object for object in state["objects"]]):
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