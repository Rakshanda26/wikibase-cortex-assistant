import os

# Base project path
base_path = r"F:\wikibase-cortex-assistant"

# Folder and file structure
structure = {
    "api": ["main.py", "snowflake_client.py", "cortex_handler.py"],
    "data": ["prepare_data.py"],
    "tests": ["test_api.py"],
    ".github/workflows": ["deploy.yml"],
    "": ["requirements.txt", "Dockerfile", "README.md"]
}

# Create folders and files
for folder, files in structure.items():
    folder_path = os.path.join(base_path, folder)
    os.makedirs(folder_path, exist_ok=True)
    
    for file in files:
        file_path = os.path.join(folder_path, file)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("")  # Create an empty file

print(" Project structure created at:", base_path)
