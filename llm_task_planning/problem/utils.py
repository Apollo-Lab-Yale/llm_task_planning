import re
from pddl.logic.predicates import Predicate
from pddl.logic.base import And, Or, Not
from pddl.core import Action
from pddl.logic.effects import AndEffect
pddl_domain_definition_vhome = '''
(define (domain virtualhome-simulator)
  (:requirements :strips :typing)

  (:types
    character object room pose
  )

    (:predicates
        (CAN_OPEN ?o - object)
        (CLOTHES ?o - object)
        (CONTAINERS ?o - object)
        (COVER_OBJECT ?o - object)
        (CREAM ?o - object)
        (CUTTABLE ?o - object)
        (DRINKABLE ?o - object)
        (EATABLE ?o - object)
        (GRABBABLE ?o - object) ; Whether the object can be grabbed
        (HANGABLE ?o - object)
        (HAS_PAPER ?o - object)
        (HAS_PLUG ?o - object)
        (HAS_SWITCH ?o - object) ; Whether the object can be turned on or off
        (LIEABLE ?o - object)
        (LOOKABLE ?o - object)
        (MOVABLE ?o - object)
        (POURABLE ?o - object)
        (READABLE ?o - object)
        (RECIPIENT ?o - object)
        (SITTABLE ?o - object) ; Whether the agent can sit in this object
        (SURFACE ?o - object) ; Whether the agent can place things on this object
        (OBJECT ?o)
        (ROOM ?r)
        (AGENT ?c)
        (OPEN ?o - object)
        (CLOSED ?o - object)
        (ON ?o - object)
        (OFF ?o - object)
        (VISIBLE ?o - object)
        
        (AT ?char - character ?p - position)

        (ON ?o1 - object ?o2 - object)
        (INSIDE ?o1 - object ?o2 - object)
        (INSIDE ?o1 - object ?r - room)
        (INSIDE ?char - character ?r - room)
        (BETWEEN ?o - object ?r - room) ; for doors
        (CLOSE ?char - character ?o - object) ; char is close to o (< 1.5 metres).
        (CLOSE ?o - object ?o - object) ;
        (FACING ?char - object ?o - object) ; o is visible from char and distance is < 5 metres. If char is a sofa or a chair it should also be turned towards o.
        (HOLDS_RH ?char - character ?o - object) ; char holds o with the right hand.
        (HOLDS_LH ?char - character ?o - object) ; char holds o with the left hand.
        (SITTING ?char - character ?o - object) ; char is sitting in o.

    )
    (:action walk
        :parameters (?char - character ?obj1 - object)
        :precondition (and
            (not (SITTING ?char ?o))
            (not (INSIDE ?obj1 ?o))
            (not (HOLDS_RH ?char ?obj1))
            (not (HOLDS_LH ?char ?obj1))
            (OBJECT ?obj1)
            (AGENT ?char)
            (VISIBLE ?obj1)
        )
        :effect (and
            (CLOSE ?char ?obj1)
            (FACING ?char ?obj1)
        )
    )
    
    (:action walk
        :parameters (?char - character ?r - room)
        :precondition (and
            (not (SITTING ?char ?o))
            (INSIDE ?char ?room)
            (not (HOLDS_RH ?char ?obj1))
            (not (HOLDS_LH ?char ?obj1))
            (ROOM ?r)
            (AGENT ?char)
        )
        :effect (and
            (IN ?char ?r)
            (VISIBLE ?o)
            (OBJECT ?o)
        )
    )

    (:action sit
        :parameters (?char - character ?obj1 - object)
        :precondition (and
            (not (SITTING ?char ?o))
            (CLOSE ?char ?obj1)
            (SITTABLE ?obj1)
            (VISIBLE ?obj1)
            (OBJECT ?obj1)
            (AGENT ?char)
        )
        :effect (SITTING ?char ?obj1)
    )

    (:action standup
        :parameters (?char - character)
        :precondition (SITTING ?char ?o)
        :effect (not (SITTING ?char ?o))
    )

    (:action grab
        :parameters (?char - character ?obj1 - object)
        :precondition (and
            (GRABBABLE ?obj1)
            (CLOSE ?char ?obj1)
            (not (INSIDE ?obj1 ?o))
            (not (HOLDS_RH ?char ?any_obj))
            (VISIBLE ?obj1)
            (OBJECT ?obj1)
            (AGENT ?char)
        )
        :effect (and
            (HOLDS_RH ?char ?obj1)
            (not (ON ?obj1 ?o2))
            (not (INSIDE ?obj1 ?o3))
        )
    )

    (:action open
        :parameters (?char - character ?obj1 - object)
        :precondition (and
            (CAN_OPEN ?obj1)
            (CLOSED ?obj1)
            (CLOSE ?char ?obj1)
            (not (INSIDE ?obj1 ?o))
            (not (HOLDS_RH ?char ?any_obj))
            (VISIBLE ?obj1)
            (OBJECT ?obj1)
            (AGENT ?char)
        )
        :effect(and
            (OPEN ?obj1)
            (VISIBLE ?o)
        )
    )

    (:action close
        :parameters (?char - character ?obj1 - object)
        :precondition (and
            (CAN_OPEN ?obj1)
            (OPEN ?obj1)
            (CLOSE ?char ?obj1)
            (not (INSIDE ?obj1 ?o))
            (VISIBLE ?obj1)
            (OBJECT ?obj1)
            (AGENT ?char)
        )
        :effect (CLOSED ?obj1)
    )

    (:action put
        :parameters (?char - character ?obj1 - object ?obj2 - object)
        :precondition (and
            (HOLDS_RH ?char ?obj1)
            (CLOSE ?char ?obj2)
            (VISIBLE ?obj2)
            (OBJECT ?obj1)
            (AGENT ?char)
            (OBJECT ?obj2)
            
        )
        :effect (and
            (ON ?obj1 ?obj2)
            (not (HOLDS_RH ?char ?obj1))
            (not (HOLDS_LH ?char ?obj1))
        )
    )

    (:action putin
        :parameters (?char - character ?obj1 - object ?obj2 - object)
        :precondition (and
            (HOLDS_RH ?char ?obj1)
            (CLOSE ?char ?obj2)
            (not (CLOSED ?obj2))
            (VISIBLE ?obj2)
            (AGENT ?char)
            (OBJECT ?obj2)
            (OBJECT ?obj1)
            
        )
        :effect (and
            (INSIDE ?obj1 ?obj2)
            (not (HOLDS_RH ?char ?obj1))
            (not (HOLDS_LH ?char ?obj1))
        )
    )

    (:action switchon
        :parameters (?char - character ?obj1 - object)
        :precondition (and
            (HAS_SWITCH ?obj1)
            (OFF ?obj1)
            (CLOSE ?char ?obj1)
            (VISIBLE ?obj1)
            (AGENT ?char)
            (OBJECT ?obj1)
        )
        :effect (ON ?obj1)
    )

    (:action switchoff
        :parameters (?char - character ?obj1 - object)
        :precondition (and
            (HAS_SWITCH ?obj1)
            (ON ?obj1)
            (CLOSE ?char ?obj1)
            (VISIBLE ?obj1)
            (AGENT ?char)
            (OBJECT ?obj1)
        )
        :effect (OFF ?obj1)
    )

    (:action drink
        :parameters (?char - character ?obj1 - object)
        :precondition (and
            (DRINKABLE ?obj1)
            (CLOSE ?char ?obj1)
            (VISIBLE ?obj1)
            (AGENT ?char)
            (OBJECT ?obj1)
        )
        :effect (not (DRINKABLE ?obj1))
    )
    
    (:action turnleft
        :parameters (?char - character)
        :precondition (not (SITTING ?char ?o))
        :effect (VISIBLE ?o)
    )

    (:action turnright
        :parameters (?char - character)
        :precondition (not (SITTING ?char ?o))
        :effect (VISIBLE ?o)
    )
    
    (:action scanroom
        :parameters (?char - character ?o - object)
        :precondition (and
            (not (SITTING ?char ?o))
            (CHARACTER ?char)
            (ROOM ?r)
            (OBJECT ?o)
            (IN ?char ?r)
        )
        :effect (VISIBLE ?o)
    )
)
'''


