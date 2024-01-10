from llm_task_planning.sim.ai2_thor.ai2thor_sim import AI2ThorSimEnv

def get_put_apple_in_fridge_goal(sim : AI2ThorSimEnv):
    graph = sim.get_graph()
    apple = [node for node in graph["objects"] if "Apple" in node["objectId"]][0]
    fridge = [node for node in graph["objects"] if "Fridge" in node["objectId"]][0]
    print("graph expanded")
    print(fridge)
    goals = [f"INSIDE {apple['objectId']} {fridge['objectId']}"]
    return goals, f"put the {apple['objectId']} in the {fridge['objectId']}."