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

        if len(predicate.terms) == 1 and input1["type"] not in predicate.terms[1].type_tags:
            return False

        return predicate.name in input1["predicates"] or (predicate.name in input1["relational_predicates"] and input1["relational_predicates"]["to_id"] == input2["id"])


    def verify_action(self, visible_objects, rooms, current_room, action, param1, param2 = None):
        if action_check is None:
            return False

        if action in ["run", "walk"]:
            return param1["name"] in [obj["name"] for obj in visible_objects] + rooms

        return all(self.verify_predicate(pred) for pred in [action_check.pred])


    def verify_action(self, visible_objects, rooms, character, action, param1, param2 = None):
        if action not in [act.name for act in self.actions]:
            return False
        possible_param1 = [obj for obj in visible_objects if any(obj["id"] in character["relational_predicates"][pred] for pred in character["relational_predicates"])]
        

        return len(possible_params) > 0
