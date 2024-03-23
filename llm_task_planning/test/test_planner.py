import time
import numpy as np

from llm_task_planning.planner.pddl_planner import PDDLPlanner
from llm_task_planning.planner.prog_prompt.progprompt_planner import ProgPromptPlanner

from llm_task_planning.planner.utils import parse_response
from llm_task_planning.sim.ai2_thor.ai2thor_sim import AI2ThorSimEnv
from llm_task_planning.sim.utils import get_sim_object
from llm_task_planning.planner.utils import extract_actions
# from llm_task_planning.problem.virtualhome.pddl_virtualhome import VirtualHomeProblem
from pddl.logic import constants, Variable, variables

from goal_gen_aithor import get_make_coffee
def get_put_apple_in_fridge_goal(sim : AI2ThorSimEnv):
    graph = sim.get_graph()
    apple = [node for node in graph["objects"] if "Apple" in node["objectId"]][0]
    fridge = [node for node in graph["objects"] if "Fridge" in node["objectId"]][0]
    print("graph expanded")
    print(fridge)
    goals = [f"INSIDE {apple['objectId']} {fridge['objectId']}"]
    return goals, f"put the {apple['objectId']} in the {fridge['objectId']}."

def get_slice_bread(sim):
    graph = sim.get_graph()
    bread = [node for node in graph["objects"] if "Bread" in node["objectId"]][0]
    goals = [f"SLICED {bread['objectId']}"]
    return goals, f"cut the {bread['objectId']}."

def get_fry_egg_goal(sim):
    graph = sim.get_graph()
    egg = [node for node in graph["objects"] if "Egg" in node["objectId"]][0]
    pan = [node for node in graph["objects"] if "Pan" in node["objectId"]][0]
    stove = [node for node in graph["objects"] if "Stove" in node["objectId"]][0]
    goals = [f"SLICED {egg['objectId']}", f"COOKED {egg['objectId']}|EggCracked_0 {stove['objectId']} {pan['objectId']}"]
    return goals, f"slice the {egg['objectId']} then fry the {egg['objectId']}|EggCracked_0 in the {pan['objectId']}."

def get_make_toast(sim):
    graph = sim.get_graph()
    bread = [node for node in graph["objects"] if "Bread" in node["objectId"]][0]
    toaster = [node for node in graph["objects"] if "Toaster" in node["objectId"]][0]

    goals = [f"SLICED {bread['objectId']}", f"COOKED {bread['objectId']}|BreadSliced_1 {toaster['objectId']}"]
    return goals, f"cut the {bread['objectId']}. And cook {bread['objectId']}|BreadSliced_1 in the {toaster['objectId']}"

# def get_make_coffee(sim):
#     graph = sim.get_graph()
#     cup = [node for node in graph["objects"] if "Mug" in node["objectId"] and node['canFillWithLiquid']][0]
#     coffee_maker = [node for node in graph["objects"] if "CoffeeMachine" in node["objectId"]][0]
#     goals = [f"ON {coffee_maker['objectId']}", f"ON_TOP {cup['objectId']} {coffee_maker['objectId']}"]
#     return goals, f"Fill the {cup['objectId']} in the {coffee_maker['objectId']}"

def get_wash_mug_in_sink_goal(sim):
    graph = sim.get_graph()
    cup = [node for node in graph["objects"] if "Mug" in node["objectId"] and node['canFillWithLiquid']][0]
    sink = [node for node in graph["objects"] if "SinkBasin" in node["objectId"]][0]
    faucet = [node for node in graph["objects"] if "Faucet" in node["objectId"]][0]

    sim.make_object_dirty(cup)
    goals = [f"WASHED_SINK {cup['objectId']} {sink['objectId']} {faucet['objectId']}"]
    return goals, f"Wash the {cup['objectId']} with {faucet['objectId']} in the {sink['objectId']}"

def get_clean_kitchen_goal(sim):
    pass

# problem = VirtualHomeProblem()
sim = AI2ThorSimEnv(scene_index=6, width=680, height=420, save_video=False, use_find=True)

# planner = ProgPromptPlanner(sim)
planner = PDDLPlanner(sim)


# NOTE: CHANGE GOAL HERE
goal = get_wash_mug_in_sink_goal
if sim.save_video:
    sim.image_saver.planner = "ATR"
    sim.image_saver.goal = goal.__name__.replace("get_", "").replace("_goal", "")
parsed_goals, nl_goals = goal(sim)
print(parsed_goals, nl_goals)
# sim.comm.activate_physics(gravity=0)

print(parsed_goals)
planner.set_goal(parsed_goals, nl_goals)
# planner.sim.comm.activate_physics()
print(planner.solve(None))
sim.end_sim()
graph = sim.get_graph()
cup = [node for node in graph["objects"] if "Mug" in node["objectId"]][0]

print(cup)
faucet = [node for node in graph["objects"] if "Faucet" in node["objectId"]][0]
cup = [node for node in graph["objects"] if "Mug" in node["objectId"]][0]
sink = [node for node in graph["objects"] if "SinkBasin" in node["objectId"]][0]
cm = [node for node in graph["objects"] if "CoffeeMachine" in node["objectId"]][0]
print(sim.scene)
print(cup)
print(faucet)
print(sink)
print(cm)
