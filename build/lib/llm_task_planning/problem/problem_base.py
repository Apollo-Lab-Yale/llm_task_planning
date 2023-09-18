from abc import ABC, abstractmethod, abstractproperty


class ProblemBase:
    def __init__(self):
        self.name = ""
        self.requirements = []
        self.constants = {}
        self.predicates = []
        self.functions = []
        self.actions = []
        self.derived = []


    @abstractmethod
    def parse_problem(self, problem):
        pass

    @abstractmethod
    def display(self):
        pass

    @abstractmethod
    def get_actions(self):
        pass