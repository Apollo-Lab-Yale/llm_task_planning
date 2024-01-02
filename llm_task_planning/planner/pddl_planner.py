from llm_task_planning.llm import openai_interface
from llm_task_planning.sim import VirtualHomeSimEnv
from llm_task_planning.sim.utils import translate_action_for_sim, get_relevant_relations
from llm_task_planning.problem.virtualhome.pddl_virtualhome import VirtualHomeProblem
from llm_task_planning.problem.virtualhome.vh_resolution_tree import get_all_valid_actions, resolve_nonvisible, resolve_not_holding, resolve_off, resolve_on, resolve_place_object, resolve_not_ontop, resolve_not_inside, get_object_properties_and_states, resolve_open, resolve_closed, get_world_predicate_set, resolve_cooked, \
    resolve_wash_obj1_in_obj2
from llm_task_planning.problem.utils import parse_instantiated_predicate, get_robot_state
from llm_task_planning.planner.utils import extract_actions, generate_next_action_prompt, parse_response, generate_goal_prompt, generate_cooked_prompt, generate_next_action_prompt_combined, \
    generate_next_action_prompt_short, build_goal_pred_prompt, fix_obj1_on_obj2, pddl_relations_to_nl
from llm_task_planning.planner.planner_memory import PlannerMemory
from llm_task_planning.llm import query_model, setup_openai
import numpy as np
import time

# todo: incorperate "clean x" and "cook y"
## ordering of tasks requires understanding of the context
## avoid object permanance and


'''
option 1:
- ignore issues with object permanence, and memory, and complex tasks like cook + clean
- get a base level paper 
Option2: 
 - try to push this to the limit
 - include memory and object permanence
 - give a week or two try to get THIS DONE 
 - 
 - 
'''


