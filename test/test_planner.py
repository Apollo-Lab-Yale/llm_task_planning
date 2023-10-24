from llm_task_planning.planner.pddl_planner import PDDLPlanner
from llm_task_planning.sim.vhome_sim import VirtualHomeSimEnv
from llm_task_planning.planner.utils import extract_actions
from llm_task_planning.problem.virtualhome.pddl_virtualhome import VirtualHomeProblem
from pddl.logic import constants, Variable, variables


problem = VirtualHomeProblem()
sim = VirtualHomeSimEnv(0)
state = sim.get_state()
# for obj in state:
#     problem.add_object()
char = state["objects"][0]
state = "I am in the living room."
goal = {"HOLDS_RH ?character ?milk"}
sim.comm.activate_physics()
planner = PDDLPlanner(problem, sim)
planner.set_goal(goal)
print(planner.solve())