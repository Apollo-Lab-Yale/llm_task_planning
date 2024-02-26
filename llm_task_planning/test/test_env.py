from llm_task_planning.sim.ai2_thor.ai2thor_sim import AI2ThorSimEnv
# easy: [1, 2, 7, 10, 13, 14, 15, 16, 18, 19, 21~]
#hard: [3?, 4, 6s, 9~, 11?, 12?, 23~, 24~, 26~, 28, x29, 30~, ]
# hidden mug: [8, 20, 25, 27]
test_set = [28, 4, 6, 11, 24]
index = 11
sim = AI2ThorSimEnv(scene_index=index)
sim.look_down()
while True:
    key = input().strip()
    if key == 'l':
        sim.turn_left()
    if key == 'f':
        sim.move_forward()
    if key == 'r':
        sim.turn_right()
    if key == 's':
        sink = [obj for obj in sim.get_graph()['objects'] if "Sink" in obj["objectId"]]
        sim.navigate_to_object(object=sink[0])
    if key == "reset":
        index += 1
        sim.reset(index)
    else:
        sim.turn_left()
    print(index)
    print(f'{key}')