import os


def rename_files_in_subdirs(parent_directory):
    # Walk through all subdirectories in the specified parent directory
    for subdir, dirs, files in os.walk(parent_directory):
        start_index = 0  # Reset index for each subdir
        files_sorted = sorted([f for f in files if f.startswith("image_") and f.endswith(".png")],
                              key=lambda x: int(x.replace("image_", "").replace(".png", "")))

        for file_name in files_sorted:
            original_path = os.path.join(subdir, file_name)
            new_file_name = f"image{start_index:05d}.png"
            new_path = os.path.join(subdir, new_file_name)

            # Check if the new file name already exists to prevent overwriting
            if not os.path.exists(new_path):
                os.rename(original_path, new_path)
                print(f"Renamed: {original_path} -> {new_path}")
            else:
                print(f"File already exists, skipping: {new_path}")

            start_index += 1


# Specify the parent directory
parent_directory = "/home/liam/dev/llm_task_planning/data/videos/"

# Call the function to start the renaming process
rename_files_in_subdirs(parent_directory)