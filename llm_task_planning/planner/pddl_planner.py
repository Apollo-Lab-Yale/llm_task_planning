from llm_task_planning.llm import openai_interface
from llm_task_planning.sim import VirtualHomeSimEnv
from llm_task_planning.sim.utils import translate_action_for_sim
from llm_task_planning.problem.virtualhome.pddl_virtualhome import VirtualHomeProblem
from llm_task_planning.problem.virtualhome.vh_resolution_tree import resolve_open, resolve_holding, resolve_nonvisible, resolve_obj_off, resolve_obj_on, resolve_obj1_in_obj2, resolve_obj1_on_obj2, resolve_close
from llm_task_planning.problem.utils import parse_instantiated_predicate, get_robot_state
from llm_task_planning.planner.utils import generate_action_set_prompt, generate_execution_prompt, extract_actions, generate_next_action_prompt, parse_response
from llm_task_planning.llm import query_model, setup_openai
import numpy as np


class PDDLPlanner:
    def __init__(self, problem : VirtualHomeProblem, sim_env: VirtualHomeSimEnv):
        self.problem = problem
        self.sim = sim_env
        self.goal = None
        self.abstract_state = "I am not sure."
        setup_openai()
        self.conversation = []
        self.last_failure = ""
        self.max_llm_retry = 5
        self.max_action_steps = 20

    def get_next_action(self):
        for _ in range(self.max_llm_retry):
            state = self.sim.get_state()
            robot_state = get_robot_state(state)
            goal = self.goal
            actions = set()
            for sub_goal in goal:
                sub_actions = self.get_feasible_actions(sub_goal, state)
                if sub_actions is None:
                    continue
                actions = actions.union(set(sub_actions))
            new_prompt = generate_next_action_prompt(actions, goal, robot_state, self.last_failure)
            print("#################################")
            print()
            self.conversation = openai_interface.add_messages_to_conversation(new_prompt, "user", self.conversation)
            print(self.conversation)
            print()
            print("#################################")
            msg_length = sum(len(message["content"]) for message in self.conversation)
            print(msg_length)
            response = None
            try:
                response = query_model(self.conversation)
            except Exception as e:
                print(f"Failed to get model response: {e}")
                continue

            print(response)

            self.conversation = openai_interface.add_messages_to_conversation([response["choices"][0]["message"]["content"]], "assistant", self.conversation)
            selected_action = parse_response(response["choices"][0]["message"]["content"])
            if len(selected_action) == 0:
                continue
            selected_action = selected_action[0]
            if selected_action not in actions:
                self.last_failure = f"I failed to complete the previous action {selected_action}, because it was not in the set actions I provided."
                continue
            return selected_action, state

    def solve(self):
        for _ in range(self.max_action_steps):
            action, state = self.get_next_action()
            if action is None:
                continue
            sim_action = translate_action_for_sim(action, state)
            print(f"Executing script: {sim_action}")
            success, msg = self.sim.comm.render_script([sim_action])
            if not success:
                print(msg)
            state = self.sim.get_state()
            if self.check_satisfied(state["predicates"]):
                return True
        return False


    def check_satisfied(self, predicates):
        for sub_goal in self.goal:
            if sub_goal in predicates:
                self.goal.pop(sub_goal)
        return len(self.goal) == 0
    def get_feasible_actions(self, goal, state):
        relation, params = parse_instantiated_predicate(goal)
        for param in params:
            param.replace("?", "")
        if relation == "HOLDS_RH":
            return resolve_holding(params[1], state)
        if relation == "INSIDE":
            return resolve_obj1_in_obj2(params[0], params[1], state)
        if relation == "ON":
            if len(params) == 1:
                return resolve_obj_on(params[0], state)
            return resolve_obj1_on_obj2(params[0], params[1], state)
        if relation == "OFF":
            return resolve_obj_off(params[0], state)
        if relation == "OPEN":
            return resolve_open(params[0], state)
        if relation == "CLOSED":
            return resolve_close(params[0], state)

    def get_action_set(self, state = None):
        state = self.sim.get_state() if state is None else state
        near_objects = {}
        visible_objects = {}
        rooms = []
        char = None
        for object in state["objects"]:
            if char is None and object["type"] == "character":
                char = object
            elif object["type"] == "room":
                rooms.append(object["name"])
            elif object["type"] == "object":
                if char is not None:
                    char_pose = char["position"][0]
                    obj_pose = object["position"][0]
                    if np.sqrt((char_pose[0] - obj_pose[0])**2 + (char_pose[1] - obj_pose[1])**2 + (char_pose[2] - obj_pose[2])**2) < 1:
                        near_objects[object["name"]] = object["predicates"]
                    visible_objects[object["name"]] = object["predicates"]
        actions = self.problem.action_strings
        goal = self.goal

        new_prompt = generate_action_set_prompt(actions, goal, self.abstract_state, rooms, near_objects, visible_objects)
        self.conversation = openai_interface.add_messages_to_conversation(new_prompt, "user", self.conversation)

        msg_length = [len(message["content"]) for message in self.conversation]
        response = query_model(self.conversation)
        self.conversation.pop(-3)
        self.conversation.pop(-3)
        self.conversation.pop(-3)
        print(self.conversation)
        print(response)
        self.conversation = openai_interface.add_messages_to_conversation(
            [response["choices"][0]["message"]["content"]], "assistant", self.conversation)

        return extract_actions(response["choices"][0]["message"]["content"])

    def set_goal(self, goal):
        self.goal = goal

    def set_abstract_state(self, state):
        self.abstract_state = state
