import numpy as np
import os

# Define the path where your NPZ file is saved and the run identifier
path = '/home/liam/dev/llm_task_planning/data/data_collection/'  # Replace 'your_path_here' with the actual path to your NPZ file
set = 'data_collection_20240223_121556'  # Replace 'your_run_identifier' with the actual run identifier used when saving the file

path = path + f"/{set}"
run = 5
# Construct the filename from the given path and run identifier
filename = os.path.join(path, f"run_{run}_data.npz")

# Load the NPZ file
data = np.load(filename)

# Access the contents
actions = data['actions']  # Actions taken
prompts = data['prompts']  # All prompts
responses = data['responses']  # All LLM responses
failures = data['failures']  # All failures

# Example of how to print or use the loaded data
print("Actions:", actions.shape)
# print("Prompts:", prompts)
# print("Responses:", responses)
# print("Failures:", failures)

# Remember to close the file after you are done
data.close()