from simulation.unity_simulator.comm_unity import UnityCommunication
from llm_task_planning.sim.utils import start_sim, stop_sim, get_characters_vhome, get_object, get_object_by_category, build_state, format_state
import sys

class VirtualHomeSimEnv:
    def __init__(self, env_idm=0, host="127.0.0.1", port="8080", sim=None):
        if sim is None:
            sim = start_sim()
        self.character_added = False
        self.sim = sim
        self.comm = UnityCommunication(url=host, port=port)
        self.comm.reset(env_idm)
        self.add_character()
        self.camera_index = self.get_camera_index()

    def __del__(self):
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
        formatted_state = format_state(state, edges)
        formatted_state["rooms"] = rooms
        return formatted_state