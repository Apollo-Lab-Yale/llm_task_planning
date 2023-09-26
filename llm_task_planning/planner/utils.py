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
