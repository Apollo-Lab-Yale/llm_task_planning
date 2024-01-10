from llm_task_planning.sim.ai2_thor. ai2thor_sim import AI2ThorSimEnv
from llm_task_planning.sim.ai2_thor.utils import get_top_down_frame



sim = AI2ThorSimEnv()
event = sim.turn_left()
graph = sim.get_graph()
for obj in graph["objects"]:
    if obj['salientMaterials'] is not None and 'Food' in obj['salientMaterials']:
        print(obj)
input()