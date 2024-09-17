import json
import sys
from osv_node_one_size_analys import calculate_min_dependency_tree_size_beam_search

from tqdm import tqdm
import os
import random

def read_products(filename):
    with open(filename, 'r') as json_file:
        return json.load(json_file)


import json

def process_repository(repo_name, graph_size_require, beam_width):
    # 读取 lock 文件和 unlock 文件中的依赖数据
    with open(f'language_nodejs_files/{repo_name}_package-lock.json', 'r') as file:
        lockdata = json.load(file)
        lock_depend = lockdata.get('dependencies', {})

    with open(f'language_nodejs_files/{repo_name}_package.json', 'r') as file:
        unlockdata = json.load(file)
        unlock_depend = unlockdata.get('dependencies', {})

    lock_versions = [item + '_' + lock_depend[item]["version"] for item in lock_depend]
    lock_product = list(lock_depend.keys())

    total_size_gaps = 0
    total_lock_tree_size=0
    processed_dependencies = set()
    for item in unlock_depend:
        try:
            path = calculate_min_dependency_tree_size_beam_search(graph_size_require, item, version_constraints=unlock_depend[item], beam_width=beam_width)
        except:
            path = [0, []]
        
        item_size_gaps = 0
        item_lock_tree_size=0

        if path[1]:
            dependencies_list = path[1]
            while any(isinstance(dep, list) for dep in dependencies_list):
                new_dependencies_list = []
                for dep in dependencies_list:
                    if isinstance(dep, list):
                        new_dependencies_list.extend(dep)
                    else:
                        new_dependencies_list.append(dep)
                dependencies_list = new_dependencies_list
            
            for dep in dependencies_list:
                if dep[0] in processed_dependencies:
                    continue
                if dep[0] in lock_product and dep[1] in lock_versions:
                    continue
                if dep[0] in lock_product and dep[1] not in lock_versions:
                    try:
                        size_gap = graph_size_require[dep[0]][dep[0] + '_' + lock_depend[dep[0]]["version"]]['size'] - graph_size_require[dep[0]][dep[1]]['size']
                        lock_tree_size = graph_size_require[dep[0]][dep[0] + '_' + lock_depend[dep[0]]["version"]]['size']
                    except KeyError:
                        size_gap = 0
                        lock_tree_size=0
                    item_size_gaps += size_gap
                    item_lock_tree_size +=lock_tree_size
                if dep[0] not in lock_product:
                    size_gap = graph_size_require[dep[0]][dep[1]]['size']
                    item_size_gaps -= size_gap
                processed_dependencies.add(dep[0])
        # if item_size_gaps < 0:
        #     return 0,0
        total_lock_tree_size +=item_lock_tree_size
        total_size_gaps += item_size_gaps

    return total_size_gaps,total_lock_tree_size



# 用于存储每个仓库的 package-lock.json 和 package.json 是否满足条件
repo_status = {}

# 读取产品大小要求
graph_size_require = read_products('node_size_require.json')

# 遍历 language_nodejs_files 目录
directory_path = 'language_nodejs_files'
for root, dirs, files in os.walk(directory_path):
    for file_name in files:
        # 检查是否为 package-lock.json 文件
        if file_name.endswith('_package-lock.json'):
            repo_name = file_name.replace('_package-lock.json', '')
            package_lock_path = os.path.join(root, file_name)
            
            with open(package_lock_path, 'r') as file:
                lockdata = json.load(file)
                if 'dependencies' in lockdata:
                    if repo_name not in repo_status:
                        repo_status[repo_name] = {'package_lock': False, 'package': False}
                    repo_status[repo_name]['package_lock'] = True

        # 检查是否为 package.json 文件
        elif file_name.endswith('_package.json'):
            repo_name = file_name.replace('_package.json', '')
            package_path = os.path.join(root, file_name)

            with open(package_path, 'r') as file:
                unlockdata = json.load(file)
                if 'dependencies' in unlockdata:
                    if repo_name not in repo_status:
                        repo_status[repo_name] = {'package_lock': False, 'package': False}
                    repo_status[repo_name]['package'] = True

# 统计同时满足条件的仓库
satisfying_repos = [repo_name for repo_name, status in repo_status.items() if status['package_lock'] and status['package']]

# 随机选择100个满足条件的仓库
random.seed(1010)
selected_repos = random.sample(satisfying_repos, min(100, len(satisfying_repos)))
beam_widths = [1, 2, 3]
repo_size_gaps = {bw: {} for bw in beam_widths}
repo_lock_sizes = {bw: {} for bw in beam_widths}
total_size_gaps = {bw: 0 for bw in beam_widths}
total_lock_sizes = {bw: 0 for bw in beam_widths}

for repo_name in tqdm(selected_repos):
    for bw in beam_widths:
        size_gaps, lock_sizes = process_repository(repo_name, graph_size_require, beam_width=bw)
        repo_size_gaps[bw][repo_name] = size_gaps
        repo_lock_sizes[bw][repo_name] = lock_sizes
        print(f"Repo: {repo_name}, Beam Width: {bw}, Size Gaps: {size_gaps}, Lock Sizes: {lock_sizes}")
        total_size_gaps[bw] += size_gaps
        total_lock_sizes[bw] += lock_sizes

# 将结果存储到一个文本文件中
with open('node_repo_size_gaps.txt', 'w') as file:
    for bw in beam_widths:
        file.write(f"Beam Width: {bw}\n")
        for repo_name in repo_size_gaps[bw]:
            size_gaps = repo_size_gaps[bw][repo_name]
            lock_sizes = repo_lock_sizes[bw][repo_name]
            file.write(f"{repo_name}: Size Gaps: {size_gaps}, Lock Sizes: {lock_sizes}\n")
        file.write(f"总的 Size Gaps (beam width {bw}): {total_size_gaps[bw]}\n")
        file.write(f"总的 Lock Sizes (beam width {bw}): {total_lock_sizes[bw]}\n")
        file.write("\n")

# 打印总的 size_gaps 和 lock_sizes
for bw in beam_widths:
    print(f"总的 Size Gaps (beam width {bw}): {total_size_gaps[bw]}")
    print(f"总的 Lock Sizes (beam width {bw}): {total_lock_sizes[bw]}")