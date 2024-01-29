import cv2
from ai2thor.controller import Controller
import numpy as np
import time
import prior
from PIL import Image

from llm_task_planning.sim.ai2_thor.utils import get_visible_objects, get_predicates, CLOSE_DISTANCE, find_closest_position, is_in_room, get_yaw_angle, get_vhome_to_thor_dict, get_inf_floor_polygon
from llm_task_planning.problem.utils import parse_instantiated_predicate

def get_ithor_scene_single_room(room, index = -1):
    kitchens = [f"FloorPlan{i}" for i in range(1, 31)]
    living_rooms = [f"FloorPlan{200 + i}" for i in range(1, 31)]
    bedrooms = [f"FloorPlan{300 + i}" for i in range(1, 31)]
    bathrooms = [f"FloorPlan{400 + i}" for i in range(1, 31)]
    rooms = []
    if "kitchen" in room.lower():
        rooms = kitchens
    if "livingroom" in room.lower().replace("_", ""):
        rooms = living_rooms
    if "bedroom" in room.lower():
        rooms = bedrooms
    if "bathroom" in room.lower():
        rooms = bathrooms
    assert len(rooms) > 0
    index = np.random.uniform(1, 30) if index == -1 else index
    return rooms[int(index)]

class AI2ThorSimEnv:
    def __init__(self, scene_index=3, width=600, height=600, gridSize=0.25, visibilityDistance=10, single_room='kitchen'):
        self.single_room = single_room
        self.scene = None
        self.controller = None
        self.comm = self
        self.reset(scene_index, width, height, gridSize, visibilityDistance, single_room)
        self.valid_positions = self.get_valid_positions()
        self.object_waypoints = {}
        self.action_fn_from_str = {
            "walk_to_room": self.navigate_to_room,
            "walk_to_object": self.navigate_to_object,
            "grab": self.grab_object,
            "turnleft": self.turn_left,
            "turnright": self.turn_right,
            "put": self.place_object,
            "putin": self.place_object,
            "open": self.open_object,
            "close": self.close_object,
            "cook": self.cook_object,
            "clean": self.clean_object,
            "switchon": self.turn_object_on,
            "switchoff": self.turn_object_off,
            "slice": self.slice_object,
            "find": self.cheat_and_find_object,
            "give-up": self.give_up
        }

    def reset(self, scene_index=3, width=600, height=600, gridSize=0.25, visibilityDistance=10, single_room='kitchen'):
        scene = None
        if scene_index == -1:
            scene = get_ithor_scene_single_room(single_room)
        else:
            dataset = prior.load_dataset("procthor-10k")
            scene = dataset["train"][scene_index]
        self.scene = scene
        self.controller = Controller(scene=scene, agentMode="default",
                                     visibilityDistance=visibilityDistance, width=width,
                                     height=height, allowAutoSimulation=True, gridSize=gridSize)
        if type(scene) is str:
            self.scene = {"rooms": [{"roomType": single_room, "floorPolygon": get_inf_floor_polygon()}]}

    def __del__(self):
        self.controller.stop()

    def get_object_location(self, object_type):
        objects = self.controller.last_event.metadata['objects']
        for obj in objects:
            if obj['objectType'] == object_type:
                return obj['position']
        return None


    def get_state(self, goal_objs=None):
        event = self.controller.last_event.metadata
        state = {}
        state["objects"] = get_visible_objects(event["objects"])
        for object in state["objects"]:
            if 'surface' in object['name']:
                object['onTop'] = object['parentReceptacles']
        state["predicates"] = get_predicates(state["objects"])
        state["room_names"] = [room['roomType'] for room in self.scene['rooms']]
        state["robot_state"] = event['agent']
        state["memory_dict"] = {}
        return state

    def get_robot_state(self, state, robot = "character", relations=None):
        state = self.get_state()
        agent_pose = state["robot_state"]["position"]
        robot_room = None
        for room in state["room_names"]:
            polygon = [room_obj for room_obj in self.scene["rooms"] if room_obj["roomType"]==room][0]["floorPolygon"]
            if is_in_room(agent_pose, polygon):
                robot_room = room

        holding = [obj['objectId'] for obj in state["objects"] if obj["isPickedUp"]]
        nl_state = f"I am in the {robot_room}."
        if len(holding) == 0:
            nl_state+= " I am not holding anything."
        else:
            holding_str = ", ".join(holding)
            nl_state+=f" I am holding the {holding_str}."
        return nl_state, robot_room

    def cheat_and_find_object(self, object):
        print(object)
        obj = [obj for obj in self.get_graph()['objects'] if object.lower() in obj['objectId'].lower()][0]
        self.navigate_to_object(obj)
        self.handle_scan_room(obj['objectId'], memory=None)
        return self.controller.last_event

    def done(self):
        return self.controller.step(action="Done")

    def turn_left(self, degrees=30):
        return self.controller.step("RotateLeft", degrees=degrees)

    def turn_right(self, degrees=30):
        return self.controller.step("RotateRight", degrees=degrees)

    def look_up(self, degrees=10):
        return self.controller.step("LookUp", degrees=degrees)

    def look_down(self, degrees=10):
        return self.controller.step("LookDown", degrees=degrees)

    def move_forward(self, meters=0.25):
        return self.controller.step("MoveAhead", moveMagnitude=meters)

    def move_back(self, meters=0.25):
        return self.controller.step("MoveBack", moveMagnitude=meters)

    def give_up(self):
        print("womp womp")
        return self.navigate_to_room(target_room_str=self.single_room)

    def navigate_to_room(self, target_room_str="bedroom"):
        target_room = None
        for room in self.scene["rooms"]:
            if room["roomType"].lower() == target_room_str.lower():
                target_room = room
        assert target_room is not None
        positions = [pose for pose in self.valid_positions if is_in_room(pose, target_room["floorPolygon"])]
        teleport_pose = np.random.choice(positions)
        return self.controller.step(
            action="Teleport",
            position=teleport_pose,
            rotation={'x': 0.0, "y": np.random.uniform(0, 360), "z": 0.0}
        )

    def grab_object(self, object):
        assert object["distance"] <= CLOSE_DISTANCE
        ret =  self.controller.step("PickupObject",
                             objectId=object["objectId"],
                             forceAction=False,
                             manualInteract=True)
        for i in range(100):
            self.controller.step("MoveHeldObjectBack", moveMagnitude=0.01, forceVisible=True)
        return ret

    def place_object(self, target):
        return self.controller.step(
            action="PutObject",
            objectId=target["objectId"],
            forceAction=False,
            placeStationary=False
        )

    def get_interactable_poses(self, object):
        positions = self.controller.step(
                action="GetInteractablePoses",
                objectId=object['objectId']
            ).metadata['actionReturn']
        return positions

    def navigate_to_object(self, object):
        positions = self.get_valid_positions()
        teleport_pose = find_closest_position(object["position"], object["rotation"], positions, 1.25, facing=False)
        # teleport_pose = np.random.choice(positions)
        assert teleport_pose is not None
        return self.controller.step(
            action="Teleport",
            position=teleport_pose,
            rotation={'x': 0.0, 'y': get_yaw_angle(teleport_pose,{'y':0.0}, object['position']), 'z': 0.0},
            forceAction=False
        )

    def open_object(self, object):
        event = self.controller.step(
            action="OpenObject",
            objectId=object['objectId'],
            openness=1,
            forceAction=False
        )

        # Image.fromarray(event.frame).show("str")
        return event

    def close_object(self, object):
        return self.controller.step(
            action="CloseObject",
            objectId=object['objectId'],
            forceAction=False
        )

    def cook_object(self, object):
        return self.controller.step(
            action="CookObject",
            objectId=object['objectid'],
            forceAction=False
        )

    def slice_object(self, object):
        return self.controller.step(
            action="SliceObject",
            objectId=object["objectId"],
            forceAction=False
        )

    def turn_object_on(self, object):
        return self.controller.step(
            action="ToggleObjectOn",
            objectId=object["objectId"],
            forceAction=False
        )

    def turn_object_off(self, object):
        return self.controller.step(
            action="ToggleObjectOff",
            objectId=object["objectId"],
            forceAction=False
        )

    def get_valid_positions(self):
        return self.controller.step(
                    action="GetReachablePositions").metadata["actionReturn"]

    def make_object_dirty(self, object):
        return  self.controller.step(
            action="DirtyObject",
            objectId=object["objectId"],
            forceAction=False
        )

    def clean_object(self, object):
        return self.controller.step(
            action="CleanObject",
            objectId=object["objectId"],
            forceAction=False
        )

    def fill_with_liquid(self, object, liquid="water"):
        return self.controller.step(
            action="FillObjectWithLiquid",
            objectId=object["objectId"],
            fillLiquid=liquid,
            forceAction=False
        )

    def empty_liquid(self, object):
        return self.controller.step(
            action="EmptyLiquidFromObject",
            objectId=object["objectId"],
            forceAction=False
        )

    def handle_fry_in_pan(self, object):
        pass

    def drop_object(self):
        return self.controller.step(action="DropHandObject",
                             forceAction=False)

    def handle_scan_room(self, goal_obj, memory):
        print(f"scanning for object {goal_obj}")
        for i in range(12):
            self.turn_left(degrees=30)
            self.done()
            state = self.get_state()
            if any([goal_obj == object["objectId"] for object in state['objects']]):
                return True
        return False

    def translate_action_for_sim(self, action, state):
        return [action]

    def add_object_waypoint(self, x, y):
        pass

    def get_graph(self):
        return self.controller.last_event.metadata

    def environment_graph(self):
        graph = self.get_graph()
        graph['nodes'] = graph['objects']
        for node in graph['nodes']:
            node['class_name'] = node['objectType']
            node['id'] = '|'.join(node['objectId'].split('|')[1:])
        return True, graph

    def check_cooked(self):
        pass

    def execute_actions(self, actions, state):
        event = None
        for action in actions:
            state = self.get_state()
            act, params = parse_instantiated_predicate(action)
            objects = []
            print(f"Action: {action}")
            if "find" in action:
                event = self.cheat_and_find_object(params[0])
                print(event.metadata["lastActionSuccess"], event.metadata['errorMessage'])
                continue
            new_action = f"{action}"
            if act == 'walk':
                new_action = f"walk_to_object"
                if any(param in state['room_names'] for param in params):
                    new_action = f"walk_to_room"
                act = new_action
            for param in params:
                if "character" in param:
                    continue
                object = [obj for obj in state["objects"] if obj["objectId"] == param]
                object = None if len(object) == 0 else object[0]
                if object is None and param not in state["room_names"]:
                    return False, f"Failed to find object {param} to act on."
                elif param in state["room_names"]:
                    object = param
                objects.append(object)
            event = None

            if len(objects) == 0:
                event = self.action_fn_from_str[act]()
            else:
                target = objects[0] if len(objects) == 1 else objects[1]
                event = self.action_fn_from_str[act](target)
                print(event.metadata["lastActionSuccess"], event.metadata['errorMessage'])
            self.move_back(meters=0.01)
        return event.metadata["lastActionSuccess"], event.metadata['errorMessage']

    def get_world_predicate_set(self, graph, custom_preds=()):
        return set(get_predicates(graph['objects']))

    def check_obj_contained(self, obj, receptacle):
        state = self.get_graph()
        receptacle = [object for object in state["objects"] if object["objectId"] == receptacle][0]
        return obj in receptacle['receptacleObjectIds']

    def check_satisfied(self, predicates, sub_goal):
        state = self.get_graph()
        to_remove = []
        success = False
        pred, params = parse_instantiated_predicate(sub_goal)
        if "INSIDE" in sub_goal or "IN" in sub_goal or ("ON" in sub_goal and len(params) == 2):
            success = self.check_obj_contained(params[0], params[1])
        elif "WASHED" in pred:
            param = params[0] if "character" not in params[0] else params[1]
            obj = [object for object in state["objects"] if object["objectId"] == param][0]
            success = not obj["isDirty"]
        else:
            vhome_to_aithor = get_vhome_to_thor_dict()

            key = vhome_to_aithor.get(pred, None)
            assert key is not None
            param = params[0] if "character" not in params[0] else params[1]
            obj = [object for object in state["objects"] if object["objectId"] ==param][0]
            success = obj[key]
        if success:
            to_remove.append(sub_goal)
        return success, to_remove