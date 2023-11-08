import time

from llm_task_planning.planner.pddl_planner import PDDLPlanner
from llm_task_planning.sim.vhome_sim import VirtualHomeSimEnv
from llm_task_planning.sim.utils import get_sim_object
from llm_task_planning.planner.utils import extract_actions
from llm_task_planning.problem.virtualhome.pddl_virtualhome import VirtualHomeProblem
from pddl.logic import constants, Variable, variables


problem = VirtualHomeProblem()
sim = VirtualHomeSimEnv(0)

sim.comm.activate_physics()
planner = PDDLPlanner(problem, sim)
goal = 'cereal'
goal_location1 = 'livingroom'
goal_storage = "dishbowl"
goal_obj = get_sim_object(goal, sim.get_graph()["nodes"])
goal_loc_obj = get_sim_object(goal_location1, sim.get_graph()["nodes"])
goal_storage_obj = get_sim_object(goal_storage, sim.get_graph()["nodes"])
# goal_container_object = get_sim_object(goal_storage, sim.get_graph()["nodes"])
goal_lit = {f"INSIDE {goal_obj['class_name']}_{goal_obj['id']} {goal_loc_obj['class_name']}_{goal_loc_obj['id']}", f"INSIDE {goal_obj['class_name']}_{goal_obj['id']} {goal_storage_obj['class_name']}_{goal_storage_obj['id']}"}
nl_goal = {"Bring some cereal in a bowl to the livingroom."}
planner.set_goal(goal_lit, nl_goal)
print(planner.solve())
