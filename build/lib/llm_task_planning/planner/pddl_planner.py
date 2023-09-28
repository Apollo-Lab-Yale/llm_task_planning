from llm_task_planning.llm import openai_interface
from llm_task_planning.sim import VirtualHomeSimEnv
from llm_task_planning.problem.pddl_problem import PDDLProblem
from llm_task_planning.problem.virtualhome.pddl_virtualhome import VirtualHomeProblem
from llm_task_planning.planner.utils import generate_action_set_prompt
from llm_task_planning.llm import query_model, setup_openai

class PDDLPlanner:
    def __init__(self, problem : VirtualHomeProblem, sim_env):
        self.problem = problem
        self.state = problem.problem.init
        self.sim = sim_env
        self.goal = None
        setup_openai()

    def get_next_action(self):
        state = self.sim.get_state()
        actions = self.problem.actions
        goal = self.problem.problem.goal
        actions = query_model(generate_action_set_prompt(state["objects"], actions, goal))
        for action in actions:
            if self.problem.verify_action(action[0], state["character"], action[1],
                                          action[2] if len(action) > 2 else None):
                return action
        return None

    def validate_action(self, action):
        state = self.sim.get_state()
        return self.problem.
    def set_goal(self, goal):
        self.goal = goal
