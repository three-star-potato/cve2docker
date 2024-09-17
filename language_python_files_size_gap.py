import json
import sys
from osv_python_one_size_analys import calculate_min_dependency_tree_size_beam_search,parse_version_constraint,calculate_dependency_tree_size_latest_version

from tqdm import tqdm
import os
import random

def read_products(filename):
    with open(filename, 'r') as json_file:
        return json.load(json_file)


def process_repository(repo_name, graph_size_require):
    # 读取 lock 文件和 unlock 文件中的依赖数据
    with open(f'language_python_files/{repo_name}_requirements.txt', 'r') as file:
        data = file.readlines()
       

    processed_dependencies_last_set = set()
    processed_dependencies_min_set_beam1=set()
    processed_dependencies_min_set_beam2=set()
    processed_dependencies_min_set_beam3=set()
    size_gap1 = 0
    size_gap2 = 0
    size_gap3 = 0
    for item in data:
        try:
            package_name, min_version_constraint, max_version_constraint = parse_version_constraint(item)
            path_min_beam1 = calculate_min_dependency_tree_size_beam_search(package_data=graph_size_require, package_name=package_name, version_constraints=item, beam_width=1)
            path_min_beam2 = calculate_min_dependency_tree_size_beam_search(package_data=graph_size_require, package_name=package_name, version_constraints=item, beam_width=2)
            path_min_beam3 = calculate_min_dependency_tree_size_beam_search(package_data=graph_size_require, package_name=package_name, version_constraints=item, beam_width=3)
            # print(path_min)
            path_last= calculate_dependency_tree_size_latest_version(package_data=graph_size_require, package_name=package_name, version_constraints=item)
            # print(path_last)
        except:
            path = [0, []]
        
        item_size_last = 0
        item_size_min_beam1=0
        item_size_min_beam2=0
        item_size_min_beam3=0

        if path_min_beam1[1] and path_min_beam2[1] and path_min_beam3[1] and path_last[1]:
            path_min_dependencies_list_beam1 = path_min_beam1[1]
            path_min_dependencies_list_beam2 = path_min_beam2[1]
            path_min_dependencies_list_beam3 = path_min_beam3[1]
            path_last_dependencies_list=path_last[1]
            while any(isinstance(dep, list) for dep in path_min_dependencies_list_beam1):
                new_dependencies_list = []
                for dep in path_min_dependencies_list_beam1:
                    if isinstance(dep, list):
                        new_dependencies_list.extend(dep)
                    else:
                        new_dependencies_list.append(dep)
                path_min_dependencies_list_beam1 = new_dependencies_list
            while any(isinstance(dep, list) for dep in path_min_dependencies_list_beam2):
                new_dependencies_list = []
                for dep in path_min_dependencies_list_beam2:
                    if isinstance(dep, list):
                        new_dependencies_list.extend(dep)
                    else:
                        new_dependencies_list.append(dep)
                path_min_dependencies_list_beam2 = new_dependencies_list
            while any(isinstance(dep, list) for dep in path_min_dependencies_list_beam3):
                new_dependencies_list = []
                for dep in path_min_dependencies_list_beam3:
                    if isinstance(dep, list):
                        new_dependencies_list.extend(dep)
                    else:
                        new_dependencies_list.append(dep)
                path_min_dependencies_list_beam3 = new_dependencies_list
            while any(isinstance(dep, list) for dep in path_last_dependencies_list):
                new_dependencies_list = []
                for dep in path_last_dependencies_list:
                    if isinstance(dep, list):
                        new_dependencies_list.extend(dep)
                    else:
                        new_dependencies_list.append(dep)
                path_last_dependencies_list = new_dependencies_list

            for dep in path_last_dependencies_list:
                if dep[1] in processed_dependencies_last_set:
                    continue
                size_last = graph_size_require[dep[0]][dep[1]]['size']
                item_size_last+=size_last
                processed_dependencies_last_set.add(dep[1])
            
            for dep in path_min_dependencies_list_beam1:
                if dep[1] in processed_dependencies_min_set_beam1:
                    continue
                size_min = graph_size_require[dep[0]][dep[1]]['size']
                item_size_min_beam1+=size_min
                processed_dependencies_min_set_beam1.add(dep[1])

            for dep in path_min_dependencies_list_beam2:
                if dep[1] in processed_dependencies_min_set_beam2:
                    continue
                size_min = graph_size_require[dep[0]][dep[1]]['size']
                item_size_min_beam2+=size_min
                processed_dependencies_min_set_beam2.add(dep[1])

            for dep in path_min_dependencies_list_beam3:
                if dep[1] in processed_dependencies_min_set_beam3:
                    continue
                size_min = graph_size_require[dep[0]][dep[1]]['size']
                item_size_min_beam3+=size_min
                processed_dependencies_min_set_beam3.add(dep[1])
                 
        print(item,item_size_last-item_size_min_beam1,item_size_last-item_size_min_beam2,item_size_last-item_size_min_beam3)
        gap1=item_size_last-item_size_min_beam1
        gap2=item_size_last-item_size_min_beam2
        gap3=item_size_last-item_size_min_beam3
        size_gap1+=gap1
        size_gap2+=gap2
        size_gap3+=gap3
    return size_gap1,size_gap2,size_gap3


