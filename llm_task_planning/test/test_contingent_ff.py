import time
import numpy as np

from llm_task_planning.planner.contingent_ff.contingent_ff import ContingentFF
from llm_task_planning.planner.utils import parse_response
from llm_task_planning.sim.vhome_sim import VirtualHomeSimEnv
from llm_task_planning.sim.utils import get_sim_object
from llm_task_planning.planner.utils import extract_actions
from llm_task_planning.problem.virtualhome.pddl_virtualhome import VirtualHomeProblem
from pddl.logic import constants, Variable, variables
from llm_task_planning.test.goal_gen import *

problem_files = ["salmon_cooked_microwave.pddl", "salmon_to_fridge.pddl", "plates_in_cabinet.pddl", "toast_cooked_toaster.pddl", "salmon_cooked_microwave_on_table.pddl"]

sim = VirtualHomeSimEnv(0)
graph = sim.get_graph()
goals, nl_goal = get_cook_salmon_in_microwave_goal(sim)
options = [f"{node['class_name']}_{node['id']}" for node in graph["nodes"] if "Room" in node["category"]]
planner = ContingentFF(sim, options)
planner.set_goal("salmon_cooked_microwave.pddl", options, goals, nl_goal)
planner.solve()
print(len(planner.actions_taken))