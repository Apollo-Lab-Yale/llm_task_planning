import re

def parse_single_pddl_action(pddl_str):
    action_name = re.search(r'walk|run|sit|standup|grab|open|close|put|putin|switchon|switchoff|drink|touch|lookat|turnleft|turnright', pddl_str).group(0)
    preconditions = re.findall(r'\(([^()]+)\)', pddl_str)

    return {
        'name': action_name,
        'preconditions': preconditions
    }