import requests
import os
import time
from tqdm import tqdm
#获取有package-lock.json和package.json的文件
# 写入laguage_nodejs_file
tokens = [
    'abc',
    'acb'
]

def get_headers():
    token = tokens.pop(0)
    tokens.append(token)
    return {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }

package_dir = 'language_nodejs_files'
if not os.path.exists(package_dir):
    os.makedirs(package_dir)

# Log file for repositories without required files
no_package_log = 'no_package_log.txt'
if not os.path.isfile(no_package_log):
    with open(no_package_log, 'w') as file:
        pass  # Create the file if it does not exist

# Load the log of repositories without required files
with open(no_package_log, 'r') as file:
    no_package = set(file.read().splitlines())

# Read the full repository names from the file
with open('language_nodejs_repositories.txt', 'r') as file:
    repo_names = file.readlines()

for repo_name in tqdm(repo_names, desc='Processing repositories'):
    repo_name = repo_name.strip()
    if repo_name in no_package:
        # Skip repositories known to lack required files
        continue

    package_json_path = os.path.join(package_dir, f"{repo_name.replace('/', '_')}_package.json")
    package_lock_json_path = os.path.join(package_dir, f"{repo_name.replace('/', '_')}_package-lock.json")

    if os.path.isfile(package_json_path) and os.path.isfile(package_lock_json_path):
        print(f"Files already exist: {package_json_path} and {package_lock_json_path}")  # 控制输出
        continue

    urls = {
        'package.json': f"https://api.github.com/repos/{repo_name}/contents/package.json",
        'package-lock.json': f"https://api.github.com/repos/{repo_name}/contents/package-lock.json"
    }

    files_to_download = {}
    headers = get_headers()
    all_files_exist = True

    for file_name, url in urls.items():
        success = False
        while not success:
            try:
                response = requests.get(url, headers=headers)
            except requests.exceptions.RequestException as e:
                print(f"Request failed: {e}")
                time.sleep(60)  # 等待一分钟后重试
                continue

            time.sleep(0.75)
            if response.status_code == 200:
                content = response.json()
                files_to_download[file_name] = content['download_url']
                success = True
            elif response.status_code == 404:
                all_files_exist = False
                with open(no_package_log, 'a') as log_file:
                    log_file.write(repo_name + '\n')
                success = True
            elif response.status_code == 403:
                print("Rate limit exceeded. Waiting to retry...")
                time.sleep(3600)  # 等待一小时
            else:
                print(f"Failed to fetch data for repository {repo_name}: {response.status_code}")
                time.sleep(120)  # 等待两分钟后重试

        if not all_files_exist:
            break

    if all_files_exist:
        for file_name, download_url in files_to_download.items():
            try:
                file_content = requests.get(download_url).text
            except requests.exceptions.RequestException as e:
                print(f"Failed to download the file content: {e}")
                break  # 出现错误时跳出循环

            file_path = os.path.join(package_dir, f"{repo_name.replace('/', '_')}_{file_name}")
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(file_content)

total_existing_files_after_download = len([name for name in os.listdir(package_dir) if os.path.isfile(os.path.join(package_dir, name))])
print(f"Total number of existing files: {total_existing_files_after_download}")
