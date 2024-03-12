import os
import pandas as pd
import numpy as np
import ast
import re

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
                    raw_data[planner] = []
                raw_data[planner].append(get_npz_data(subdir))
                # if planner == 'ATR':
    return aggregated_data, raw_data

def results(data):
    atr_data = data[data['Planner'] == PLANNER_NAME]
    prog_prompt_data = data[data['Planner'] == PROG_PROMPT_NAME]
    prog_prompt_nofind_data = data[data['Planner'] == PROG_PROMPT_NAME+"_noFind"]
    contingent_ff_noinfo_data = data[data['Planner'] == CONTINGENT_FF_NAME+"_noInfo"]

    contingent_ff_data = data[data['Planner'] == CONTINGENT_FF_NAME]

    planners = [atr_data, prog_prompt_data, contingent_ff_data, prog_prompt_nofind_data , contingent_ff_noinfo_data]
    problems = list(data['Goals'].unique())
    results = pd.DataFrame(columns=["Planner"] + problems + [f"{prob}_num_runs" for prob in problems])
    for planner in planners:
        if len(planner["Planner"].unique()) == 0:
            continue
        row = {"Planner": planner["Planner"].unique()[0]}
        for prob in problems:
            target = planner[planner['Goals'] == prob]
            row[f"{prob}_num_runs"] = len(target['Status'])
            row[f"{prob}"] = len(target[target['Status']]) / len(target['Status']) if len(target['Status']) > 0 else 0.0
        results = results._append(row, ignore_index=True)
    return  results

def get_npz_data(subdir):
    path = '/home/liam/Documents/phd/data/llm_task_planning/data_1_no_hidden_mug/'  # Replace 'your_path_here' with the actual path to your NPZ file

    runs = {}
    for subdir, dirs, filenames in os.walk(subdir):
        for filename in filenames:
            # Construct the filename from the given path and run identifier
            if filename.split('.')[-1] != 'npz':
                continue
            # Load the NPZ file

            data = np.load(os.path.join(subdir, filename))
            data_dict = {}
            for key in data:
                data_dict[key] = data[key]
            # Access the contents
            runs[filename] = data_dict
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
                print()
                for prompt in all_prompts:
                    print(prompt)
                    try:
                        parsed_list = ast.literal_eval(prompt)
                    except Exception as e:
                        print(e)
                        continue
                    for message in parsed_list:
                        actions = extract_actions_from_message(message)
                        if len(actions) > 0:
                            all_act += len(actions)
                            if len(actions) > max_act:
                                max_act = len(actions)
                print(max_act)
                print(all_act)
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

def get_avg_actions_per_ff(dir = '/home/liam/dev/llm_task_planning/data/num_actions_ff'):
    counts = {'apple': [], 'mug': [], 'coffee': [], 'toast':[]}
    for _,_,files in os.walk(dir):
        for file in files:
            path = os.path.join(dir, file)
            count = 0
            with open(path) as nums_file:
                for line in nums_file:
                    num = int(line.strip())
                    count += num
            for key in counts:
                if key in file.lower():
                    counts[key].append(count)
    for key in counts:
        print(key)
        print(sum(counts[key])/len(counts[key]))

get_avg_actions_per_ff()
exit(0)

# root_directory = '/home/liam/Documents/phd/data/llm_task_planning/data_1_no_hidden_mug/'  # Replace this with the path to your root directory.
root_directory = '/home/liam/dev/llm_task_planning/data/data_collection/data_collection_20240310_084110'
print_all_prompts_from_npz(root_directory + f'/run_2_data.npz')
# aggregated_data, raw_data = aggregate_csv_data(root_directory)
all_counts = []
for subdir,_,files in os.walk(root_directory):
    for file_name in files:
        if "npz" in file_name:
            all_counts.append( print_all_prompts_from_npz(os.path.join(root_directory, file_name)))
total_count = 0
num_runs = 0
for count in all_counts:
    if count > 0:
        total_count += count
        num_runs += 1

print(total_count/num_runs)
# print(results(aggregated_data))

print(root_directory)
# print(res.to_string())

