import time
import numpy as np

from llm_task_planning.planner.pddl_planner import PDDLPlanner
from llm_task_planning.planner.utils import parse_response
from llm_task_planning.sim.ai2_thor.ai2thor_sim import AI2ThorSimEnv
from llm_task_planning.sim.utils import get_sim_object
from llm_task_planning.planner.utils import extract_actions
from llm_task_planning.problem.virtualhome.pddl_virtualhome import VirtualHomeProblem
from pddl.logic import constants, Variable, variables

def get_put_away_plates_goal(sim):
    goal = 'plate'
    goal_start = "kitchentable"
    goal_location1 = 'kitchencabinet'

    state = sim.get_graph()
    table_node = [node for node in state["nodes"] if node["class_name"]=="kitchentable"][0]
    cabinet_node = [node for node in state["nodes"] if node["class_name"]=="kitchencabinet"][0]
    on_table = [edge["from_id"] for edge in state["edges"] if edge["relation_type"] == "ON" and edge["to_id"] == table_node["id"]]
    plates = [node for node in state["nodes"] if node["id"] in on_table and node["class_name"] == "plate"]
    goals = [f"INSIDE {plate['class_name']}_{plate['id']} {cabinet_node['class_name']}_{cabinet_node['id']}" for plate in plates]
    plates_str = f", ".join([f"{plate['class_name']}_{plate['id']}" for plate in plates[:-1]])
    return goals, f"Put these plates: {plates_str}, and {plates[-1]['class_name']}_{plates[-1]['id']} into the {cabinet_node['class_name']}_{cabinet_node['id']}"

def get_throw_away_pepper_goal(sim):
    graph = sim.get_graph()
    all_trash = [node for node in graph["nodes"] if node["class_name"] == "garbagecan"]
    trash_ids = set([node["id"] for node in all_trash])
    kitchen = [node for node in graph["nodes"] if node["class_name"] == "kitchen"][0]
    kitchen_trash_ids = [edge["from_id"] for edge in graph["edges"] if
                        edge["from_id"] in trash_ids and edge["to_id"] == kitchen["id"]]
    trashcan_node = [tc for tc in all_trash if tc["id"] in kitchen_trash_ids][0]
    new_node = sim.create_waypoint(trashcan_node)
    sim.add_object_waypoint(f"{trashcan_node['class_name']}_{trashcan_node['id']}", f"{new_node['class_name']}_{new_node['id']}")

    pepper = [node for node in graph["nodes"] if node["class_name"] == "bellpepper"][0]
    goals = [f"INSIDE {pepper['class_name']}_{pepper['id']} {trashcan_node['class_name']}_{trashcan_node['id']}"]
    return goals, f"Throw away the apple."

def get_wash_then_put_away_plates_goal(sim):
    goal = 'plate'
    goal_start = "kitchentable"
    goal_location1 = 'kitchencabinet'
    goal_wash_loc = "sink"
    state = sim.get_graph()
    all_sinks = [node for node in state["nodes"] if node["class_name"]=="sink"]
    print(all_sinks)
    sink_ids = set([node["id"] for node in all_sinks])
    kitchen = [node for node in state["nodes"] if node["class_name"]=="kitchen"][0]
    kitchen_sink_ids = [edge["from_id"] for edge in state["edges"] if edge["from_id"] in sink_ids and edge["to_id"] == kitchen["id"]]
    sink_node = [sink for sink in all_sinks if sink["id"] in kitchen_sink_ids][0]
    print(sink_node)
    new_node = sim.create_waypoint(sink_node)
    sim.add_object_waypoint(f"{sink_node['class_name']}_{sink_node['id']}",
                            f"{new_node['class_name']}_{new_node['id']}")
    table_node = [node for node in state["nodes"] if node["class_name"]=="kitchentable"][0]
    cabinet_node = [node for node in state["nodes"] if node["class_name"]=="kitchencabinet"][0]
    on_table = [edge["from_id"] for edge in state["edges"] if edge["relation_type"] == "ON" and edge["to_id"] == table_node["id"]]
    plates = [node for node in state["nodes"] if node["id"] in on_table and node["class_name"] == "plate"]
    goals = [f"WASHED {plate['class_name']}_{plate['id']} {sink_node['class_name']}_{sink_node['id']}" for plate in plates] + [f"INSIDE {plate['class_name']}_{plate['id']} {cabinet_node['class_name']}_{cabinet_node['id']}" for plate in plates]

    plates_str = f", ".join([f"{plate['class_name']}_{plate['id']}" for plate in plates[:-1]])
    return goals, f"Wash these plates: {plates_str}, and {plates[-1]['class_name']}_{plates[-1]['id']} in the {sink_node['class_name']}_{sink_node['id']} then put them into the {cabinet_node['class_name']}_{cabinet_node['id']}"

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
    return goals, f"slice the {bread['objectId']}."

