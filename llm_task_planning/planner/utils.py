from llm_task_planning.problem.virtualhome.vh_resolution_tree import GOAL_PREDICATES
from llm_task_planning.problem.utils import parse_instantiated_predicate
import re

def extract_actions(text):
    pattern = r'\$\$.*?\$\$'
    matches = re.findall(pattern, text)
    return [match.replace('$$', '').replace('**', '').split(" ")[1:-1] for match in matches]


def generate_next_action_prompt_combined(actions, goal_actions, goal, robot_state, previous_failure="", previous_actions = [], relevant_relations=(), item_states=[]):
    prompts = "I am a robot called character acting in a household environment and I need your help selecting my next atomic action from a limited set to move towards my goal."+\
              robot_state
    if previous_failure != "":
        prompts += '\n'+previous_failure
    if len(previous_actions) > 0:
        prompts += f"\nI have completed the following actions: {previous_actions[-5:]}"

    prompts += '\n' + f"THESE ARE THE ONLY VALID ACTIONS I CAN PERFORM: {actions}"
                # f"This is how these objects relate to each other: {relevant_relations}"+
    prompts += '\n' + f"NOTE the following actions involve a goal object: {goal_actions}" if len(goal_actions) > 0 else ""
    prompts += '\n' +f"The action scanroom if available allows me to visually scan a room to see if an object is visible. Do not perform consecutive scanroom actions."
    prompts += f"Of these actions which should I take to move towards my goal of {goal}. include an explaination for your action selection. Please refrain from getting stuck in action loops and provide your selected action in the format '$$ <action> <object, room, (including id tag) or character> <optional second object (including id tag) depending on action> $$."
    return [prompts]

def generate_next_action_prompt(actions, goal_memory, goal, robot_state, previous_failure="", previous_actions = [], relevant_relations=(), completed_goals=[]):
    prompts = ["I am a robot called character acting in a household environment and I need your help selecting my next atomic action from a limited set to move towards my goal.",
               robot_state]
    if len(completed_goals) > 0:
        prompts += completed_goals
    if len(goal_memory) > 0:
        prompts += [f"The last known predicates of the current goal were: {goal_memory}"]
    if previous_failure != "":
        prompts += [previous_failure]
    # if len(previous_actions) > 0:
    #     prompts += [f"I have completed the following actions: {previous_actions[-10:]}"]

    prompts += [f"Right now I can only perform the following actions: {actions}",
                # f"This is how these objects relate to each other: {relevant_relations}",
                # f"NOTE the following actions involve a goal object: {goal_actions}" if len(goal_actions) > 0 else "",
                # f"The action scanroom if available allows me to visually scan a room to see if an object is visible.", #Do not perform consecutive scanroom actions.",
               f"Of these actions which should I take to move towards my goal of {goal}. include an explaination for your action selection. Please refrain from getting stuck in action loops and provide your selected action in the format 'format '$$ <selected action> $$."]
    if len(goal_memory) > 0:
        prompts += [f"The last known predicates of the current goal were: {goal_memory}"]
    return prompts

def generate_next_action_prompt_short(actions, goal_actions, goal, robot_state, previous_failure="", previous_actions = [], relevant_relations=(), item_states=[]):
    prompts = [f"{robot_state}. I have performed actions: {previous_actions}. To achieve the goal of {goal}, select my next action from the following actions: {actions}. provide your selected action in the format '$$ <selected action> $$."]
    return prompts
def generate_goal_prompt(nl_goal):
    return [f"Break the following goal into algorithmic sub goals for a robot acting in an environment with very limited information: {nl_goal} return your response in a python list of sub goals, excluding all other text"]

def generate_cooked_prompt(cooked):
    cooked_prompts = set()
    # if type(cooked) not in [list, tuple] and cooked is not None:
    #     cooked = [cooked]
    for item in cooked:
        cooked_prompts.add(f"The {item['class_name']}_{item['id']} is cooked!")
    return cooked_prompts

def pddl_relations_to_nl(relations):
    nl_relations = ""
    for edge in relations:
        relation, params = parse_instantiated_predicate(edge)
        if relation == "INSIDE":
            nl_relations += f"The last time I saw the {params[0]} it was inside the {params[1]}"
    return nl_relations

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


def parse_response(text):
    pattern = r'\$\$([^$]+)\$\$'
    matches = re.findall(pattern, text)
    return [match.strip() for match in matches]

def build_goal_pred_prompt(nl_goal):
    return f"""
            Please format the natural laguage goal: {nl_goal}. into some or all of the following goal predicates:
            {GOAL_PREDICATES}
            ONLY INCLUDE RELEVANT PREDICATES. NOTE: ON_TOP AND INSIDE ARE MUTUALLY EXCLUSIVE. format each goal predicate in the format: $$ <complete predicate> $$
            """

def fix_obj1_on_obj2(goals):
    for i in range(len(goals)):
        if "ON_TOP" in goals[i]:
            temp = goals[i]
            temp = temp.replace("ON_TOP", "ON")
            goals[i] = temp
    return goals