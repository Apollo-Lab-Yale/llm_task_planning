from llm_task_planning.sim.ai2_thor.ai2thor_sim import AI2ThorSimEnv
from llm_task_planning.planner.contingent_ff.contingent_ff import ContingentFF

def get_put_apple_in_fridge_goal(sim : AI2ThorSimEnv, planner: ContingentFF):
    graph = sim.get_graph()
    apple = [node for node in graph["objects"] if "Apple" in node["objectId"]][0]
    fridge = [node for node in graph["objects"] if "Fridge" in node["objectId"]][0]
    planner.add_placeholder_id(apple)
    planner.add_placeholder_id(fridge)
    goal_preds_pddl = f"""
        (inside {apple["name"]} kitchen)\n
        (inside {fridge['name']} kitchen)\n
        (closed {fridge['name']})\n
        (grabbable {apple["name"]})\n
        (can_open {fridge['name']})\n
    """
    goal_pddl = f"(inside {apple['name']} {fridge['name']})"
    goal_objects_pddl = f"""
        {apple['name']} - Object\n
        {fridge['name']} - Object\n
        kitchen - Room\n
    """
    goals = [f"INSIDE {apple['objectId']} {fridge['objectId']}"]
    return goal_objects_pddl, goal_preds_pddl, goal_pddl, goals, f"put the {apple['objectId']} in the {fridge['objectId']}."

def get_slice_bread_goal(sim : AI2ThorSimEnv, planner: ContingentFF):
    graph = sim.get_graph()
    bread = [node for node in graph["objects"] if "Bread" in node["objectId"]][0]
    planner.add_placeholder_id(bread)
    goal_preds_pddl = f"""
        (sliceable {bread["name"]})\n
        (inside {bread["name"]} kitchen)\n
    """
    goal_pddl = f"(sliced {bread['name']})"
    goal_objects_pddl = f"""
        {bread['name']} - Object\n
        kitchen - Room\n
    """
    goals = [f"SLICED {bread['objectId']}"]
    return goal_objects_pddl, goal_preds_pddl, goal_pddl, goals, f"slice the {bread['objectId']}."

def get_wash_mug_in_sink_goal(sim, planner):
    graph = sim.get_graph()
    cup = [node for node in graph["objects"] if "Mug" in node["objectId"] and node['canFillWithLiquid']][0]
    sink = [node for node in graph["objects"] if "SinkBasin" in node["objectId"]][0]
    faucet = [node for node in graph["objects"] if "Faucet" in node["objectId"]][0]
    planner.add_placeholder_id(cup)
    planner.add_placeholder_id(sink)
    planner.add_placeholder_id(faucet)

    goal_preds_pddl = f"""
            (inside {cup["name"]} kitchen)\n
            (inside {sink["name"]} kitchen)\n
            (inside {faucet["name"]} kitchen)\n
            (water_source {faucet['name']})\n
            (cleaning_target {sink['name']})\n
            (has_switch {faucet['name']})\n
            (grabbable {cup['name']})\n
            (open {sink['name']})\n
            (off {faucet['name']})\n
            (dirty {cup['name']})\n
        """
    goal_pddl = f"(inside {cup['name']} {sink['name']})\n (ACTIVE {faucet['name']})"
    goal_objects_pddl = f"""
            {cup['name']} - Object\n
            {sink['name']} - Object\n
            {faucet['name']} - Object\n
            
            kitchen - Room\n
        """

    sim.make_object_dirty(cup)
    goals = [f"WASHED_SINK {cup['objectId']} {sink['objectId']} {faucet['objectId']}"]
    return goal_objects_pddl, goal_preds_pddl, goal_pddl, goals, f"Wash the {cup['objectId']} with {faucet['objectId']} in the {sink['objectId']}"


def get_make_coffee(sim, planner):
    graph = sim.get_graph()
    cup = [node for node in graph["objects"] if "Mug" in node["objectId"] and node['canFillWithLiquid']][0]
    coffee_maker = [node for node in graph["objects"] if "CoffeeMachine" in node["objectId"]][0]
    goals = [f"ACTIVE {coffee_maker['objectId']}", f"INSIDE {cup['objectId']} {coffee_maker['objectId']}"]
    goal_preds_pddl = f"""
                (inside {cup["name"]} kitchen)\n
                (inside {coffee_maker["name"]} kitchen)\n
                (has_switch {coffee_maker['name']})\n
                (grabbable {cup['name']})\n
                (open {coffee_maker['name']})\n
                (off {coffee_maker['name']})\n
            """
    planner.add_placeholder_id(cup)
    planner.add_placeholder_id(coffee_maker)

    goal_pddl = f"(INSIDE {cup['name'].lower()} {coffee_maker['name'].lower()})\n (active {coffee_maker['name'].lower()})"
    goal_objects_pddl = f"""
            {cup['name'].lower()} - Object\n
            {coffee_maker['name'].lower()} - Object\n

            kitchen - Room\n
        """

    return goal_objects_pddl, goal_preds_pddl, goal_pddl, goals, f"Make coffee in the {cup['objectId']} with coffee from the {coffee_maker['objectId']}"

def get_make_toast_goal(sim : AI2ThorSimEnv, planner: ContingentFF):
    graph = sim.get_graph()
    bread = [node for node in graph["objects"] if "Bread" in node["objectId"]][0]
    toaster = [node for node in graph["objects"] if "Toaster" in node["objectId"]][0]

    planner.add_placeholder_id(bread)
    planner.add_placeholder_id(toaster)

    goal_preds_pddl = f"""
        (sliceable {bread["name"]})\n
        (inside {bread["name"]} kitchen)\n
        (inside Bread_26_Slice_1 kitchen)\n
        (inside {toaster["name"]} kitchen)\n
        (grabbable Bread_26_Slice_1)\n
        (open {toaster['name']}) \n
        (can_cook {toaster['name']})\n
        (off {toaster['name']})
        (has_switch {toaster['name']})\n
    """
    goal_pddl = f"""
        (sliced {bread["name"]})\n
        (INSIDE Bread_26_Slice_1 {toaster['name']})\n
        (active {toaster['name']})\n
        (cooked Bread_26_Slice_1 {toaster['name']})
    """
    goal_objects_pddl = f"""
        {bread['name']} - Object\n
        kitchen - Room\n
        Bread_26_Slice_1 - Object\n
    """
    goals = [f"SLICED {bread['objectId']}"]
    return goal_objects_pddl, goal_preds_pddl, goal_pddl, goals, f"slice the {bread['objectId']}."