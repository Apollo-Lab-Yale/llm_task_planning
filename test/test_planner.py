from llm_task_planning.planner.pddl_planner import PDDLPlanner
from llm_task_planning.sim.vhome_sim import VirtualHomeSimEnv
from llm_task_planning.planner.utils import extract_actions
from llm_task_planning.problem.virtualhome.pddl_virtualhome import VirtualHomeProblem
from pddl.logic import constants, Variable, variables


problem = VirtualHomeProblem()
sim = VirtualHomeSimEnv(0)
print(problem.domain.predicates)
state = sim.get_state()
# for obj in state:
#     problem.add_object()
char = state["objects"][0]
print(char)
in_pred = [predicate for predicate in problem.domain.predicates if predicate.name == "INSIDE"][0]
char_0 = Variable(f"char", "character")
[living_room, kitchen] = variables("r kitchen", types="room")
state = "I am in the living room."
goal = "I need a glass of water to a user in the living room. Where should I start?"
planner = PDDLPlanner(problem, sim)
planner.set_goal(goal)
planner.set_abstract_state(state)
while True:
    response = planner.get_action_set()
    print(f"actions: {response}")
    for action in response:
        if action not in problem.action_map:
            continue
        if problem.verify_action(problem.action_map[action[0]], sim.get_state()["character"], action[1], action[2] if len(action) > 2 else None):
            print(f"Valid: {action}")
    new_state = input()
    planner.set_abstract_state(new_state)
    print("request sent")