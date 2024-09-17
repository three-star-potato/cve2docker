import requests
import os
import time
from tqdm import tqdm
#获取
tokens = [
'abc',
'acb'

    
    # Add more tokens as needed
]

# Function to get headers with the next token
def get_headers():
    token = tokens.pop(0)  # Get the next token
    tokens.append(token)   # Move the token to the end of the list
    return {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }

headers = {
    'Authorization': 'abc',
    'Accept': 'application/vnd.github.v3+json'
}

# The directory to store requirements.txt files
requirements_dir = 'language_python_files'
if not os.path.exists(requirements_dir):
    os.makedirs(requirements_dir)

# Read the full repository names from the file
with open('language_python_repositories.txt', 'r') as file:
    repo_names = file.readlines()

# Check each repository for a requirements.txt file
for repo_name in tqdm(repo_names, desc='Processing repositories'):
    repo_name = repo_name.strip()  # Remove any leading/trailing whitespace
    file_path = os.path.join(requirements_dir, f"{repo_name.replace('/', '_')}_requirements.txt")

    # Check if we already have the file
    if os.path.isfile(file_path):
        print(f"File already exists: {file_path}")
        continue

    url = f"https://api.github.com/repos/{repo_name}/contents/requirements.txt"
    success = False
    headers = get_headers()  # Get the initial headers with a token
    
    while not success:
        response = requests.get(url, headers=headers)
        time.sleep(0.75)
        if response.status_code == 200:
            # Repository has a requirements.txt file
            print(f"Downloading requirements.txt from {repo_name}")
            content = response.json()
            file_content = requests.get(content['download_url']).text

            # Write the contents of requirements.txt to a file in the specified directory
            with open(file_path, 'w') as file:
                file.write(file_content)
            
            # Set success flag to True to exit the loop
            success = True

        elif response.status_code == 404:
            print(f"Repository {repo_name} does not have a requirements.txt file.")
            # Set success flag to True to exit the loop
            success = True
        else:
            print(f"Failed to fetch data for repository {repo_name}: {response.status_code}")
            # Switch to the next token
            headers = get_headers()
            # Wait for 2 minutes before retrying
            time.sleep(120)

# Calculate the total number of existing files after downloading
total_existing_files_after_download = len([name for name in os.listdir(requirements_dir) if os.path.isfile(os.path.join(requirements_dir, name))])

# Print the total number of requirements.txt files downloaded
print(f"Total number of existing files: {total_existing_files_after_download}")
