import argparse
from datetime import datetime
import os
import csv
import numpy as np
from copy import deepcopy


from llm_task_planning.sim.vhome_sim import VirtualHomeSimEnv
from llm_task_planning.planner.pddl_planner import PDDLPlanner
from llm_task_planning.planner.prog_prompt.progprompt_planner import ProgPromptPlanner
# from llm_task_planning.problem.virtualhome.pddl_virtualhome import VirtualHomeProblem
from llm_task_planning.sim.ai2_thor.ai2thor_sim import AI2ThorSimEnv
# from goal_gen import get_make_toast_goal, get_put_salmon_in_fridge_goal, get_put_away_plates_goal, get_cook_salmon_in_microwave_goal, get_cook_salmon_in_microwave_put_on_table_goal
from goal_gen_aithor import get_put_apple_in_fridge_goal, get_wash_mug_in_sink_goal, get_make_toast, get_make_coffee
# goal_methods = [get_make_toast_goal, get_put_salmon_in_fridge_goal, get_put_away_plates_goal, get_cook_salmon_in_microwave_goal, get_cook_salmon_in_microwave_put_on_table_goal]
# goal_methods = [get_make_coffee, get_put_apple_in_fridge_goal, get_wash_mug_in_sink_goal]
# goal_methods = [get_wash_mug_in_sink_goal]
goal_methods = [get_put_apple_in_fridge_goal]


def record_data(success, planner : PDDLPlanner, path, run, goals):
    csv_file_path = os.path.join(path, "data_log.csv")
    file_exists = os.path.isfile(csv_file_path)
    with open(csv_file_path, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            # Write header if the file does not exist
            writer.writerow(["Status", "Planner", "Num Actions", "Abstract Planning Time", "Sim Time", "Run", "Goals", "Unsolved Goals", "Scene"])
        writer.writerow([success, type(planner), len(planner.actions_taken), planner.abstract_planning_time, planner.sim_planning_time, run, goals, "&".join(list(planner.goal)), planner.sim.scene['rooms'][0]['name']])
    print(len(planner.actions_taken), len(planner.all_prompts), len(planner.all_llm_responses), len(planner.all_failures))
    print(planner.actions_taken)
    print(planner.all_failures)
    print(planner.all_llm_responses)
    print(planner.all_prompts)
    print(len(planner.actions_taken), len(planner.all_prompts), len(planner.all_llm_responses), len(planner.all_failures))

    np.savez(os.path.join(path, f"run_{run}_data"), actions=planner.actions_taken, prompts=planner.all_prompts, responses=planner.all_llm_responses, failures=planner.all_failures)

def run_goals(num_runs, goal_fns, planner : PDDLPlanner, directory, current_datetime, args):
    run_index = 84
    test_set = [4, 6, 11, 24, 28]
    # test_set = [8, 20, 25]
    for fn in goal_fns:
        for i in range(num_runs):
            for scene in test_set:
                print("reseting")
                planner.sim.comm.reset(scene_index=scene)
                print("reset")
                goals, nl_goals = fn(planner.sim)
                planner.set_goal(deepcopy(goals), deepcopy(nl_goals))
                success, sim_error = planner.solve(args)
                if sim_error < 0:
                    i -= 1
                    continue
                record_data(success, planner, directory, run_index, fn.__name__)
                run_index += 1
                planner.reset_data()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--problem", type=str, choices=["all", ""], default="all")
    parser.add_argument("--planner", type=str, choices=["PDDLPlanner", "ProgPrompt", ""], default="PDDLPlanner")
    parser.add_argument("--num-runs", type=int, default=5)
    parser.add_argument("--data-path", type=str, default="/home/liam/dev/llm_task_planning/data/data_collection/")
    parser.add_argument("--show-graphics", type=bool, default=False)
    parser.add_argument("--progprompt-path", type=str,
                        default="/home/liam/dev/llm_task_planning/llm_task_planning/planner/prog_prompt")
    parser.add_argument("--expt-name", type=str, default=datetime.now().strftime("%Y%m%d_%H%M%S"))
    parser.add_argument("--use-find", type=bool, default=False)

    parser.add_argument("--gpt-version", type=str, default="gpt-3.5-turbo-1106",
                        choices=['text-davinci-002', 'davinci', 'code-davinci-002', "gpt-3.5-turbo-1106"])
    parser.add_argument("--env-id", type=int, default=0)
    parser.add_argument("--test-set", type=str, default="test_unseen",
                        choices=['test_unseen', 'test_seen', 'test_unseen_ambiguous', 'env1', 'env2'])

    parser.add_argument("--prompt-task-examples", type=str, default="default",
                        choices=['default', 'random'])
    # for random task examples, choose seed
    parser.add_argument("--seed", type=int, default=0)

    ## NOTE: davinci or older GPT3 versions have a lower token length limit
    ## check token length limit for models to set prompt size:
    ## https://platform.openai.com/docs/models
    parser.add_argument("--prompt-num-examples", type=int, default=3,
                        choices=range(1, 7))
    parser.add_argument("--prompt-task-examples-ablation", type=str, default="none",
                        choices=['none', 'no_comments', "no_feedback", "no_comments_feedback"])
    args = parser.parse_args()
    print("starting sim")
    sim = AI2ThorSimEnv(use_find=args.use_find)
    print("sim started")

    # problem = VirtualHomeProblem()
    problem = None
    planner = None
    if args.planner == "PDDLPlanner":
        planner = PDDLPlanner(sim)
    if args.planner == "ProgPrompt":
        planner = ProgPromptPlanner(sim)
    # Create a new directory with the current datetime
    current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
    directory_name = f"{args.data_path}/data_collection_{current_datetime}"
    if not args.use_find:
        directory_name += "_nofind"
    os.makedirs(directory_name, exist_ok=True)

    # Path for the CSV file
    csv_file_path = os.path.join(directory_name, "data_log.csv")

    goals = []
    if args.problem == "all":
        goals = goal_methods

    run_goals(args.num_runs, goals, planner, directory_name, current_datetime, args)


if __name__ == "__main__":
    main()