from llm_task_planning.sim.vhome_sim import VirtualHomeSimEnv
from llm_task_planning.test.goal_gen import *

sim = VirtualHomeSimEnv(0)
goal, nl_goal = get_make_toast_goal(sim)
graph = sim.get_graph()
for node in graph['nodes']:
    if node["class_name"] == "kitchentable":
        print(node)
print(goal)
print(nl_goal)