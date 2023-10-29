import time

from llm_task_planning.planner.pddl_planner import PDDLPlanner
from llm_task_planning.sim.vhome_sim import VirtualHomeSimEnv
from llm_task_planning.planner.utils import extract_actions
from llm_task_planning.problem.virtualhome.pddl_virtualhome import VirtualHomeProblem
from pddl.logic import constants, Variable, variables


problem = VirtualHomeProblem()
sim = VirtualHomeSimEnv(0)
goal = {"INSIDE salmon fridge"}
nl_goal = {"put the salmon in the fridge"}
sim.comm.activate_physics()
planner = PDDLPlanner(problem, sim)
planner.set_goal(goal, nl_goal)
print(planner.solve())