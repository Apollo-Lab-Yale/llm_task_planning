from llm_task_planning.planner.pddl_planner import PDDLPlanner
from llm_task_planning.sim.vhome_sim import VirtualHomeSimEnv
from llm_task_planning.planner.utils import extract_actions
from llm_task_planning.problem.virtualhome.pddl_virtualhome import VirtualHomeProblem
from pddl.logic import constants, Variable, variables


problem = VirtualHomeProblem()
sim = VirtualHomeSimEnv(0)
print(problem.domain.predicates)
state = sim.get_state()
print(state["object_relations"])
# for obj in state:
#     problem.add_object()
char = state["objects"][0]
print(char)
in_pred = [predicate for predicate in problem.domain.predicates if predicate.name == "INSIDE"][0]
char_0 = Variable(f"char", "character")
[living_room, kitchen] = variables("r kitchen", types="room")
state = "I am in the living room."
goal = {"HOLDS_RH ?character ?milk"}
planner = PDDLPlanner(problem, sim)
planner.set_goal(goal)
print(planner.get_next_action())