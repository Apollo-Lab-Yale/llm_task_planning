from simulation.unity_simulator.comm_unity import UnityCommunication
from utils import start_sim, stop_sim

class VirtualHomeSimEnv:
    def __init__(self, env_idm, host="127.0.0.1", port="8080", sim=None):
        if sim is None:
            sim = start_sim()

        self.sim = sim
        self.comm = UnityCommunication(url=host, port=port)
        self.comm.reset(env_idm)

    def validate_plan_syntax(self, plan):
        return plan

    def execute_plan(self, plan, output_video=False):
        plan = self.validate_plan_syntax(plan)
        self.comm.render_script(plan, recording=output_video)