def predicate_func(predicate, char, obj1, obj2, active_predicates):
    # Mapping for all the predicate functions
    pred_map = {
        "SITTING": lambda: f'SITTING {char} {obj2}' in active_predicates,
        "CLOSE": lambda: f'CLOSE {char} {obj1}' in active_predicates,
        "SITTABLE": lambda: f'SITTABLE {obj1}' in active_predicates,
        "FACING": lambda: f'FACING {char} {obj1}' in active_predicates,
        "INSIDE": lambda: f'INSIDE {obj1} {obj2}' in active_predicates,
        "GRABBABLE": lambda: f'GRABBABLE {obj1}' in active_predicates,
        "HAS_SWITCH": lambda: f'HAS_SWITCH {obj1}' in active_predicates,
        "ON": lambda: f'ON {obj1}' in active_predicates,
        "HOLDS_RH": lambda: f'HOLDS_RH {char} {obj1}' in active_predicates,
        "HOLDS_LH": lambda: f'HOLDS_LH {char} {obj1}' in active_predicates,
        "OPEN": lambda: f'OPEN {obj1}' in active_predicates,
        "CLOSED": lambda: f'CLOSED {obj1}' in active_predicates,
        "DRINKABLE": lambda: f'DRINKABLE {obj1}' in active_predicates,
        "RECIPIENT": lambda: f'RECIPIENT {obj1}' in active_predicates,
        "OFF": lambda: f'OFF {obj1}' in active_predicates,
        "CAN_OPEN": lambda: f'CAN_OPEN {obj1}' in active_predicates
    }

    # Execute the appropriate function and return its result
    return pred_map[predicate]()


