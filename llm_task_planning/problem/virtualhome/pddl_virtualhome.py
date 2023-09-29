from llm_task_planning.problem.pddl_problem import PDDLProblem
from llm_task_planning.problem.utils import predicate_func, evaluate_action_pddl, parse_pddl_effect
from pddl.logic.predicates import Predicate

class VirtualHomeProblem(PDDLProblem):
    def __init__(self, name="Virtual Home Problem", domain_name="virtualhome"):
        super().__init__(name, domain_name)
        self.predicate_map = {
            "INSIDE"
        }
    def verify_action(self, action, char, obj1, obj2=None ):
        return evaluate_action_pddl(action.precondition.__str__, char, obj1, obj2)

    def get_valid_actions(self, active_preds, char, target1, target2):
        valid_actions = []
        for action in self.actions:
            if evaluate_action_pddl(action.precondition.__str__(), active_preds, char, target1, target2):
                valid_actions.append((action, char, target1, target2))

    def get_action_effects(self, action):
        return parse_pddl_effect(action.effect.__str__())

    def build_resolution_tree(self):



problem = VirtualHomeProblem()
for action in problem.actions:
    print(problem.actions[action].effect.__str__())
    print(action, parse_pddl_effect(problem.actions[action].effect.__str__()))