from ai2thor.controller import Controller
import numpy as np
import time
import prior
from PIL import Image

from llm_task_planning.sim.ai2_thor.utils import get_visible_objects, get_predicates, CLOSE_DISTANCE, find_closest_position, is_in_room

class AI2ThorSimEnv:
    def __init__(self, scene_index=3, width=600, height=600, gridSize=0.25, visibilityDistance=10):
        dataset = prior.load_dataset("procthor-10k")
        scene = dataset["train"][scene_index]
        self.scene = scene
        self.controller = Controller(scene=scene, agentMode="default",
                                     visibilityDistance=visibilityDistance, width=width,
                                     height=height, allowAutoSimulation=True, gridSize=gridSize)
        self.scene = scene
        # self.controller.reset(scene)
        self.valid_positions = self.get_valid_positions()
    def __del__(self):
        self.controller.stop()

    def get_object_location(self, object_type):
        objects = self.controller.last_event.metadata['objects']
        for obj in objects:
            if obj['objectType'] == object_type:
                return obj['position']
        return None

    def get_state(self):
        # AI2-THOR provides a different way of getting state information.
        # This is an example to get the metadata of the last event.
        event = self.controller.last_event.metadata
        state = {}
        state["objects"] = get_visible_objects(event["objects"])
        for object in state["objects"]:
            if 'surface' in object['name']:
                object['onTop'] = object['parentReceptacles']
        state["predicates"] = get_predicates(state["objects"])
        return state

    def turn_left(self, degrees=90):
        self.controller.step("RotateLeft", degrees=degrees)

    def turn_right(self, degrees=90):
        self.controller.step("RotateRight", degrees=degrees)

    def look_up(self, degrees=10):
        self.controller.step("LookUp", degrees=degrees)

    def look_down(self, degrees=10):
        self.controller.step("LookDown", degrees=degrees)

    def move_forward(self, meters=0.25):
        self.controller.step("MoveAhead", moveMagnitude=meters)

    def move_back(self, meters=0.25):
        self.controller.step("MoveBack", moveMagnitude=meters)

    def navigate_to_room(self, target_room_str="bedroom"):
        target_room = None
        for room in self.scene["rooms"]:
            if room["roomType"].lower() == target_room_str.lower():
                target_room = room
        assert target_room is not None
        positions = [pose for pose in self.valid_positions if is_in_room(pose, target_room["floorPolygon"])]
        teleport_pose = np.random.choice(positions)
        self.controller.step(
            action="Teleport",
            position=teleport_pose
        )



    def grab_object(self, object):
        assert object["distance"] <= CLOSE_DISTANCE
        self.controller.step("PickupObject",
                             object_id=object["objectId"],
                             forceAction=False,
                             manualInteract=True)
    def place_object(self, target):
        self.controller.step(
            action="PutObject",
            objectId=target["objectId"],
            forceAction=False,
            placeStationary=False
        )

    def navigate_to_object(self, object):
        positions = self.get_valid_positions()
        teleport_pose = find_closest_position(object["position"], positions)
        self.controller.step(
            action="Teleport",
            position=teleport_pose
        )

    def open_object(self, object):
        event = self.controller.step(
            action="OpenObject",
            objectId=object['objectId'],
            openness=1,
            forceAction=False
        )

    def close_object(self, object):
        self.controller.step(
            action="CloseObject",
            objectId=object['objectId'],
            forceAction=False
        )
    def cook_object(self, object):
        event = self.controller.step(
            action="CookObject",
            objectId=object['objectid'],
            forceAction=False
        )
    def slice_object(self, object):
        event = self.controller.step(
            action="SliceObject",
            objectId=object["objectId"],
            forceAction=False
        )

    def turn_object_on(self, object):
        event = self.controller.step(
            action="ToggleObjectOn",
            objectId=object["objectId"],
            forceAction=False
        )

    def turn_object_off(self, object):
        event = self.controller.step(
            action="ToggleObjectOff",
            objectId=object["objectId"],
            forceAction=False
        )

    def get_valid_positions(self):
        return self.controller.step(
                    action="GetReachablePositions").metadata["actionReturn"]

    def make_object_dirty(self, object):
        event = self.controller.step(
            action="DirtyObject",
            objectId=object["objectId"],
            forceAction=False
        )

    def clean_object(self, object):
        event = self.controller.step(
            action="CleanObject",
            objectId=object["objectId"],
            forceAction=False
        )

    def fill_with_liquid(self, object, liquid="water"):
        event = self.controller.step(
            action="FillObjectWithLiquid",
            objectId=object["objectId"],
            fillLiquid=liquid,
            forceAction=False
        )

    def empty_liquid(self, object):
        event = self.controller.step(
            action="EmptyLiquidFromObject",
            objectId=object["objectId"],
            forceAction=False
        )

    def drop_object(self):
        self.controller.step(action="DropHandObject",
                             forceAction=False)
    def handle_scan_room(self, goal_obj, memory):
        for i in range(12):
            self.turn_left(degrees=30)
            state = self.get_state()


