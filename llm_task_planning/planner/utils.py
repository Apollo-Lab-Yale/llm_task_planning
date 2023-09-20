from numba import njit


@njit
def generate_prompt(state, actions, goal):
    prompt = f"I am an agent acting in an environment, these are the parts of the environment I can see and their status: {state}, I can perform the following actions if the preconditions in the state are satisfied: {actions}, and I am trying to achieve this pddl goal: {goal} what action should I perform?"
    return prompt