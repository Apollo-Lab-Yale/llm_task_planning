import os
import pandas as pd
import numpy as np
import ast
import re
import statistics
from llm_task_planning.llm.openai_interface import add_messages_to_conversation
import random

pd. set_option("display.max_rows", None, "display.max_columns", None)
PLANNER_CLASS = "<class 'llm_task_planning.planner.pddl_planner.PDDLPlanner'>"
PLANNER_NAME = 'ATR'
PROG_PROMPT_CLASS = "<class 'llm_task_planning.planner.prog_prompt.progprompt_planner.ProgPromptPlanner'>"
PROG_PROMPT_NAME = "ProgPrompt"
CONTINGENT_FF_CLASS = "<class 'llm_task_planning.planner.contingent_ff.contingent_ff.ContingentFF'>"
CONTINGENT_FF_NAME = "Contingent-FF-OG"

def aggregate_csv_data(root_dir):
    """
    Iterates through all subdirectories of the given root directory,
    aggregates data from 'data_log.csv' files found in each subdirectory,
    and returns a single DataFrame containing all the aggregated data.

    Parameters:
    - root_dir: The root directory to search for 'data_log.csv' files.

    Returns:
    - A pandas DataFrame containing aggregated data from all 'data_log.csv' files.
    """
    aggregated_data = pd.DataFrame()  # Initialize an empty DataFrame to store aggregated data.
    raw_data = {}
    raw_columns = []
    for subdir, dirs, files in os.walk(root_dir):
        no_find = "nofind" in subdir
        no_info = "noinfo" in subdir
        for file in files:
            if file == 'data_log.csv':
                file_path = os.path.join(subdir, file)  # Construct the full file path.
                data = pd.read_csv(file_path)  # Read the CSV data into a DataFrame.
                if no_find:
                    data["Planner"] = data['Planner'].str.replace(PROG_PROMPT_CLASS, PROG_PROMPT_NAME+"_noFind")
                elif no_info:
                    data["Planner"] = data['Planner'].str.replace(CONTINGENT_FF_CLASS, CONTINGENT_FF_NAME+"_noInfo")
                data["Planner"] = data['Planner'].str.replace(PLANNER_CLASS, PLANNER_NAME)
                data["Planner"] = data['Planner'].str.replace(PROG_PROMPT_CLASS, PROG_PROMPT_NAME)
                data["Planner"] = data['Planner'].str.replace(CONTINGENT_FF_CLASS, CONTINGENT_FF_NAME)
                data["Goals"] = data['Goals'].str.replace("_ff", '').replace("_goal", '')
                aggregated_data = pd.concat([aggregated_data, data], ignore_index=True)  # Aggregate the data.


                planner = list(aggregated_data["Planner"])[-1]
                if planner not in raw_data:
                    raw_data[planner] = {}
                if subdir not in raw_data[planner]:
                    raw_data[planner][subdir] = {}
                raw_data[planner][subdir]['npz'] = get_npz_data(subdir)
                raw_data[planner][subdir]['meta'] = data
                # if planner == 'ATR':
    return aggregated_data, raw_data

def results(data):
    atr_data = data[data['Planner'] == PLANNER_NAME]
    print(f" ATR: {atr_data['Goals'].unique()}")
    prog_prompt_data = data[data['Planner'] == PROG_PROMPT_NAME]
    prog_prompt_nofind_data = data[data['Planner'] == PROG_PROMPT_NAME+"_noFind"]
    contingent_ff_noinfo_data = data[data['Planner'] == CONTINGENT_FF_NAME+"_noInfo"]

    contingent_ff_data = data[data['Planner'] == CONTINGENT_FF_NAME]

    planners = [atr_data, prog_prompt_data, contingent_ff_data, prog_prompt_nofind_data , contingent_ff_noinfo_data]
    problems = list(data['Goals'].unique())
    print(problems)
    results = pd.DataFrame(columns=["Planner"] + problems + [f"{prob}_num_runs" for prob in problems])
    for planner in planners:
        if len(planner["Planner"].unique()) == 0:
            continue
        row = {"Planner": planner["Planner"].unique()[0]}
        for prob in problems:
            target = planner[planner['Goals'] == prob]
            target = target.sample(min(50, len(target)))
            row[f"{prob}_num_runs"] = len(target['Status'])
            row[f"{prob}"] = f"{len(target[target['Status']])}/{len(target['Status'])}"
        results = results._append(row, ignore_index=True)
    return  results