def get_make_toast(sim):
    graph = sim.get_graph()
    bread = [node for node in graph["objects"] if "Bread" in node["objectId"]][0]
    toaster = [node for node in graph["objects"] if "Toaster" in node["objectId"]][0]

    goals = [f"SLICED {bread['objectId']}"]
    return goals, f"slice the {bread['objectId']}."

def get_cook_salmon_in_microwave_goal(sim):
    graph = sim.get_graph()
    salmon = [node for node in graph["nodes"] if node["class_name"] == "salmon"][0]
    microwave = [node for node in graph["nodes"] if node["class_name"] == "microwave"][0]
    goals = [f"COOKED {salmon['class_name']}_{salmon['id']} {microwave['class_name']}_{microwave['id']}"]
    return goals, f"Cook the {salmon['class_name']}_{salmon['id']} in the {microwave['class_name']}_{microwave['id']}."

def get_make_toast_goal(sim):
    graph = sim.get_graph()
    bread = [node for node in graph["nodes"] if node["class_name"] == "breadslice"][0]
    toaster = [node for node in graph["nodes"] if node["class_name"] == "toaster"][0]
    goals = [f"COOKED {bread['class_name']}_{bread['id']} {toaster['class_name']}_{toaster['id']}"]
    return goals, f"Make toast."

def get_cook_salmon_in_microwave_put_on_table_goal(sim):
    graph = sim.get_graph()
    table_node = [node for node in graph["nodes"] if node["class_name"] == "kitchentable"][0]
    new_node = sim.create_waypoint(table_node, offset=(0,1.3,0))
    sim.add_object_waypoint(f"{table_node['class_name']}_{table_node['id']}", f"{new_node['class_name']}_{new_node['id']}")
    salmon = [node for node in graph["nodes"] if node["class_name"] == "salmon"][0]
    microwave = [node for node in graph["nodes"] if node["class_name"] == "microwave"][0]
    goals = [f"COOKED {salmon['class_name']}_{salmon['id']} {microwave['class_name']}_{microwave['id']}", f"ON {salmon['class_name']}_{salmon['id']} {table_node['class_name']}_{table_node['id']}"]
    return goals, f"Cook the {salmon['class_name']}_{salmon['id']} in the {microwave['class_name']}_{microwave['id']}, then put it on the {table_node['class_name']}_{table_node['id']}."

def get_cereal_bowl_livingroom_goal(sim):
    graph = sim.get_graph()
    salmon = [node for node in graph["nodes"] if node["class_name"] == "salmon"][0]
    fridge = [node for node in graph["nodes"] if node["class_name"] == "fridge"][0]
    goals = [f"INSIDE {salmon['class_name']}_{salmon['id']} {fridge['class_name']}_{fridge['id']}"]
    return goals

def get_cook_salmon_put_away_plates_goal(sim):
    graph = sim.get_graph()
    state = graph
    table_node = [node for node in graph["nodes"] if node["class_name"] == "kitchentable"][0]
    new_node = sim.create_waypoint(table_node, offset=(0, 1.3, 0))
    sim.add_object_waypoint(f"{table_node['class_name']}_{table_node['id']}",
                            f"{new_node['class_name']}_{new_node['id']}")
    salmon = [node for node in graph["nodes"] if node["class_name"] == "salmon"][0]
    microwave = [node for node in graph["nodes"] if node["class_name"] == "microwave"][0]
    goals = [f"COOKED {salmon['class_name']}_{salmon['id']} {microwave['class_name']}_{microwave['id']}",
             f"ON {salmon['class_name']}_{salmon['id']} {table_node['class_name']}_{table_node['id']}"]
    table_node = [node for node in state["nodes"] if node["class_name"] == "kitchentable"][0]
    cabinet_node = [node for node in state["nodes"] if node["class_name"] == "kitchencabinet"][0]
    on_table = [edge["from_id"] for edge in state["edges"] if
                edge["relation_type"] == "ON" and edge["to_id"] == table_node["id"]]
    plates = [node for node in state["nodes"] if node["id"] in on_table and node["class_name"] == "plate"]
    goals += [f"INSIDE {plate['class_name']}_{plate['id']} {cabinet_node['class_name']}_{cabinet_node['id']}" for plate
             in plates]
    plates_str = f", ".join([f"{plate['class_name']}_{plate['id']}" for plate in plates[:-1]])
    return (goals,
            f"Cook the {salmon['class_name']}_{salmon['id']} in the {microwave['class_name']}_{microwave['id']}, then put it on the {table_node['class_name']}_{table_node['id']}."
            + f"Put these plates: {plates_str}, and {plates[-1]['class_name']}_{plates[-1]['id']} into the {cabinet_node['class_name']}_{cabinet_node['id']}")



problem = VirtualHomeProblem()
sim = AI2ThorSimEnv()
# bowl = sim.set_up_cereal_env()
planner = PDDLPlanner(sim)
parsed_goals, nl_goals = get_slice_bread(sim)
print(parsed_goals, nl_goals)
# sim.comm.activate_physics(gravity=0)

print(parsed_goals)
planner.set_goal(parsed_goals, nl_goals)
# planner.sim.comm.activate_physics()
print(planner.solve(None))
