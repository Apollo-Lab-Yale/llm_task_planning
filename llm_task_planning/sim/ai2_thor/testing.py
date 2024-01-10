from llm_task_planning.sim.ai2_thor. ai2thor_sim import AI2ThorSimEnv
from llm_task_planning.sim.ai2_thor.utils import get_top_down_frame



sim = AI2ThorSimEnv()
event = sim.turn_left()
graph = sim.get_graph()
fridge = [node for node in graph["objects"] if "Fridge" in node["objectId"]][0]
sim.navigate_to_object(fridge)
sim.open_object(fridge)
sim.turn_left(degrees=30)
sim.turn_left(degrees=1)
# print(fridge)
input()