def evaluate_action_pddl(pddl_str, active_predicates, char, obj1, obj2 = None):
    # Split the pddl string into predicates and logical constructs
    tokens = [tok.strip() for tok in pddl_str.split('(') if tok]

    # Lists to store evaluations
    evaluations = []
    negations = []  # for handling 'not' constructs

    # Process each token
    for token in tokens:
        predicate = token.split()[0]

        if predicate == 'and':
            continue  # We'll evaluate all 'and' conditions collectively at the end
        elif predicate == 'or':
            # Get the sub-conditions inside the 'or' and evaluate them
            sub_conditions = token[token.find('or') + 2:].strip().split()
            or_results = [predicate_func(cond, char, obj1, obj2, active_predicates) for cond in sub_conditions]
            evaluations.append(any(or_results))
        elif predicate == 'not':
            negations.append(token.split()[1])  # Store the predicate to be negated
        else:
            eval_result = predicate_func(predicate, char, obj1, obj2, active_predicates)
            if predicate in negations:
                evaluations.append(not eval_result)
            else:
                evaluations.append(eval_result)

    # Combine all evaluations using 'and' operation
    result = all(evaluations)
    return result


def parse_pddl_effect(effect_str, nested=False, notted=False):
    # Handle 'and' constructs
    if effect_str.startswith("(false)"):
        return []
    if effect_str.startswith("(and"):
        inner_effects = re.findall(r'\(not \(([^()]+)\)', effect_str[4:])
        parsed_vals = []
        if inner_effects is not None and len(inner_effects) > 0:
            parsed_vals = [parse_pddl_effect(inner, True, True) for inner in inner_effects]
        inner_effects = re.findall(r'\(([^()]+)\)', effect_str[4:])
        return parsed_vals + [parse_pddl_effect(inner, True) for inner in inner_effects if not any([inner.split(" ")[0] in parsed_val for parsed_val in parsed_vals])]

    # Handle 'not' constructs
    if effect_str.startswith("(not"):
        inner_effect = re.match(r'\(not \((.*?)\)\)', effect_str).group(1)
        if nested:
            return (False,) + parse_pddl_effect(inner_effect, True, True)
        else:
            return [(False,) + parse_pddl_effect(inner_effect, True, True)]

    # Handle simple predicates with parentheses around arguments
    match = re.match(r'\((\w+) \?(\w+)( \?(\w+))?\)', effect_str)
    if match:
        predicate, obj1, _, obj2 = match.groups()
        if nested:
            if notted:
                return (False, predicate, obj1, obj2)
            else:
                return (True, predicate, obj1, obj2)
        else:
            if notted:
                return [(False, predicate, obj1, obj2)]

            else:
                return [(True, predicate, obj1, obj2)]

    # Handle simple predicates without parentheses around arguments
    match = re.match(r'not (\w+) \?(\w+) \?(\w+)', effect_str)
    if match:
        predicate, obj1, obj2 = match.groups()
        if nested:
            return (False, predicate, obj1, obj2)
        else:
            return [(False, predicate, obj1, obj2)]

    # Handle simple predicates without parentheses around arguments
    match = re.match(r'(\w+) \?(\w+) \?(\w+)', effect_str)
    if match:
        predicate, obj1, obj2 = match.groups()
        if nested:
            if notted:
                return (False, predicate, obj1, obj2)
            else:
                return (True, predicate, obj1, obj2)

        else:
            if notted:
                return [(False, predicate, obj1, obj2)]

    raise ValueError(f"Unknown PDDL format: {effect_str}")


