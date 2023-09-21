from llm_task_planning.llm import openai_interface
from llm_task_planning.sim import VirtualHomeSimEnv
from llm_task_planning.problem.pddl_problem import PDDLProblem
from llm_task_planning.planner.utils import generate_prompt
from llm_task_planning.llm import query_model, setup_openai

class PDDLPlanner:
    def __init__(self, problem : PDDLProblem, sim_env):
        self.problem = problem
        self.state = problem.problem.init
        self.sim = sim_env
        self.goal = None
        setup_openai()

    def get_next_action(self):
        state = self.sim.get_state()
        actions = self.problem.actions
        goal = self.problem.problem.goal
        response = query_model(generate_prompt(state, actions, goal))
        print(response)

    def set_goal(self, goal):
        self.goal = goal
