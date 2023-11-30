import argparse
from datetime import datetime
import os
import csv
import numpy as np
from copy import deepcopy

from llm_task_planning.sim.vhome_sim import VirtualHomeSimEnv
from llm_task_planning.planner.pddl_planner import PDDLPlanner
# from llm_task_planning.problem.virtualhome.pddl_virtualhome import VirtualHomeProblem

from goal_gen import get_make_toast_goal, get_put_salmon_in_fridge_goal, get_put_away_plates_goal, get_cook_salmon_in_microwave_goal, get_cook_salmon_in_microwave_put_on_table_goal

goal_methods = [get_make_toast_goal, get_put_salmon_in_fridge_goal, get_put_away_plates_goal, get_cook_salmon_in_microwave_goal, get_cook_salmon_in_microwave_put_on_table_goal]



def record_data(success, planner : PDDLPlanner, path, run, goals):
    csv_file_path = os.path.join(path, "data_log.csv")
    file_exists = os.path.isfile(csv_file_path)
    with open(csv_file_path, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            # Write header if the file does not exist
            writer.writerow(["Status", "Planner", "Num Actions", "Abstract Planning Time", "Sim Time", "Run", "Goals", "Unsolved Goals"])
        writer.writerow([success, type(planner), len(planner.actions_taken), planner.abstract_planning_time, planner.sim_planning_time, run, goals, "&".join(list(planner.goal))])
    print(len(planner.actions_taken), len(planner.all_prompts), len(planner.all_llm_responses), len(planner.all_failures))
    print(planner.actions_taken)
    print(planner.all_failures)
    print(planner.all_llm_responses)
    print(planner.all_prompts)
    np.savez(os.path.join(path, f"run_{run}_data"), actions=planner.actions_taken, prompts=planner.all_prompts, responses=planner.all_llm_responses, failures=planner.all_failures)

def run_goals(num_runs, goal_fns, planner : PDDLPlanner, directory, current_datetime):
    num_problems = 0
    for fn in goal_fns:
        num_problems += 1
        for i in range(num_runs):
            planner.sim.comm.reset(0)
            goals, nl_goals = fn(planner.sim)
            planner.sim.add_character()
            planner.set_goal(deepcopy(goals), deepcopy(nl_goals))
            success, sim_error = planner.solve()
            if sim_error < 0:
                i -= 1
                continue
            record_data(success, planner, directory, i * num_problems, fn.__name__)
            planner.reset_data()


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--problem", type=str, choices=["all", ""], default="all")
    parser.add_argument("--num-runs", type=int, default=2)
    parser.add_argument("--data-path", type=str, default="/home/liam/dev/llm_task_planning/data/data_collection/")
    parser.add_argument("--show-graphics", type=bool, default=False)
    args = parser.parse_args()

    sim = VirtualHomeSimEnv(0, no_graphics=not args.show_graphics)
    # problem = VirtualHomeProblem()
    problem = None
    planner = PDDLPlanner(problem, sim)
    # Create a new directory with the current datetime
    current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
    directory_name = f"{args.data_path}/data_collection_{current_datetime}"
    os.makedirs(directory_name, exist_ok=True)

    # Path for the CSV file
    csv_file_path = os.path.join(directory_name, "data_log.csv")

    goals = []
    if args.problem == "all":
        goals = goal_methods

    run_goals(args.num_runs, goals, planner, directory_name, current_datetime)


if __name__ == "__main__":
    main()