
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


class VHResolutionNode:
    def __init__(self):
        self.resolutions = None
        self.previous_action = None
        self.blocking_mode = None

class VHResolutionTree:
    def __init__(self):
        pass