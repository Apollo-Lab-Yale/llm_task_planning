import argparse
from datetime import datetime
import os
import csv
import numpy as np
from copy import deepcopy


from llm_task_planning.sim.vhome_sim import VirtualHomeSimEnv
from llm_task_planning.planner.contingent_ff.contingent_ff import ContingentFF

from goal_gen import get_make_toast_goal, get_put_salmon_in_fridge_goal, get_put_away_plates_goal, get_cook_salmon_in_microwave_goal, get_cook_salmon_in_microwave_put_on_table_goal

goal_methods = [get_make_toast_goal, get_put_salmon_in_fridge_goal]
goal_problems = ["toast_cooked_toaster.pddl", "salmon_to_fridge.pddl"]

def record_data(success, planner : ContingentFF, path, run, goals):
    csv_file_path = os.path.join(path, "data_log.csv")
    file_exists = os.path.isfile(csv_file_path)
    with open(csv_file_path, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            # Write header if the file does not exist
            writer.writerow(["Status", "Planner", "Num Actions", "Abstract Planning Time", "Sim Time", "Run", "Goals", "Unsolved Goals"])
        writer.writerow([success, type(planner), len(planner.actions_taken), planner.abstract_planning_time, planner.sim_planning_time, run, goals, "&".join(list(planner.goal))])
    print(len(planner.actions_taken), len(planner.all_sub_plans), len(planner.all_failures))
    print(planner.actions_taken)
    print(planner.all_failures)
    print(planner.all_sub_plans)
    print(len(planner.actions_taken), len(planner.all_sub_plans), len(planner.all_failures))

    np.savez(os.path.join(path, f"run_{run}_data"), actions=planner.actions_taken, sub_plans=planner.all_sub_plans, failures=planner.all_failures)

def run_goals(num_runs, goal_fns, planner : ContingentFF, directory, current_datetime, args):
    num_problems = 0
    for i in range(len(goal_fns)):
        fn = goal_fns[i]
        problem = goal_problems[i]
        num_problems += 1
        for i in range(num_runs):
            print("reseting")
            planner.sim.comm.reset(0)
            print("reset")
            goals, nl_goals = fn(planner.sim)
            planner.sim.add_character()
            planner.set_goal(problem, get_tmp_options(problem, planner.sim), goals, deepcopy(nl_goals))
            success, sim_error = planner.solve()
            if sim_error < 0:
                i -= 1
                continue
            record_data(success, planner, directory, i * num_problems, fn.__name__)
            planner.reset_data()

def get_tmp_options(problem, sim):
    graph = sim.get_graph()
    rooms = []
    containers = []
    for node in graph["nodes"]:
        if "Room" in node["category"]:
            rooms.append(f"{node['class_name']}_{node['id']}")
        if "CONTAINERS" in node["properties"]:
            containers.append(f"{node['class_name']}_{node['id']}")
    return rooms

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--problem", type=str, choices=["all", ""], default="all")
    parser.add_argument("--num-runs", type=int, default=10)
    parser.add_argument("--data-path", type=str, default="/home/liam/dev/llm_task_planning/data/data_collection/")
    parser.add_argument("--show-graphics", type=bool, default=False)
    parser.add_argument("--expt-name", type=str, default=datetime.now().strftime("%Y%m%d_%H%M%S"))
    parser.add_argument("--env-id", type=int, default=0)
    args = parser.parse_args()
    print("starting sim")
    sim = VirtualHomeSimEnv(0, no_graphics=not args.show_graphics, port="8080")
    print("sim started")

    # problem = VirtualHomeProblem()
    problem = None
    planner = None
    planner = ContingentFF(sim)
    # Create a new directory with the current datetime
    current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
    directory_name = f"{args.data_path}/data_collection_{current_datetime}"
    os.makedirs(directory_name, exist_ok=True)

    # Path for the CSV file
    csv_file_path = os.path.join(directory_name, "data_log.csv")

    goals = []
    if args.problem == "all":
        goals = goal_methods

    run_goals(args.num_runs, goals, planner, directory_name, current_datetime, args)


if __name__ == "__main__":
    main()