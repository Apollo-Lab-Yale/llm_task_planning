from llm_task_planning.problem.pddl_problem import PDDLProblem
from pddl.logic.predicates import Predicate

class VirtualHomeProblem(PDDLProblem):
    def __init__(self, name="Virtual Home Problem", domain_name="virtualhome"):
        super().__init__(name, domain_name)
        self.predicate_map = {
            "INSIDE"
        }


    def verify_predicate(self, predicate: Predicate, input1, input2=None):
        if input2 == None and len(predicate.terms) > 1:
            raise f"Too few arguments for predicate {predicate} need 2 received {input1}, {input2}"

        if len(predicate.terms) == 1 and input1["type"] == predicate.terms[]:
            return predicate.name in input1["predicates"]