class PDDLPlanner:
    def __init__(self, problem : VirtualHomeProblem, sim_env: VirtualHomeSimEnv, retain_memory=False):
        self.problem = problem
        self.sim = sim_env
        self.goal = set()
        self.retain_memory = retain_memory
        self.nl_goal = set()
        self.abstract_state = "I am not sure."
        setup_openai()
        self.conversation = []
        self.actions_taken = []
        self.all_prompts = []
        self.all_llm_responses = []
        self.item_states = set()
        self.last_failure = ""
        self.all_failures = []
        self.max_llm_retry = 5
        self.max_action_steps = 50
        self.abstract_planning_time = 0
        self.sim_planning_time = 0
        self.execution_time = 0
        self.failure_resolutions = []
        self.robot_location = ""
        self.start_state = None
        self.completed_goals = []
        self.memory = PlannerMemory()

    def reset_data(self):
        self.last_failure = ""
        self.all_failures = []
        self.all_prompts = []
        self.all_llm_responses = []
        self.actions_taken = []
        self.goal = []
        self.abstract_planning_time = 0
        self.sim_planning_time = 0
        self.execution_time = 0
        self.nl_goal = ""

    def get_next_action(self):
        for _ in range(self.max_llm_retry):
            _, goal_objects = parse_instantiated_predicate(self.goal[0])
            state = self.sim.get_state(goal_objs=goal_objects)
            self.memory.update_memory(state)
            self.memory.object_waypoints = self.sim.object_waypoints
            robot_state, location = get_robot_state(state)
            self.get_item_states()
            self.robot_location = location
            goal = self.goal
            actions = set()
            sub_goal = goal[0]
            print([pred for pred in state["predicates"] if any(goal_obj in pred for goal_obj in goal_objects)])
            # for sub_goal in goal:
            sub_actions = self.get_feasible_actions(sub_goal, state, self.memory)
            if sub_actions is None:
                continue
            if "scanroom" in self.last_failure:
                sub_actions = [action for action in sub_actions if action != self.actions_taken[-1]]

            actions = actions.union(set(sub_actions))
            if len(actions) == 1:
                self.all_failures.append(self.last_failure)
                self.all_prompts.append("")
                self.all_llm_responses.append("")
                self.last_failure = ""
                return list(actions)[0], state
            rooms = [f"{room['class_name']}_{room['id']}" for room in state["rooms"]]
            relevant_relations =  pddl_relations_to_nl(get_relevant_relations(state["object_relations"], rooms=rooms))

            _, goal_objects = parse_instantiated_predicate(sub_goal)
            goal_memory = [pddl_relations_to_nl(self.memory.object_states[obj]) for obj in goal_objects if obj in self.memory.object_states]
            print(self.memory.object_states)
            print(goal_objects)
            print(goal_memory)
            print([self.memory.object_states[obj] for obj in goal_objects if obj in self.memory.object_states])
            new_prompt = generate_next_action_prompt(actions, goal_memory, self.goal, robot_state, self.last_failure, self.actions_taken, relevant_relations, self.completed_goals)
            self.all_prompts.append(f"{new_prompt}")
            if self.last_failure != "":
                if len(self.actions_taken) > 0 and "scanroom" in self.actions_taken[-1]:
                    pass
                else:
                    self.actions_taken.append("")
            self.all_failures.append(self.last_failure)
            self.last_failure = ""
            print("#################################")
            print()
            previous_convo = self.conversation if self.retain_memory else []
            self.conversation = openai_interface.add_messages_to_conversation(new_prompt, "user", previous_convo)
            print(self.conversation)
            print()
            print("#################################")
            msg_length = sum(len(message["content"]) for message in self.conversation)
            print(msg_length)
            response = None
            try:
                response = query_model(self.conversation)
                self.all_llm_responses.append(response["choices"][0]["message"]["content"])
            except Exception as e:
                print(f"Failed to get model response: {e}")
                continue
            print(response)
            self.conversation = openai_interface.add_messages_to_conversation([response["choices"][0]["message"]["content"]], "assistant", self.conversation)
            selected_action = parse_response(response["choices"][0]["message"]["content"])
            if len(selected_action) == 0:
                self.last_failure = "I failed to complete the previous action because I failed to parse it. Make sure the action is in the form requested."
                continue
            selected_action = selected_action[0]
            if selected_action not in actions:
                self.last_failure = f"I failed to complete the previous action {selected_action}, because it was not in the set actions I provided. Only select actions that exactly match an entry in the set I provide."
                continue
            return selected_action, state

    # todo - add failure detection
    def solve(self, args):
        self.start_state = self.sim.get_graph()
        for _ in range(self.max_action_steps):
            abstract_planning_start = time.time()
            ret = self.get_next_action()
            self.abstract_planning_time += time.time() - abstract_planning_start
            if ret is None:
                continue
            (action, state) = ret
            success = False
            print(f"returned action: {action}")
            if "scanroom" in action:
                print(f"Executing action: {action}")
                sim_planning_start = time.time()
                success = self.sim.handle_scan_room(action.split()[-1].replace("?",""), self.memory)
                self.sim_planning_time += time.time() - sim_planning_start
                if not success:
                    self.last_failure = f"The action {action} failed. The object is not visible from my current location, do not repeat this action until moving locations."
                self.actions_taken.append(action)
                continue
            sim_action_list = translate_action_for_sim(action, state)
            print(f"Executing script: {sim_action_list}")
            sim_planning_start = time.time()
            success, msg = self.sim.comm.render_script(sim_action_list, frame_rate=60)
            if success and "put" in action:
                _, objs = parse_instantiated_predicate(action)
                self.sim.add_object_waypoint(objs[0], objs[1])
            self.sim_planning_time += time.time() - sim_planning_start
            self.actions_taken.append(f"{action}")
            if not success:
                print(msg)
                if any("REASON: Path partially completed" in msg[val]["message"] for val in msg):
                    return False, -1
                self.last_failure = f"I failed to perform action: {action} due to blocking condition."
            if self.check_satisfied(get_world_predicate_set(self.sim.get_graph())):
                print("Task success!")
                return True, 0
        print("Max actions taken, task failed.")
        return False, 0


    def check_satisfied(self, predicates):
        to_remove = []
        sub_goal = self.goal[0]
        if sub_goal in predicates:
            print(f"{sub_goal} SATISFIED!")
            to_remove.append(sub_goal)
        elif "COOKED" in sub_goal or "WASHED" in sub_goal:
            relation, params = parse_instantiated_predicate(sub_goal)
            if f"INSIDE {params[0]} {params[1]}" in predicates and f"ON {params[1]}" in predicates:
                to_remove.append(sub_goal)
        for sub_goal in to_remove:
            relation, params = parse_instantiated_predicate(sub_goal)
            self.completed_goals.append(f"I successfully completed the pddl goal: {sub_goal}!")
            self.goal.remove(sub_goal)
        return len(self.goal) == 0

    def get_feasible_actions(self, goal, state, memory):
        relation, params = parse_instantiated_predicate(goal)
        obj_preds = get_object_properties_and_states(state)
        rooms = state["room_names"]
        for param in params:
            param.replace("?", "")
        if relation == "HOLDS_RH":
            return resolve_not_holding(params[1], obj_preds, rooms, self.memory)
        if relation == "INSIDE":
            return resolve_not_inside(params[0], params[1], obj_preds, rooms, self.memory)
        if relation == "ON":
            if len(params) == 1:
                return resolve_off(params[0], obj_preds, rooms, self.memory)
            return resolve_not_ontop(params[0], params[1], obj_preds, rooms, self.memory)
        if relation == "OFF":
            return resolve_on(params[0], obj_preds, rooms, self.memory)
        if relation == "OPEN":
            return resolve_closed(params[0], obj_preds, rooms, self.memory)
        if relation == "CLOSED":
            return resolve_open(params[0], obj_preds, rooms, self.memory)
        if relation == "COOKED":
            return resolve_cooked(params[0], params[1], obj_preds, rooms, self.memory)
        if relation == "WASHED":
            return resolve_wash_obj1_in_obj2(params[0], params[1], obj_preds, rooms, self.memory)

    def set_goal(self, goal, nl_goal):
        self.goal = goal
        llm_goals = self.query_llm_for_goals(nl_goal)
        if llm_goals is None:
            self.nl_goal = nl_goal
        else:
            self.nl_goal = llm_goals

    def query_llm_for_goals(self, nl_goal):
        goal_query = generate_goal_prompt(nl_goal)
        conversation = openai_interface.add_messages_to_conversation(goal_query, speaker="user", conversation=[])
        return None
        try:
            response = query_model(conversation)
            return response["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"Failed to get model response for sub goals: {e}")
            return None

    def get_item_states(self):
        self.item_states.union(generate_cooked_prompt(self.sim.check_cooked()))


    def set_abstract_state(self, state):
        self.abstract_state = state

    def get_predicate_goal(self, nl_goal):
        prompt = [build_goal_pred_prompt(nl_goal)]
        conversation = openai_interface.add_messages_to_conversation(prompt, speaker="user", conversation=[])
        response = query_model(conversation)
        print(conversation)
        print(response)
        return fix_obj1_on_obj2(parse_response(response["choices"][0]["message"]["content"]))