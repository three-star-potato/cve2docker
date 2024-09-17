
import requests
import time
from tqdm import tqdm
import os

#获取10k星标以上的仓库


headers = {
    'Authorization': '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',
    'Accept': 'application/vnd.github.v3+json'
}
# Function to fetch repositories within a specific star range
def fetch_repos(stars_min, stars_max, file):
    # base_url = f'https://api.github.com/search/repositories?q=stars:{stars_min}..{stars_max}+language:Python&sort=stars&order=desc&per_page=100'
    base_url = f'https://api.github.com/search/repositories?q=stars:{stars_min}..{stars_max}+language:nodejs&sort=stars&order=desc&per_page=100'
    for page in tqdm(range(1, 11)):  # GitHub API only allows access to the first 1000 results
        try:
            response = requests.get(base_url + f"&page={page}", headers=headers)
            if response.status_code == 200:
                data = response.json()['items']
                if not data:  # If there's no data, we've reached the end of the list
                    break
                for item in data:
                    repo_name = item['full_name']
                    stars = item['stargazers_count']
                    print(f"{repo_name} - Stars: {stars}\n")
                    file.write(f"{repo_name} \n")
            else:
                print(f"Failed to fetch data: {response.status_code}")
                break
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            break
        time.sleep(10)  # Respect the rate limit

# Ensure the file is opened in append mode
with open('language_node_repositories.txt', 'a') as file:
    fetch_repos(100000, 500000, file)
    fetch_repos(90000, 100000, file)
    fetch_repos(80000, 90000, file)
    fetch_repos(70000, 80000, file)
    fetch_repos(60000, 70000, file)
    fetch_repos(50000, 60000, file)
    fetch_repos(40000, 50000, file)
    fetch_repos(30000, 40000, file)
    fetch_repos(25000, 30000, file)
    fetch_repos(20000, 25000, file)
    fetch_repos(15000, 20000, file)
    fetch_repos(14000, 15000, file)
    fetch_repos(13000, 14000, file)
    fetch_repos(12000, 13000, file)
    fetch_repos(11000, 12000, file)
    fetch_repos(10000, 11000, file)



# ... rest of the script