# 用于存储每个仓库的 package-lock.json 和 package.json 是否满足条件
repo_status = {}

# 读取产品大小要求
graph_size_require = read_products('python_size_require.json')

satisfying_repos=[]
# 遍历 language_python_files 目录
directory_path = 'language_python_files'
for root, dirs, files in os.walk(directory_path):
    for file_name in files:
        # 检查是否为 package-lock.json 文件
        if file_name.endswith('_requirements.txt'):
            repo_name = file_name.replace('_requirements.txt', '')
            satisfying_repos.append(repo_name)
            
          



# 假设 satisfying_repos 和 process_repository 函数已经定义
random.seed(1010)
selected_repos = random.sample(satisfying_repos, min(100, len(satisfying_repos)))
print(selected_repos)

from tqdm import tqdm

# 读取已经处理的仓库
processed_repos = {}
try:
    with open('python_repo_size_gaps.txt', 'r') as file:
        for line in file:
            repo_name, size_gaps_str = line.strip().split(': ')
            size_gaps = {}
            for part in size_gaps_str.split(', '):
                key, value = part.split('=')
                size_gaps[key] = int(value)
            processed_repos[repo_name] = size_gaps
except FileNotFoundError:
    print("文件不存在，创建一个新的文件。")

total_size_gap1 = sum(item.get('size_gap1', 0) for item in processed_repos.values())
total_size_gap2 = sum(item.get('size_gap2', 0) for item in processed_repos.values())
total_size_gap3 = sum(item.get('size_gap3', 0) for item in processed_repos.values())

# 打开文件以追加模式写入
with open('python_repo_size_gaps.txt', 'a') as file:
    for repo_name in tqdm(selected_repos):
        if repo_name in processed_repos:
            print(f"{repo_name} 已经处理过，跳过")
            continue
        
        size_gap1, size_gap2, size_gap3 = process_repository(repo_name, graph_size_require)
        

        
        # 将处理过的仓库和对应的 size_gaps 存入字典
        processed_repos[repo_name] = {'size_gap1': size_gap1, 'size_gap2': size_gap2, 'size_gap3': size_gap3}
        
        # 将信息写入文件
        file.write(f"{repo_name}: size_gap1={size_gap1}, size_gap2={size_gap2}, size_gap3={size_gap3}\n")
        file.flush()  # 确保数据立即写入文件
        
        print(f"{repo_name}: size_gap1={size_gap1}, size_gap2={size_gap2}, size_gap3={size_gap3} 已写入文件")
                # 确保 size_gap1, size_gap2, size_gap3 都是非负数
        size_gap1 = max(size_gap1, 0)
        size_gap2 = max(size_gap2, 0)
        size_gap3 = max(size_gap3, 0)
        
        # 累加总的 size_gaps
        total_size_gap1 += size_gap1
        total_size_gap2 += size_gap2
        total_size_gap3 += size_gap3

# 打印总的 size_gaps
print(f"总的 size_gap1: {total_size_gap1}")
print(f"总的 size_gap2: {total_size_gap2}")
print(f"总的 size_gap3: {total_size_gap3}")
