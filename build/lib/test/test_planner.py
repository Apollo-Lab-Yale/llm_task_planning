from llm_task_planning.planner.pddl_planner import PDDLPlanner
from llm_task_planning.problem.pddl_problem import PDDLProblem
from llm_task_planning.sim.vhome_sim import VirtualHomeSimEnv


problem = PDDLProblem()
sim = VirtualHomeSimEnv(0)
print(problem.domain.predicates)