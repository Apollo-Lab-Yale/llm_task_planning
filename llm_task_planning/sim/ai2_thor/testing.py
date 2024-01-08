from llm_task_planning.sim.ai2_thor. ai2thor_sim import AI2ThorSimEnv

sim = AI2ThorSimEnv()
sim.turn_right()
input()
print(sim.get_state()["objects"][0])
for object in sim.get_state()["objects"]:
    print(object['name'])
    print(object['parentReceptacles'])
    print(object)
    print()
sim.turn_right()
input()