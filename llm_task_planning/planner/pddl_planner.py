from llm_task_planning.llm import openai_interface
from llm_task_planning.sim import VirtualHomeSimEnv
from llm_task_planning.problem.virtualhome.pddl_virtualhome import VirtualHomeProblem
from llm_task_planning.problem.virtualhome.vh_resolution_tree import resolve_open, resolve_holding, resolve_nonvisible, resolve_obj_off, resolve_obj_on, resolve_obj1_in_obj2, resolve_obj1_on_obj2
from llm_task_planning.problem.utils import parse_instantiated_predicate
from llm_task_planning.planner.utils import generate_action_set_prompt, generate_execution_prompt, extract_actions
from llm_task_planning.llm import query_model, setup_openai
import numpy as np


class PDDLPlanner:
    def __init__(self, problem : VirtualHomeProblem, sim_env):
        self.problem = problem
        self.sim = sim_env
        self.goal = None
        self.abstract_state = "I am not sure."
        setup_openai()
        self.conversation = []

    def get_next_action(self):
        state = self.sim.get_state()
        objects = [obj for obj in state["objects"] if obj["type"] == "object"]
        rooms = [obj for obj in state["objects"] if obj["type"] == "room"]
        actions = self.problem.actions
        goal = self.goal
        new_prompt = generate_action_set_prompt(actions, goal, self.abstract_state, rooms, objects)
        print("#################################")
        print()
        self.conversation = openai_interface.add_messages_to_conversation(new_prompt, "user", self.conversation)
        print(self.conversation)
        print()
        print("#################################")
        msg_length = sum(len(message["content"]) for message in self.conversation)
        print(msg_length)
        response = query_model(self.conversation)

        print(response)
        self.conversation = openai_interface.add_messages_to_conversation([response["choices"][0]["message"]["content"]], "assistant", [])

    def get_feasible_actions(self, goal):
        state, params = parse_instantiated_predicate(goal)
        for param in params:
            param.replace("?", "")
        if state == "HOLDS_RH":
             return resolve_holding(params[1], self.sim.get_state())
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
