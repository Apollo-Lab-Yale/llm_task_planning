from numba import njit


def generate_prompt(actions, goal, abstract_state, rooms, objects):
    sub_state = []
    # for obj in state:
    #     if obj["type"] =="room":
    #         continue
    #     new_obj = {}
    #     new_obj["name"]= obj["name"]
    #     new_obj["predicates"] = obj["predicates"]
    #     sub_state.append(new_obj)
    # if len(str_state) > 4097:
    #     str_state = str_state[:3000]
    prompts = ["I am an agent acting in an environment and I need your help selecting an action.",
               f"this is what I know about my state: {abstract_state}",
               f"these are the rooms I know about: {rooms}",
               f"these are the objects I can see and their predicates: {objects}"[:3000],
               f"and these are the actions I can take: {actions}",
               f"I am trying to achieve this goal: {goal}",
               "Which action should I perform first? please provide your best guess in an easily parsable format"]

    return prompts