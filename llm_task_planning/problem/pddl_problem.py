import re
from llm_task_planning.problem.problem_base import ProblemBase
from llm_task_planning.problem.utils import extract_section
from pddl.core import Domain, Problem, Requirements, Action, Predicate, Variable
from pddl import parse_domain, parse_problem
from pddl.formatter import domain_to_string, problem_to_string

class PDDLProblem(ProblemBase):
    def __init__(self, name="PDDL Problem", domain_name="virtualhome"):
        super().__init__()
        self.name = name
        self.problem = None
        self.domain = parse_domain(f"./definitions/{domain_name}-domain.pddl")
        self.problem = None

    def display(self):
        print(domain_to_string(self.domain))
        if self.problem is not None:
            print(problem_to_string(self.problem))
        else:
            print("Problem not initialized")

    def setup_problem(self, name, objects, start_state, goal_state,
                      requirements=(Requirements.STRIPS, Requirements.TYPING)):
        self.problem = Problem(name, domain=self.domain, requirements=requirements,
                               objects=objects, init=start_state, goal=goal_state)

    def set_state(self, obj_name, state):
        self.problem.objects[obj_name].state = state

    def add_object(self, obj_name, obj_type):
        self.problem.objects.extend([Variable(obj_name, obj_type)])

test_problem = PDDLProblem()
test_problem.display()