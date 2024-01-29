from llm_task_planning.sim.ai2_thor. ai2thor_sim import AI2ThorSimEnv
from llm_task_planning.sim.ai2_thor.utils import get_top_down_frame, is_in_room, get_room_polygon
import prior

sim = AI2ThorSimEnv(scene_index=-1)
graph = sim.get_graph()
spoon = [obj for obj in graph['objects'] if "spoon" in obj['objectId'].lower()]
fork = [obj for obj in graph['objects'] if "fork" in obj['objectId'].lower()]

print(spoon)
print(fork)
sim.turn_left()
sim.turn_left()
input()
sim.turn_left()
sim.turn_left()

input()