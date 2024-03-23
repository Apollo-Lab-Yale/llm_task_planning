from llm_task_planning.llm import openai_interface
from llm_task_planning.sim import VirtualHomeSimEnv
from llm_task_planning.sim.ai2_thor.ai2thor_sim import AI2ThorSimEnv
from llm_task_planning.sim.utils import translate_action_for_sim, get_relevant_relations
from llm_task_planning.problem.virtualhome.vh_resolution_tree import get_all_valid_actions, resolve_nonvisible, resolve_not_holding, resolve_off, resolve_on, resolve_place_object, resolve_not_ontop, resolve_not_inside, resolve_open, resolve_closed, get_world_predicate_set, resolve_cooked, \
    resolve_wash_obj1_in_obj2, resolve_not_sliced, resolve_wash_in_sink#, get_object_properties_and_states
from llm_task_planning.sim.ai2_thor.utils import get_object_properties_and_states, preds_dict_to_set
from llm_task_planning.sim.ai2_thor.ai2thor_resolution import resolve_no_placement
from llm_task_planning.problem.utils import parse_instantiated_predicate, get_robot_state
from llm_task_planning.planner.utils import extract_actions, generate_next_action_prompt, parse_response, generate_goal_prompt, generate_cooked_prompt, generate_next_action_prompt_combined, \
    generate_next_action_prompt_short, build_goal_pred_prompt, fix_obj1_on_obj2, pddl_relations_to_nl, MSG_FORMAT
