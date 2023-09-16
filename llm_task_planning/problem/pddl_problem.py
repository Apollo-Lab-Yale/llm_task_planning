import re
from problem_base import ProblemBase
from utils import extract_section


class PDDLProblem(ProblemBase):
    def __init__(self, name="PDDL Problem"):
        super.__init__()
        self.name = name

    def display(self):
        print("Requirements:", self.requirements)
        print("\nConstants:")
        for key, val in self.constants.items():
            print(f"{key} -> {val}")

        print("\nPredicates:")
        for predicate in self.predicates:
            print(predicate)

        print("\nFunctions:")
        for function in self.functions:
            print(function)

        print("\nActions:")
        for action in self.actions:
            action.display()
            print("-" * 30)

        print("\nDerived:")
        for derived in self.derived:
            derived.display()
            print("-" * 30)

    def parse_problem(self, problem_str):
        # Split the domain string by lines and remove whitespace
        lines = [line.strip() for line in problem_str.split('\n') if line.strip()]

        self.parse_requirements(lines)
        self.parse_constants(lines)
        self.parse_predicates_and_functions(lines)
        self.parse_actions(lines)
        self.parse_derived(lines)

    def parse_requirements(self, lines):
        requirements_line = [line for line in lines if line.startswith('(:requirements')][0]
        self.requirements = re.findall(r':\w+', requirements_line)

    def parse_constants(self, lines):
        constants = {}
        constants_lines = extract_section('(:constants', ')', lines)
        for line in constants_lines:
            parts = line.split()
            if len(parts) == 2:  # format: <constant> <type>
                self.constants[parts[0]] = parts[1]

    def parse_predicates_and_functions(self, lines):
        self.predicates = extract_section('(:predicates', ')', lines)
        self.functions = extract_section('(:functions', ')', lines)

    def parse_actions(self, lines):
        action_indices = [i for i, line in enumerate(lines) if line.startswith('(:action')]
        for index in action_indices:
            action = PDDLAction()
            action.name = lines[index].split()[1]
            end_of_action = lines.index(')', index)
            action_lines = lines[index:end_of_action + 1]
            # Extract parameters
            params_line = [line for line in action_lines if line.startswith(':parameters')][0]
            action.parameters = re.findall(r'\?\w+', params_line)

            # Extract preconditions and effects
            action.precondition = extract_section(':precondition', ')', action_lines)
            action.effect = extract_section(':effect', ')', action_lines)

            self.actions.append(action)

    def parse_derived(self, lines):
        derived_indices = [i for i, line in enumerate(lines) if line.startswith('(:derived')]
        for index in derived_indices:
            derived = PDDLDerived()
            derived.name = re.search(r'\((\?\w+)', lines[index + 1]).group(1)
            end_of_derived = lines.index(')', index)
            derived_lines = lines[index:end_of_derived + 1]
            derived.predicate = ' '.join(derived_lines[1:])
            self.derived.append(derived)


class PDDLAction:
    def __init__(self):
        self.name = ''
        self.parameters = []
        self.precondition = []
        self.effect = []

    def display(self):
        print("Name:", self.name)
        print("Parameters:", self.parameters)
        print("Preconditions:", self.precondition)
        print("Effects:", self.effect)


class PDDLDerived:
    def __init__(self):
        self.name = ''
        self.predicate = ''

    def display(self):
        print("Name:", self.name)
        print("Predicate:", self.predicate)
