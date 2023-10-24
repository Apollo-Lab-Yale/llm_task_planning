from numba import njit

import re

def extract_actions(text):
    pattern = r'\$\$.*?\$\$'
    matches = re.findall(pattern, text)
    return [match.replace('$$', '').replace('**', '').split(" ")[1:-1] for match in matches]

def generate_execution_prompt(actions, goal, abstract_state, rooms, near_objects, visible_objects):
    prompts = ["I am a robot acting in an environment and I need your help selecting my next atomic action to move towards my goal.",
               f"this is what I know about my state: {abstract_state}",
               f"these are the rooms I know about but may not be all the rooms: {rooms}",
               f"these are the objects I can see and their predicates but may not be all the objects: {visible_objects}"[:4096],
               f"and these are the actions I can take, note actions on objects can only be performed on objects I can see and am near: {actions}",
               f"I am trying to achieve this goal: {goal}",
               "Which action should I perform first and on which object or room? please ensure the action is feasible, and that the action's predicates are satisfied. please provide your best guess in the format 'ANSWER: <action> <room or object> <optional second object> END_ANSWER'"]

    return prompts

def generate_action_set_prompt(actions, goal, abstract_state, rooms, near_objects, visible_objects):
    prompts = ["I am a robot acting in an environment and I need your help selecting my next atomic action to move towards my goal.",
               f"this is what I know about my state: {abstract_state}",
               f"these are the rooms I know about but may not be all the rooms: {rooms}",
               f"these are the objects I can see and their predicates but may not be all the objects: {visible_objects}"[:4096],
               f"these are the objects I can interact with, all other visible objects need to be walked to: {near_objects}"
               f"and these are the actions I can take, note actions on objects can only be performed on objects I can see and am near: {actions}",
               f"I am trying to achieve this goal: {goal}",
               "Which actions in my set of actions do you think should I evaluate for feasibility on which objects or rooms. I can only act on the objects that I meantioned that I can see or am near. Please provide each possible action in the form '$$ <action> <object or room> <optional second object depending on action> $$'"]

    return prompts

def generate_next_action_prompt(actions, goal, robot_state, previous_failure=""):
    prompts = ["I am a robot acting in an environment and I need your help selecting my next atomic action to move towards my goal.",
               robot_state]
    if previous_failure != "":
        prompts += [previous_failure]
    prompts += [f"I can take the following actions: {actions}",
               f"Of these actions which should I take to move towards my goal of {goal}. include an explaination for your action selection. Please provide the action in the format '$$ <action> <object or room> <optional second object depending on action> $$."]
    return prompts


def build_precondition_actions_dict_from_list(action_strings):
    precondition_actions = {}

    for pddl_action in action_strings:
        action_details = parse_single_pddl_action(pddl_action)
        action_name = action_details['name']
        for precondition in action_details['preconditions']:
            if precondition not in precondition_actions:
                precondition_actions[precondition] = set()
            precondition_actions[precondition].add(action_name)

    return precondition_actions


def backward_chaining(goal, start, precondition_actions_dict):
    if not goal:
        return []

    current_goal = goal.pop()  # Take one of the goal predicates to satisfy

    # Check if the current goal is already satisfied by the start state
    if current_goal in start:
        return backward_chaining(goal, start, precondition_actions_dict)

    # Find actions that can satisfy the current goal
    if current_goal in precondition_actions_dict:
        actions = precondition_actions_dict[current_goal]

        for action in actions:
            # Build a new goal state with the preconditions of the chosen action
            new_goal = goal.union(action['preconditions'])
            result = backward_chaining(new_goal, start, precondition_actions_dict)
            if result is not None:  # If a valid sequence is found
                return [action['name']] + result

    # If no valid sequence is found
    return None

import re

def parse_single_pddl_action(pddl_str):
    action_name = re.search(r'walk|run|sit|standup|grab|open|close|put|putin|switchon|switchoff|drink|touch|lookat|turnleft|turnright', pddl_str).group(0)
    preconditions = re.findall(r'\(([^()]+)\)', pddl_str)

    return {
        'name': action_name,
        'preconditions': preconditions
    }
def build_precondition_actions_dict_from_list(action_strings):
    precondition_actions = {}

    for pddl_action in action_strings:
        action_details = parse_single_pddl_action(pddl_action)
        action_name = action_details['name']
        for precondition in action_details['preconditions']:
            if precondition not in precondition_actions:
                precondition_actions[precondition] = set()
            precondition_actions[precondition].add(action_name)

    return precondition_actions


def backward_chaining(goal, start, precondition_actions_dict):
    if not goal:
        return []

    current_goal = goal.pop()  # Take one of the goal predicates to satisfy

    # Check if the current goal is already satisfied by the start state
    if current_goal in start:
        return backward_chaining(goal, start, precondition_actions_dict)

    # Find actions that can satisfy the current goal
    if current_goal in precondition_actions_dict:
        actions = precondition_actions_dict[current_goal]

        for action in actions:
            # Build a new goal state with the preconditions of the chosen action
            new_goal = goal.union(action['preconditions'])
            result = backward_chaining(new_goal, start, precondition_actions_dict)
            if result is not None:  # If a valid sequence is found
                return [action['name']] + result

    # If no valid sequence is found
    return None

def parse_response(text):
    pattern = r'\$\$([^$]+)\$\$'
    matches = re.findall(pattern, text)
    return [match.strip() for match in matches]