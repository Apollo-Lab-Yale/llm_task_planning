from llm_task_planning.sim.ai2_thor. ai2thor_sim import AI2ThorSimEnv
from llm_task_planning.sim.ai2_thor.utils import get_top_down_frame, is_in_room, get_room_polygon
import prior
import numpy as np


def calculate_new_position_global_frame(position, orientation, distance):
    # Unpack the orientation and position according to the specified convention
    pitch, yaw, roll = orientation
    x, y, z = position  # Adjusted to match the specified axis convention
    if yaw <= 180:
        new_pose = (x * np.cos(yaw) * distance, y, z * np.sin(yaw) * distance)
    else:
        new_pose = (x * np.sin(yaw) * distance, y, z * np.cos(yaw) * distance)


    return new_pose

sim = AI2ThorSimEnv(scene_index=6, single_room="kitchen", use_find=True)
graph = sim.get_graph()
fridge = [obj for obj in graph['objects'] if "fridge" in obj['objectId'].lower()][0]
print(fridge)
fridge_pose = [val for key, val in fridge['position'].items()]
fridge_orientation = [val for key, val in fridge['rotation'].items()]
garbage = [obj for obj in graph['objects'] if "garbagecan" in obj['objectId'].lower()][0]
point = calculate_new_position_global_frame(fridge_pose, fridge_orientation, 1)
print(sim.controller.step(
    action="PlaceObjectAtPoint",
    objectId=garbage['objectId'],
    position={
        "x": point[0],
        "y": point[1],
        "z": point[2]
    }
))
graph = sim.get_graph()
fridge = [obj for obj in graph['objects'] if "fridge" in obj['objectId'].lower()][0]

sim.cheat_and_find_object(fridge)
sim.look_down()
sim.look_down()
graph = sim.get_graph()
print(sim.controller.last_event)
garbage = [obj for obj in graph['objects'] if "garbagecan" in obj['objectId'].lower()][0]
print(garbage)
input()
while True:
    ans = input("keep going").strip()
    print(sim.scene)
    if ans == 'no':
        break
    if ans == 'l':
        sim.turn_left()
        sim.move_forward()
        sim.move_forward()
    else:
        sim.turn_left()
# fridge block wors: [3]
sim.turn_left()

input()