class PDDLAction:
    def __init__(self, name, parameters, param_types, precondition, effect, param_values=()):
        self.name = name
        self.parameters = parameters
        self.precondition = precondition
        self.effect = effect
        self.param_values = param_values
        self.param_types = param_types

    def satisfies(self, literal, lit_param_types, predicate_map):
        return matches_action_effects(literal, self.effect, predicate_map, lit_param_types)

    def __repr__(self):
        return self.name


def parse_conditions(conditions, is_not=False):
    parsed_conditions = []
    if isinstance(conditions, Predicate):
        values = conditions.__str__().replace("(", "").replace(")", "").split()
        parsed_conditions = [(not is_not, values[0], values[1:])]
    elif isinstance(conditions, tuple):
        for condition in conditions:
            parsed_conditions += parse_conditions(condition)

    elif isinstance(conditions, And) or isinstance(conditions, AndEffect):
        parsed_conditions = parse_conditions(conditions.operands)
    elif isinstance(conditions, Not):
        parsed_conditions = parse_conditions(conditions.argument, is_not or True)

    return parsed_conditions

def parse_pddl_action(action: Action):
    params = [f"?{param.name}" for param in action.parameters]
    param_types = tuple([param_type for param_type in param.type_tags][0] for param in action.parameters)
    return PDDLAction(action.name, params, param_types, parse_conditions(action.precondition), parse_conditions(action.effect))

def parse_instantiated_predicate(predicate_str):
    parts = predicate_str.split()
    predicate_name = parts[0]
    parameters = parts[1:]
    return predicate_name, parameters


def matches_action_effects(literal_str, action_effects, predicate_map, lit_param_types):
    predicate_name, parameters = parse_instantiated_predicate(literal_str)

    for effect in action_effects:
        effect_truth_value, effect_name, effect_parameters = effect
        # Check if the predicate name matches
        if predicate_name == effect_name:
            # Check if the parameters match (assuming parameters are in order

            param_list = [params for params in predicate_map[predicate_name] if params == lit_param_types]
            if len(param_list) > 0:
                print(f"Match found for {literal_str} in {action_effects}")
                return effect_truth_value
    # If no match found, return False
    # print(f"No match found {predicate_str} in {action_effects }")

    return False

CHAR_RELATIONS = ("INSIDE", "HOLDS_RH")
def get_robot_state(state, robot = "character", relations=CHAR_RELATIONS):
    robot_state = ""
    holding = False
    location = None
    for literal in state["object_relations"]:
        if robot in literal:
            relation, params = parse_instantiated_predicate(literal)
            if relation in relations:
                if relation == "HOLDS_RH":
                    holding = True
                    robot_state += f" I am holding {params[1]}."
                else:
                    robot_state += f" I am inside the {params[1]}."
                    location = params[1].replace('.', '')
    if not holding:
        robot_state += " I am not holding anything."
    return robot_state, location