def get_npz_data(subdir):
    runs = {}
    for subdir, dirs, filenames in os.walk(subdir):
        filenames = [os.path.join(subdir, filename) for filename in filenames]
        filenames.sort(key=os.path.getctime)
        for filename in filenames:
            # Construct the filename from the given path and run identifier
            if filename.split('.')[-1] != 'npz':
                continue
            # Load the NPZ file

            data = np.load(filename)
            data_dict = {}
            for key in data:
                data_dict[key] = data[key]
            # Access the contents
            runs[os.path.basename(filename)] = data_dict
    return runs
import numpy as np

def print_all_prompts_from_npz(file_path):
    """
    Load an NPZ file and print all values of the 'all_prompts' variable.

    Parameters:
    - file_path: str, the path to the NPZ file.
    """
    try:
        # Load the NPZ file
        with np.load(file_path) as data:
            # Check if 'all_prompts' is in the NPZ file
            if 'responses' in data or "prompts" in data:
                all_prompts = data['prompts'] if 'prompts' in data else data['responses']
                is_responses = 'responses' in data
                # Iterate over each item in 'all_prompts' and print it
                max_act = 0
                all_act = 0
                # print()
                for prompt in all_prompts:
                    # print(prompt)
                    try:
                        parsed_list = ast.literal_eval(prompt)
                    except Exception as e:
                        # print(e)
                        continue
                    for message in parsed_list:
                        actions = extract_actions_from_message(message)
                        if len(actions) > 0:
                            all_act += len(actions)
                            if len(actions) > max_act:
                                max_act = len(actions)
                # print(max_act)
                # print(all_act)
                return all_act
                        # print(prompt)
                    # print(prompt)
            else:
                print("'all_prompts' variable not found in the NPZ file.")
                return -1
    except IOError:
        print(f"Error: The file '{file_path}' could not be opened. Make sure the path is correct.")
    return -1

def extract_actions_from_ff_output(message):
    pass

def extract_actions_from_message(message):
    """
    Extracts a list of actions from a given message.

    Parameters:
    - message: str, the message containing the action list.

    Returns:
    - list of str, the extracted actions.
    """
    # Regular expression to find the list of actions
    pattern = r"\[\s*'([^']*)'\s*(?:,\s*'[^']*'\s*)*\]"
    match = re.search(pattern, message)

    if match:
        # Extract the matched text
        matched_text = match.group()
        # Convert the matched text to a Python list
        try:
            actions_list = eval(matched_text)
            if "$$" not in actions_list[0]:
                return []
            return actions_list
        except:
            return []
    else:
        return []

def get_avg_actions_per_ff(raw_data, dir = '/home/liam/Documents/phd/data/llm_task_planning/FF_ACTION_DATA/trial_2_fixed_index/action_consideration'):
    counts = {'apple': [], 'mug': [], 'coffee': [], 'toast':[]}
    num_actions = {'apple': [], 'mug': [], 'coffee': [], 'toast':[]}
    # assume raw data is just ff_data


    number_files = [os.path.join(dir, file) for file in os.listdir(dir)]
    # number_files.sort(key=os.path.getctime)

    # for root_directory, subdir, files in os.walk(dir):
    #     print(subdir)
    #     print(root_directory)
    #     print(len(files))
    #     files = [os.path.join(root_directory, file) for file in files]
    #     files.sort(key=os.path.getctime)
    keys = list(raw_data.keys())
    keys.sort()
    index = 0
    for filedir in keys:
        meta_data = raw_data[filedir]['meta']
        filenames = list(raw_data[filedir]['npz'].keys())
        filenames.sort()
        for filename in filenames:
            count = 0
            run_id = int(filename.split('_')[1])
            nactions = list(meta_data[meta_data["Run"] == run_id]["Num Actions"])[-1]
            with open(number_files[index]) as nums_file:
                index += 1
                for line in nums_file:
                    num = int(line.strip())
                    count += num
                count = count / (nactions if nactions > 0 else 101)

            for key in counts:
                if key in number_files[index-1].lower():
                    counts[key].append(count)
                    num_actions[key].append(nactions)
    # print(counts)
    for key in counts:
        print(key)
        if len(counts[key]) > 0:
            print(sum(counts[key])/len(counts[key]))
            print(f"std: {statistics.stdev(counts[key])}")


