from llm_task_planning.llm import openai_interface
from llm_task_planning.sim import VirtualHomeSimEnv
from llm_task_planning.sim.utils import translate_action_for_sim, get_relevant_relations
from llm_task_planning.problem.virtualhome.pddl_virtualhome import VirtualHomeProblem
from llm_task_planning.problem.virtualhome.vh_resolution_tree import resolve_open, resolve_holding, resolve_nonvisible, resolve_obj_off, resolve_obj_on, resolve_obj1_in_obj2, resolve_obj1_on_obj2, resolve_close, get_all_valid_actions
from llm_task_planning.problem.utils import parse_instantiated_predicate, get_robot_state
from llm_task_planning.planner.utils import extract_actions, generate_next_action_prompt, parse_response, generate_goal_prompt, generate_cooked_prompt
from llm_task_planning.llm import query_model, setup_openai
import numpy as np


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
        self.item_states = set()
        self.last_failure = ""
        self.max_llm_retry = 5
        self.max_action_steps = 20
        self.failure_resolutions = []
        self.robot_location = ""
        self.start_state = None

    def get_next_action(self):
        for _ in range(self.max_llm_retry):
            state = self.sim.get_state()
            robot_state, location = get_robot_state(state)
            self.get_item_states()
            self.robot_location = location
            goal = self.goal
            actions = set()
            # for sub_goal in goal:
                # sub_actions = self.get_feasible_actions(sub_goal, state)
                # if sub_actions is None:
                #     continue
                # actions = actions.union(set(sub_actions))
            all_actions, goal_actions = get_all_valid_actions(state, self.goal, current_room=location,
                                                  didScanRoom="scanroom" in self.actions_taken[-1] if len(self.actions_taken) > 0 else False)
            rooms = [f"{room['class_name']}_{room['id']}" for room in state["rooms"]]
            relevant_relations = get_relevant_relations(state["object_relations"], rooms=rooms)
            new_prompt = generate_next_action_prompt(all_actions, goal_actions, self.nl_goal, robot_state, self.last_failure, self.actions_taken, relevant_relations, [f"{self.item_states}"])
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
            if selected_action not in all_actions:
                self.last_failure = f"I failed to complete the previous action {selected_action}, because it was not in the set actions I provided. Only select actions that exactly match an entry in the set I provide."
                continue
            return selected_action, state

    # todo - add failure detection
    def solve(self):
        self.start_state = self.sim.get_graph()
        for _ in range(self.max_action_steps):
            ret = self.get_next_action()
            if ret is None:
                continue
            (action, state) = ret
            print(f"returned action: {action}")
            if "scanroom" in action:
                print(f"Executing action: {action}")
                if not self.sim.handle_scan_room(action.split()[-1].replace("?","")):
                    self.last_failure = f"I failed to find {action.split()[-1].replace('?','')} after performing scanroom. The object is not visible from my current location."
                continue
            sim_action_list = translate_action_for_sim(action, state)
            print(f"Executing script: {sim_action_list}")

            success, msg = self.sim.comm.render_script(sim_action_list,frame_rate=10, camera_mode=["THIRD_PERSON"])
            if not success:
                print(msg)
                self.last_failure = f"I failed to perform action: {action} due to blocking condition."
            state = self.sim.get_state()
            self.actions_taken.append(f"{action} executed in the {self.robot_location}")
            if self.check_satisfied(state["predicates"]):
                print("Task success!")
                return True
        print("Max actions taken, task failed.")
        return False


    def check_satisfied(self, predicates):
        print(predicates)
        for predicate in predicates:
            if predicate in self.goal:
                self.goal.remove(predicate)
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
