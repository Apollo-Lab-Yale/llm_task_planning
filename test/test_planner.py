from llm_task_planning.planner.pddl_planner import PDDLPlanner
from llm_task_planning.problem.pddl_problem import PDDLProblem, Constant
from llm_task_planning.sim.vhome_sim import VirtualHomeSimEnv
from pddl.logic import constants, Variable, variables


problem = PDDLProblem()
sim = VirtualHomeSimEnv(0)
print(problem.domain.predicates)
state = sim.get_state()
# for obj in state:
#     problem.add_object()
char = state[0]
in_pred = [predicate for predicate in problem.domain.predicates if predicate.name == "INSIDE"][0]
char_0 = Variable(f"char", "character")
[living_room, kitchen] = variables("r kitchen", types="room")
print(problem.domain.constants)
print(living_room)
print(in_pred)
state = "I am in the living room"
goal = "I want to be in the kitchen"
planner = PDDLPlanner(problem, sim)
planner.set_goal(goal)
planner.set_abstract_state(state)
print(planner.get_next_action())