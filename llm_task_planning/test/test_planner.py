import time

from llm_task_planning.planner.pddl_planner import PDDLPlanner
from llm_task_planning.sim.vhome_sim import VirtualHomeSimEnv
from llm_task_planning.sim.utils import get_sim_object
from llm_task_planning.planner.utils import extract_actions
from llm_task_planning.problem.virtualhome.pddl_virtualhome import VirtualHomeProblem
from pddl.logic import constants, Variable, variables


problem = VirtualHomeProblem()
sim = VirtualHomeSimEnv(0)
# bowl = sim.set_up_cereal_env()
sim.comm.activate_physics()
planner = PDDLPlanner(problem, sim)

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
    return goals

def get_put_salmon_in_fridge_goal(sim):
    graph = sim.get_graph()
    salmon = [node for node in graph["nodes"] if node["class_name"] == "salmon"][0]
    fridge = [node for node in graph["nodes"] if node["class_name"] == "fridge"][0]
    goals = [f"INSIDE {salmon['class_name']}_{salmon['id']} {fridge['class_name']}_{fridge['id']}"]
    return goals


def get_cereal_bowl_livingroom_goal(sim):
    graph = sim.get_graph()
    salmon = [node for node in graph["nodes"] if node["class_name"] == "salmon"][0]
    fridge = [node for node in graph["nodes"] if node["class_name"] == "fridge"][0]
    goals = [f"INSIDE {salmon['class_name']}_{salmon['id']} {fridge['class_name']}_{fridge['id']}"]
    return goals

plate_goals = get_put_away_plates_goal(sim)
planner.set_goal(plate_goals, plate_goals)
print(planner.solve())
