from simulation.unity_simulator.comm_unity import UnityCommunication
from llm_task_planning.sim.utils import start_sim, stop_sim, get_characters_vhome, get_object, get_object_by_category, build_state


class VirtualHomeSimEnv:
    def __init__(self, env_idm=0, host="127.0.0.1", port="8080", sim=None):
        if sim is None:
            sim = start_sim()
        self.character_added = False
        self.sim = sim
        self.comm = UnityCommunication(url=host, port=port)
        self.comm.reset(env_idm)
        self.add_character()

    def __del__(self):
        stop_sim(self.sim)

    def validate_plan_syntax(self, plan):
        return plan

    def execute_plan(self, plan, output_video=False):
        plan = self.validate_plan_syntax(plan)
        self.comm.render_script(plan, recording=output_video)

    def add_character(self, model='Chars/Male1'):
        if not self.character_added:
            self.comm.add_character_camera()

        self.comm.add_character(model)
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
        chars = get_characters_vhome(graph)
        visible = self.comm.get_visible_objects(self.comm.camera_count()[1]-1)[1]
        state = chars + visible
        return build_state(state)