from llm_task_planning.planner.planner_memory import PlannerMemory
from llm_task_planning.llm import query_model, setup_openai, OpenAIInterface, get_openai_key
import numpy as np
import time
from PIL import Image

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
    def __init__(self, sim_env, retain_memory=False, model="gpt-3.5-turbo-0125"):
        self.sim = sim_env
        self.goal = []
        self.retain_memory = retain_memory
        self.nl_goal = []
        self.abstract_state = "I am not sure."
        setup_openai()
        self.llm_interface = OpenAIInterface()
        self.conversation = []
        self.actions_taken = []
        self.all_prompts = []
        self.all_llm_responses = []
        self.item_states = set()
        self.last_failure = ""
        self.all_failures = []
        self.max_llm_retry = 5
        self.max_action_steps = 100
        self.abstract_planning_time = 0
        self.sim_planning_time = 0
        self.execution_time = 0
        self.failure_resolutions = []
        self.robot_location = ""
        self.start_state = None
        self.completed_goals = []
        self.rooms_scanned = {}
        self.memory = PlannerMemory()
        self.model_name = model
        self.placeholder_ids = {}
        self.blocking_mode = None

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

    def add_placeholder_id(self, obj, is_concat = True):
        placeholder = obj["name"].lower()
        self.placeholder_ids[placeholder] = obj['objectId']
        return placeholder

    def get_next_action(self, use_all_feasible=False):
        for _ in range(self.max_llm_retry):


            _, goal_objects = parse_instantiated_predicate(self.goal[0])
            state = self.sim.get_state(goal_objs=goal_objects)
            obj_prop_and_states = preds_dict_to_set(get_object_properties_and_states(state))
            self.memory.update_memory(state)
            self.memory.object_waypoints = self.sim.object_waypoints
            robot_state, location = self.sim.get_robot_state(state)
            # self.get_item_states()
            self.robot_location = location
            goal = self.goal
            actions = set()
            sub_goal = goal[0]
            # for sub_goal in goal:
            if not use_all_feasible:
                sub_actions = self.get_feasible_actions(sub_goal, state, self.memory)
            else:
                sub_actions, goal_actions = get_all_valid_actions(state, self.goal, obj_prop_and_states)
                sub_actions = list(sub_actions)
            if sub_actions is None:
                continue
            for i in range(len(sub_actions)):
                if "scanroom" in sub_actions[i]:
                    sub_actions[i] += f" {location}"
            if "scanroom" in self.last_failure and len(self.actions_taken):
                sub_actions = [action for action in sub_actions if action != self.actions_taken[-1]]

            actions = sub_actions

            if len(actions) == 1:
                self.all_failures.append(self.last_failure)
                self.all_prompts.append("")
                self.all_llm_responses.append("")
                self.last_failure = ""
                return list(actions)[0], state
            # rooms = [f"{room['class_name']}_{room['id']}" for room in state["rooms"]]
            relevant_relations = None# pddl_relations_to_nl(get_relevant_relations(state["object_relations"], rooms=rooms))
            actions += ["turnleft character", "turnright character", "moveforward", "movebackward", "turnaround",
                        "lookup", "lookdown"]
            # if use_all_feasible:
            actions = [action for action in actions if action not in self.last_failure]
            actions = [f"$$ {action} $$" for action in actions]# if action not in self.last_failure]
            _, goal_objects = parse_instantiated_predicate(sub_goal)

            print(self.memory.object_states)
            goal_memory = [self.memory.object_states[obj] for obj in goal_objects if obj in self.memory.object_states]
            print(goal_objects)
            print(goal_memory)
            print([self.memory.object_states[obj] for obj in goal_objects if obj in self.memory.object_states])
            new_prompt = generate_next_action_prompt(actions, goal_memory, self.goal, robot_state, self.last_failure, self.actions_taken, obj_prop_and_states, self.completed_goals, scanned_rooms=self.rooms_scanned)
            self.all_prompts.append(f"{new_prompt}")
            if self.last_failure != "":
                if len(self.actions_taken) > 0 and "scanroom" in self.actions_taken[-1]:
                    pass
                else:
                    self.actions_taken.append("")
            self.all_failures.append(self.last_failure)
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
            response = self.llm_interface.query_model(self.conversation, model_name=self.model_name)
            if response is None:
                continue
            print(response)
            # self.all_llm_responses.append(response["choices"][0]["message"]["content"])
            self.all_llm_responses.append(response.choices[0].message.content)

            # try:
            #     response = query_model(self.conversation, model_name=self.model_name, image=Image.fromarray(self.sim.controller.last_event.metadata['frame']))
            #     self.all_llm_responses.append(response["choices"][0]["message"]["content"])
            # except Exception as e:
            #     print(f"Failed to get model response: {e}")
            #     continue
            print(response)
            self.conversation = openai_interface.add_messages_to_conversation([response.choices[0].message.content], "assistant", self.conversation)
            selected_action = parse_response(response.choices[0].message.content)
            if len(selected_action) == 0:
                self.last_failure = f"I failed to complete the previous action because I failed to parse it. Make sure the action is in the format: {MSG_FORMAT}."
                continue
            selected_action = selected_action[0]
            # if selected_action not in actions:
            #     self.last_failure = f"I failed to complete the previous action {selected_action}, because it was not in the list of actions I indicated were feasible in my current state, please ONLY SELECT FROM THE LIST. The object may be inside of something and therefore not visible."
            #     continue
            self.last_failure = ""
            return selected_action, state

    # todo - add failure detection
    def solve(self, args):
        for _ in range(self.max_action_steps):
            # if self.abstract_planning_time > 600:
            #     return False, 1
            sub_goal = self.goal[0]
            _, goal_objects = parse_instantiated_predicate(sub_goal)
            objs = [obj for obj in self.sim.get_graph()['objects'] if obj['objectId'] in sub_goal]
            if any(obj['isBroken'] for obj in objs):
                return False, 1
            abstract_planning_start = time.time()
            ret = self.get_next_action()
            self.abstract_planning_time += time.time() - abstract_planning_start
            if ret is None:
                continue
            (action, state) = ret
            print(f"SimScene: {self.sim.scene}")
            if len(self.actions_taken) > 0 and action == self.actions_taken[-1]:
                ret = self.get_next_action(use_all_feasible=True)
                if ret is None:
                    continue
                action, ret = ret
            success = False
            print(f"returned action: {action}")
            if "scanroom" in action:
                print(f"Executing action: {action}")
                sim_planning_start = time.time()
                try:
                    obj = action.split()[-1] if len(action.split()) == 2 else action.split()[-2]
                except Exception as e:
                    continue
                success, msg = self.sim.handle_scan_room(obj, self.memory)
                print(f"*********** {msg}")
                self.sim_planning_time += time.time() - sim_planning_start
                if obj not in self.rooms_scanned:
                    self.rooms_scanned[obj] = []
                self.rooms_scanned[obj].append(self.robot_location)
                if not success:
                    self.last_failure = f"The action {action} failed. The object is not visible from my current location, do not repeat this action until moving locations."
                self.actions_taken.append(action)
                continue
            sim_action_list = self.sim.translate_action_for_sim(action, state)
            print(f"Executing script: {sim_action_list}")
            sim_planning_start = time.time()
            success, msg = self.sim.execute_actions(sim_action_list, state=self.sim.get_state())
            self.blocking_mode = self.sim.failure_msg_to_blocking_mode(msg, action)
            if success and "put" in action:
                _, objs = parse_instantiated_predicate(action)
                self.sim.add_object_waypoint(objs[0], objs[1])
            self.sim_planning_time += time.time() - sim_planning_start
            self.actions_taken.append(f"{action}")
            if not success:
                print(f"failure message: {msg}")
                # if any("REASON: Path partially completed" in msg[val]["message"] for val in msg):
                #     return False, -1
                self.last_failure = f"I failed to perform action: {action} due to this blocking condition: {msg}"
            satisfied, to_remove = self.sim.check_satisfied(self.sim.get_world_predicate_set(self.sim.get_graph()), self.goal[0])
            if satisfied:
                for sub_goal in to_remove:
                    relation, params = parse_instantiated_predicate(sub_goal)
                    # self.completed_goals.append(f"I successfully completed the pddl goal: {sub_goal}!")
                    self.goal.remove(sub_goal)
            if len(self.goal)==0:
                print("Task success!")
                return True, 0
        print("Max actions taken, task failed.")
        return False, 0


    def handle_blocking_mode(self, object_preds):
        mode, params = parse_instantiated_predicate(self.blocking_mode)
        self.blocking_mode = None
        print("-------------------------------------------------------------------------------------------")
        print(f"{mode}")
        if mode == "no-placement":
            print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
            new_goal = resolve_no_placement(params[0], self.sim.get_state())
            print(new_goal)
            if new_goal is not None:
                self.goal.insert(0, new_goal)
            else:
                self.sim.navigate_to_room(target_room_str=self.sim.single_room)
        return None

    def get_feasible_actions(self, goal, state, memory):
        relation, params = parse_instantiated_predicate(goal)
        obj_preds_dict = get_object_properties_and_states(state)
        obj_preds = preds_dict_to_set(obj_preds_dict)
        print(obj_preds)
        # TODO: Detect unexpected blocking modes and handle for them before addressing the goal
        rooms = state["room_names"]
        for param in params:
            param.replace("?", "")
        if self.blocking_mode is not None:
            self.handle_blocking_mode(obj_preds)
            relation, params = parse_instantiated_predicate(self.goal[0])
        if "HOLDS" in relation:
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
            param3 = None if len(params) < 3 else params[2]
            return resolve_cooked(params[0], params[1], obj_preds, rooms, self.memory, obj3=param3)
        if relation == "WASHED":
            return resolve_wash_obj1_in_obj2(params[0], params[1], obj_preds, rooms, self.memory)
        if relation == "SLICED":
            return resolve_not_sliced(params[0], obj_preds, rooms, self.memory)
        if relation == "WASHED_SINK":
            return resolve_wash_in_sink(params[0], params[1], params[2], obj_preds, rooms, self.memory)
        raise f"No resolution function for relation {relation}."

    def set_goal(self, goal, nl_goal):
        self.goal = goal

        llm_goals = self.query_llm_for_goals(nl_goal)
        if llm_goals is None:
            self.nl_goal = nl_goal
        else:
            self.nl_goal = llm_goals

        # if self.sim.image_saver is not None:
        #     self.sim.image_saver.goal = nl_goal

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