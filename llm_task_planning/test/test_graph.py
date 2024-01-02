from llm_task_planning.planner.pddl_planner import PDDLPlanner
from llm_task_planning.planner.utils import parse_response
from llm_task_planning.sim.vhome_sim import VirtualHomeSimEnv
from llm_task_planning.sim.utils import get_sim_object
from llm_task_planning.planner.utils import extract_actions
from llm_task_planning.problem.virtualhome.pddl_virtualhome import VirtualHomeProblem
from pddl.logic import constants, Variable, variables

problem = VirtualHomeProblem()
sim = VirtualHomeSimEnv(0)

graph = sim.get_graph()
objects = []
predicates = []
for node in graph["nodes"]:
    name = f"{node['class_name']}_{node['id']}"
    if "Room" in node["category"]:
        objects.append(f"{name} - Room")
    if "character" in name:
        objects.append(f"{name} - Character")
    if "SURFACES" in node["properties"]:
        objects.append(f"{name} - Surface")
    if "CONTAINERS" in node["properties"]:
        objects.append(f"{name} - Container")
    else:
        objects.append(f"{name} - Object")
    for state in node["states"] + node["properties"]:
        predicates.append(f"{state.lower()} {name}")

for object in objects:
    print(object)
print('\n\n')
print(predicates)