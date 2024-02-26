import os
import pandas as pd
pd. set_option("display.max_rows", None, "display.max_columns", None)
PLANNER_CLASS = "<class 'llm_task_planning.planner.pddl_planner.PDDLPlanner'>"
PLANNER_NAME = 'ATR'
PROG_PROMPT_CLASS = "<class 'llm_task_planning.planner.prog_prompt.progprompt_planner.ProgPromptPlanner'>"
PROG_PROMPT_NAME = "ProgPrompt"
CONTINGENT_FF_CLASS = "<class 'llm_task_planning.planner.contingent_ff.contingent_ff.ContingentFF'>"
CONTINGENT_FF_NAME = "Contingent-FF"

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

                aggregated_data = pd.concat([aggregated_data, data], ignore_index=True)  # Aggregate the data.
    aggregated_data["Planner"] = aggregated_data['Planner'].str.replace(PLANNER_CLASS, PLANNER_NAME)
    aggregated_data["Planner"] = aggregated_data['Planner'].str.replace(PROG_PROMPT_CLASS, PROG_PROMPT_NAME)
    aggregated_data["Planner"] = aggregated_data['Planner'].str.replace(CONTINGENT_FF_CLASS, CONTINGENT_FF_NAME)
    return aggregated_data

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
        row = {"Planner": planner["Planner"].unique()[0]}
        for prob in problems:
            target = planner[planner['Goals'] == prob]
            row[f"{prob}_num_runs"] = len(target['Status'])
            row[f"{prob}"] = len(target[target['Status']]) / len(target['Status']) if len(target['Status']) > 0 else 0.0
        print(row)
        results = results._append(row, ignore_index=True)
    return  results

# Example usage:
root_directory = '/home/liam/dev/llm_task_planning/data/data_collection'  # Replace this with the path to your root directory.
aggregated_data = aggregate_csv_data(root_directory)
print(aggregated_data["Planner"].unique())
# print(aggregated_data['Goals'].unique())
res = results(aggregated_data)

print(res.to_string())