from llm_task_planning.problem.pddl_problem import PDDLProblem
from llm_task_planning.problem.utils import predicate_func, evaluate_action_pddl, parse_pddl_effect, parse_pddl_action
from llm_task_planning.problem.virtualhome.vh_resolution_tree import resolution_tree, ResolutionNode


class VirtualHomeProblem(PDDLProblem):
    def __init__(self, name="Virtual Home Problem", domain_name="virtualhome"):
        super().__init__(name, domain_name)
        self.predicate_map = {}
        # self.build_predicate_map()

    # def build_predicate_map(self):
    #     for predicate in self.domain.predicates:
    #         pred_param_types = tuple([param_type for param_type in param.type_tags][0] for param in predicate.terms)
    #         name = predicate.name
    #         if name not in self.predicate_map:
    #             self.predicate_map[name] = []
    #         self.predicate_map[name].append(pred_param_types)


    def verify_action(self, action, char, obj1, obj2=None):
        return evaluate_action_pddl(action.precondition.__str__, char, obj1, obj2)

    def get_valid_actions(self, active_preds, char, target1, target2):
        valid_actions = []
        for action in self.actions:
            if evaluate_action_pddl(action.precondition.__str__(), active_preds, char, target1, target2):
                valid_actions.append((action, char, target1, target2))

    def get_action_effects(self, action):
        return parse_pddl_effect(action.effect.__str__())


if __name__ == "__main__":
    problem = VirtualHomeProblem()
    # actions = [parse_pddl_action(action) for action in problem.action_strings]




