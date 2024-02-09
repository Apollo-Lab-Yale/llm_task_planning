import time
import numpy as np

from llm_task_planning.planner.contingent_ff.contingent_ff import ContingentFF
from llm_task_planning.planner.utils import parse_response
from llm_task_planning.sim.vhome_sim import VirtualHomeSimEnv
from llm_task_planning.sim.ai2_thor.ai2thor_sim import AI2ThorSimEnv
from llm_task_planning.sim.utils import get_sim_object
from llm_task_planning.planner.utils import extract_actions
from llm_task_planning.problem.virtualhome.pddl_virtualhome import VirtualHomeProblem
from pddl.logic import constants, Variable, variables
from llm_task_planning.test.goal_gen_ff import *


sim = AI2ThorSimEnv(scene_index=-1)
graph = sim.get_graph()
state = sim.get_state()
options = [f"{room}" for room in state['room_names']]

planner = ContingentFF(sim, options)
goal_objects_pddl, goal_preds_pddl, goal_pddl, goals, nl_goal = get_put_apple_in_fridge_goal_ff(sim, planner)

print("got goal")
planner.set_goal(goal_objects_pddl, goal_preds_pddl, goal_pddl, goals, nl_goal)
print("set goal")
print(planner.solve())
print(len(planner.actions_taken))