
implicit_resolutions = {
    "NEAR": ["walk", ]
}

def resolution_tree(goal_literals, start_literals, actions):
    tree = []
    unresolved = list(goal_literals)  # Convert set to list for modification

    while unresolved:
        literal = unresolved.pop()

        if literal in start_literals:
            continue  # Literal is already satisfied in the start state

        # Find actions that can satisfy the current goal literal
        for action in actions:
            if action.satisfies(literal) and action not in tree:
                tree.append(action)
                # Check if action's preconditions are satisfied by start_literals
                if all(precond in start_literals for precond in action.precondition):
                    continue  # This branch is complete
                # Otherwise, add unsatisfied preconditions to the list of literals to be resolved
                unresolved.extend([precond for precond in action.precondition if precond not in start_literals])

    return tree