#
# root_directory = '/home/liam/Documents/phd/data/llm_task_planning/data_1_no_hidden_mug/'  # Replace this with the path to your root directory.
def track_index_counts(raw_data):
    counts = {}
    for dir in raw_data:
        meta = list(raw_data[dir]['meta']['Run'])
        for run in meta:
            if run not in counts:
                counts[run] = 0
            counts[run] += 1
    for run in counts:
        if counts[run] % 5 != 0:
            print(f"{run} - {counts[run]}")
    # print(counts)
    return counts

# root_directory = '/home/liam/Documents/phd/data/llm_task_planning/FF_ACTION_DATA/ff_run_data'
# root_directory = '/home/liam/Documents/phd/data/llm_task_planning/FF_ACTION_DATA/trial_2_fixed_index/run_data'
root_directory = '/home/liam/Documents/phd/data/llm_task_planning/data_2_100_actions'
# root_directory = '/home/liam/Documents/phd/data/llm_task_planning/ATR_action_check_data'
# print_all_prompts_from_npz(root_directory + f'/run_2_data.npz')
aggregated_data, raw_data = aggregate_csv_data(root_directory)
# run_id_counts = track_index_counts(raw_data[PLANNER_NAME])
# get_avg_actions_per_ff(raw_data[CONTINGENT_FF_NAME])

# for key in raw_data[PLANNER_NAME]:
#     for file in raw_data[PLANNER_NAME][key]['npz']:
#         # print(raw_data[PLANNER_NAME][key]['npz'].keys())
#         data = raw_data[PLANNER_NAME][key]['npz'][file]
#         real_actions = [action for action in data['actions'] if action != '']
#         # if len(real_actions) > 100:
#         print(len(real_actions))


def get_action_metrics(raw_data, planner=PLANNER_NAME):
    all_counts = {}
    seen_counts = {}

    subdirs = list(raw_data[planner].keys())
    subdirs.sort()
    for subdir in subdirs:
        data = raw_data[planner][subdir]['meta']
        files = list(raw_data[planner][subdir]['npz'].keys())
        files.sort()
        for file_name in files:
            if "npz" in file_name:
                run_index = int(file_name.split('_')[1])
                all_data = data[data['Run'] == run_index]
                problem = list(all_data['Goals'])[0]
                if problem not in all_counts:
                    all_counts[problem] = []
                np_data = raw_data[planner][subdir]['npz'][file_name]
                real_actions = [action for action in np_data['actions'] if action != '']
                tot_actions = 100 if len(real_actions) == 0 else len(real_actions)
                all_counts[problem].append( print_all_prompts_from_npz(os.path.join(subdir, file_name))/ tot_actions)
    total_count = 0
    num_runs = 0
    # print(all_counts)
    for problem in all_counts:
            if len(all_counts[problem]) ==0:
                continue
            print(f"{planner} -- {problem}")
            print(sum(all_counts[problem]) / len(all_counts[problem]))
            print(f"std- {statistics.stdev(all_counts[problem])}")

PLANNERS = [PLANNER_NAME, CONTINGENT_FF_NAME, PROG_PROMPT_NAME, PROG_PROMPT_NAME + "_noFind", CONTINGENT_FF_NAME+'_noInfo']

def get_avg_run_time(agg_data):
    for planner in PLANNERS:
        run_times = {'apple': [], 'mug': [], 'coffee': [], 'toast': []}
        meta = agg_data[agg_data['Planner'] == planner]
        print(planner)
        for key in meta['Goals'].unique():
            run_times = list(meta[meta["Goals"] == key]['Abstract Planning Time'])

            print(f"{planner} - {key} - {sum(run_times)/len(run_times)} +- {statistics.stdev(run_times)}")

def get_data_examples(raw_data):
    planner_data = raw_data[PROG_PROMPT_NAME]
    for dirname in planner_data:
        for file in planner_data[dirname]['npz']:
            data = planner_data[dirname]['npz'][file]
            actions = data['actions']
            prompt = eval( data['prompts'][0])
            response = data['responses'][0]
            output = f'''
            {actions}
            ---------------
            {add_messages_to_conversation(messages=prompt, speaker='user', conversation=[])}
            ------------------------------
            {response}
            '''
            print(output)
            exit(0)



get_data_examples(raw_data)

# get_avg_run_time(aggregated_data)
# get_action_metrics(raw_data)
# print(total_count/num_runs)
# print(results(aggregated_data))
#
# print(root_directory)
# print(res.to_string())

