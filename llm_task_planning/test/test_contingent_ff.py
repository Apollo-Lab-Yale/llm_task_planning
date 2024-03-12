import time
import numpy as np

from llm_task_planning.planner.contingent_ff.contingent_ff import ContingentFF
from llm_task_planning.planner.utils import parse_response
from llm_task_planning.sim.vhome_sim import VirtualHomeSimEnv
from llm_task_planning.sim.ai2_thor.ai2thor_sim import AI2ThorSimEnv
from llm_task_planning.sim.utils import get_sim_object
from llm_task_planning.planner.utils import extract_actions
from pddl.logic import constants, Variable, variables
from llm_task_planning.test.goal_gen_ff import *
import uuid

sim = AI2ThorSimEnv(scene_index=6, width=680, height=420, save_video=False, use_find=True)
graph = sim.get_graph()
state = sim.get_state()
options = [f"{room}" for room in state['room_names']]




# NOTE: CHANGE GOAL HERE
goal = get_put_apple_in_fridge_goal

if sim.save_video:
    sim.image_saver.planner = "ContingentFF"
    sim.image_saver.goal = goal.__name__.replace("get_", "").replace("_goal", "")
planner = ContingentFF(sim, options)
goal_objects_pddl, goal_preds_pddl, goal_pddl, goals, nl_goal = goal(sim, planner)

print("got goal")
planner.set_goal(goal_objects_pddl, goal_preds_pddl, goal_pddl, goals, goal_name=goal.__name__ + uuid.uuid4().__str__().split('-')[0], nl_goal=nl_goal)
print("set goal")
print(planner.solve())
sim.end_sim()
print(len(planner.actions_taken))
print([obj for obj in sim.get_graph()["objects"] if "Fridge" in obj["objectId"]])
print([obj for obj in sim.get_graph()["objects"] if "Apple" in obj["objectId"]])
