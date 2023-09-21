from llm_task_planning.llm import openai_interface
from llm_task_planning.sim import VirtualHomeSimEnv
from llm_task_planning.problem.pddl_problem import PDDLProblem
from llm_task_planning.planner.utils import generate_prompt
from llm_task_planning.llm import query_model, setup_openai

class PDDLPlanner:
    def __init__(self, problem : PDDLProblem, sim_env):
        self.problem = problem
        self.sim = sim_env
        self.goal = None
        self.abstract_state = "I am not sure."
        setup_openai()

    def get_next_action(self):
        state = self.sim.get_state()
        objects = [obj for obj in state if obj["type"] == "object"]
        rooms = [obj for obj in state if obj["type"] == "room"]
        actions = self.problem.actions
        goal = self.goal
        response = query_model(generate_prompt(actions, goal, self.abstract_state, rooms, objects))
        print(response)

    def set_goal(self, goal):
        self.goal = goal

    def set_abstract_state(self, state):
        self.abstract_state = state
