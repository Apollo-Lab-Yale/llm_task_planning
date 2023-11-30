from llm_task_planning.problem.utils import parse_instantiated_predicate, MEMORY_PREDICATES

# todo: what is a good way to represent pose of objects in a way that is a good abstract representation for the last known pose
# - record last known pose for where the object was seen, go back to that pose
# - encode move to last known location of object as an abstract action optoion for LLM

# ^^ is this info useful for the LLM?
# - encode spacial data for where the goal is relative to the robots pose and current pose
# - test adding info to the prompt, add time to recording info

# add info to the prompt and limit filtering


class PlannerMemory:
    def __init__(self):
        self.object_states = {}
        self.rooms = []
        self.object_waypoints = {}

    #itterate through memory, upadate state of visible objects
    def update_memory(self, state):
        self.rooms = state["room_names"]
        memory_update = state["memory_dict"]
        negated = set()
        for obj in memory_update:
            if obj in self.object_states:
                negated.union(self.object_states[obj].difference(memory_update[obj]))
            update = set([pred for pred in memory_update[obj] if tuple(parse_instantiated_predicate(pred))[0] in MEMORY_PREDICATES])
            self.object_states[obj] = update
        # for obj in self.object_states:
        #     self.object_states[obj] = self.object_states[obj].difference(negated)

    def is_object_known(self, obj):
        return False
        # return obj in self.object_states

    def get_object_location(self, obj):
        if not self.is_object_known(obj):
            return None
        location = {"room": None, "container": None}
        for state in self.object_states[obj]:
            if "INSIDE" in state:
                _, params = parse_instantiated_predicate(state)
                if params[0] == obj:
                    where = "room" if params[1] in self.rooms else "container"
                    location[where] = params[1]
        return location

