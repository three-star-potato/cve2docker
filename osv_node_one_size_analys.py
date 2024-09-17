import re
import json
import heapq
import time
from tqdm import tqdm
from packaging.requirements import Requirement
from packaging.version import Version, InvalidVersion
from packaging import version
import random
def read_products(filename):
    with open(filename, 'r') as json_file:
        return json.load(json_file)

def get_unique_products(vul_products):
    return list(vul_products.keys())

vul_products_311 = read_products('node_dockerfile/node_v20.13.1vul_node_versions.json')
graph_size_require = read_products('node_size_require.json')
random.seed(1010)
vul_products_unique = get_unique_products(vul_products_311)
vul_products_unique_random100=random.sample(vul_products_unique, 100)

vul_products_311_release=[]


for vul_products_key in vul_products_311:
    for release_item in vul_products_311[vul_products_key]:
        vul_products_311_release.append(vul_products_key+'_'+release_item)  


def parse_node_version_constraint(constraint):
    min_version = None
    max_version = None

    if '>=' in constraint:
        min_version = constraint.split('>=')[1].strip()
    elif '>' in constraint:
        min_version = constraint.split('>')[1].strip()

    if '<=' in constraint:
        max_version = constraint.split('<=')[1].strip()
    elif '<' in constraint:
        max_version = constraint.split('<')[1].strip()

    if '~' in constraint:
        version = constraint.split('~')[1].strip()
        parts = version.split('.')
        if len(parts) >= 2 :
            try:
                min_version = f"{parts[0]}.{parts[1]}.0"
                max_version = f"{parts[0]}.{int(parts[1]) + 1}.0"
            except ValueError as e:
                print(f"版本号部分无法转换为整数: {parts[1]}")
                print(f"错误详情: {e}")
        else:
            print(f"无效的版本格式用于 '~' 约束: {version}")

    if '^' in constraint:
        version = constraint.split('^')[1].strip()
        parts = version.split('.')
        if len(parts) >= 2:
            try:
                min_version = f"{parts[0]}.{parts[1]}.0"
                max_version = f"{parts[0]}.{int(parts[1]) + 1}.0"
            except ValueError as e:
                print(f"版本号部分无法转换为整数: {parts[1]}")
                print(f"错误详情: {e}")
        else:
            print(f"无效的版本格式用于 '^' 约束: {version}")

    if '*' in constraint or 'x' in constraint:
        min_version = '0.0.0'
        max_version = '9999.9999.9999'

    return min_version, max_version


def version_in_range(version_str, min_version_str=None, max_version_str=None):
    try:
        version_obj = version.parse(version_str)
    except version.InvalidVersion:
        print(f"Invalid version: '{version_str}'")
        return False

    if min_version_str is not None:
        try:
            min_version_obj = version.parse(min_version_str)
            if version_obj < min_version_obj:
                return False
        except version.InvalidVersion:
            print(f"Invalid minimum version: '{min_version_str}'")
            return False

    if max_version_str is not None:
        try:
            max_version_obj = version.parse(max_version_str)
            if version_obj > max_version_obj:
                return False
        except version.InvalidVersion:
            print(f"Invalid maximum version: '{max_version_str}'")
            return False

    return True

def find_latest_version(package_versions, version_constraints):
    # 解析版本约束
    if version_constraints:
        min_version_constraint, max_version_constraint = parse_node_version_constraint(version_constraints)
    else:
        min_version_constraint = max_version_constraint = None

    # 过滤符合版本约束的版本
    filtered_versions = [
        version for version in package_versions.keys()
        if not version_constraints or version_in_range(version.split('_')[-1], min_version_constraint, max_version_constraint)
    ]

    # 如果没有符合条件的版本，返回 None
    if not filtered_versions:
        return None

    # 对版本进行排序并返回最新的版本
    return max(filtered_versions, key=lambda v: version.parse(v.split('_')[-1]))


def find_min_size_versions(package_versions, version_constraints, beam_width):
    versions_with_size = []

    for version, details in package_versions.items():
        if version_constraints:
            min_version_constraint, max_version_constraint = parse_node_version_constraint(version_constraints)
            if not version_in_range(version.split('_')[-1], min_version_constraint, max_version_constraint):
                continue

        versions_with_size.append((details['size'], version))

    if beam_width is None:
        return versions_with_size
    else:
        return heapq.nsmallest(beam_width, versions_with_size)

def calculate_dependency_tree_size_latest_version(package_data, package_name, version_constraints=None):
    def dfs_latest(current_package, current_constraints, paths_sizes, visited, depth):
        if depth == 0 or current_package not in package_data:
            return []
        if current_package in visited:
            return []  # 避免循环和重新安装同一个包
        package_versions = package_data[current_package]
        latest_version = find_latest_version(package_versions, current_constraints)
        if not latest_version:
            return []
        visited.add(current_package)  # 标记当前包为已访问
        all_paths = []
        try:
            last_size=package_versions[latest_version]['size']
        except:
            last_size=0
        
        new_path = paths_sizes[1] + [(current_package, latest_version)]
        total_size = paths_sizes[0] + last_size
        requirelist = package_versions[latest_version]['requirelist']
        path_size = (total_size, new_path)
        if requirelist:
            sub_paths = []
            for required_package in requirelist:
                sub_path = dfs_latest(required_package, requirelist[required_package], (0, []), visited.copy(), depth - 1)
                print(required_package,sub_path)
                if sub_path:
                    sub_paths.append(sub_path[0])  # 只取每个依赖的最小路径

            # 组合子路径形成完整路径
            if sub_paths:
                combined_size = path_size[0] + sum(sub_path[0] for sub_path in sub_paths)
                combined_path = path_size[1] + [sub_path[1] for sub_path in sub_paths]
                all_paths.append((combined_size, combined_path))
            else:
                all_paths.append(path_size)
        else:
            all_paths.append(path_size)

        return all_paths
    initial_paths_size = dfs_latest(package_name, version_constraints, (0, []), set(), 5)
    try:
        min_path_size = min(initial_paths_size, key=lambda x: x[0])
    except:
        min_path_size = (0, [])
        print('没有找到合适的路径')
    return min_path_size

def calculate_min_dependency_tree_size_beam_search(package_data, package_name, version_constraints=None, beam_width=1):
    def dfs_beam(current_package, current_constraints, paths_sizes, visited, depth):
        if depth == 0 or current_package not in package_data:
            return []
        if current_package in visited:
            return []  # Avoid cycles and reinstallation of the same package
        package_versions = package_data[current_package]
        min_versions = find_min_size_versions(package_versions, current_constraints, beam_width)
        visited.add(current_package)  # Mark the current package as visited
        all_paths = []
        for min_size, min_version in min_versions:
            new_path = paths_sizes[1] + [(current_package, min_version)]
            total_size = paths_sizes[0] + min_size
            requirelist = package_versions[min_version]['requirelist']
            path_size = (total_size, new_path)
            if requirelist:
                sub_paths = []
                for required_package in requirelist:
                    sub_path = dfs_beam(required_package, requirelist[required_package], (0, []), visited.copy(), depth - 1)
                    if sub_path:
                        sub_paths.append(sub_path[0])  # Only take the smallest path for each dependency

                # Combine sub-paths to form full paths
                if sub_paths:
                    combined_size = path_size[0] + sum(sub_path[0] for sub_path in sub_paths)
                    combined_path = path_size[1] + [sub_path[1] for sub_path in sub_paths]
                    all_paths.append((combined_size, combined_path))
                else:
                    all_paths.append(path_size)
            else:
                all_paths.append(path_size)

        # Only keep the top beam_width paths
        all_paths.sort(key=lambda x: x[0])
        return all_paths[:beam_width]

    initial_paths_size = dfs_beam(package_name, version_constraints, (0, []), set(), 5)
    try:
        min_path_size = min(initial_paths_size, key=lambda x: x[0])
    except:
        min_path_size = (0, [])
        print('没有找到合适的路径')
    return min_path_size

def evaluate_strategies(vul_products_unique, vul_products_311_release, graph_size_require):
    results = {
        "Greedy": {"Time": 0, "Paths": []},
        "Beam Search": {"Time": 0, "Paths": []},
        "Beam Search (width=3)": {"Time": 0, "Paths": []},
        "Greedy with Versions": {"Time": 0, "Paths": []},
        "Beam Search with Versions": {"Time": 0, "Paths": []},
        "Beam Search with Versions (width=3)": {"Time": 0, "Paths": []},
        "Latest Version": {"Time": 0, "Paths": []},
    }

    def evaluate(strategy_name, beam_width, products, with_versions=False, latest_version=False):
        start_time = time.time()
        for item in tqdm(products, desc=f"Evaluating unique products ({strategy_name})"):
            if with_versions:
                package_name, version_constraint = item.split('_')
                if latest_version:
                    _, path = calculate_dependency_tree_size_latest_version(graph_size_require, package_name, version_constraints=version_constraint)
                else:
                    _, path = calculate_min_dependency_tree_size_beam_search(graph_size_require, package_name, version_constraints=version_constraint, beam_width=beam_width)
            else:
                if latest_version:
                    _, path = calculate_dependency_tree_size_latest_version(graph_size_require, item)
                else:
                    _, path = calculate_min_dependency_tree_size_beam_search(graph_size_require, item, beam_width=beam_width)
            
            results[strategy_name]["Paths"].append((item, path))
        results[strategy_name]["Time"] = time.time() - start_time
        write_results_to_file(strategy_name)

    def write_results_to_file(strategy_name):
        with open("node_time_results.txt", "a") as f:
            f.write(f"{strategy_name}: Time = {results[strategy_name]['Time']}\n")

        with open("node_dependency_paths.txt", "a") as f:
            f.write(f"\n{strategy_name} Paths:\n")
            for product, path in results[strategy_name]["Paths"]:
                f.write(f"{product}: {path}\n")

    # Evaluate original products without versions
    evaluate("Greedy", beam_width=1, products=vul_products_unique)
    evaluate("Beam Search", beam_width=2, products=vul_products_unique)
    evaluate("Beam Search (width=3)", beam_width=3, products=vul_products_unique)
    evaluate("Latest Version", beam_width=1, products=vul_products_unique, latest_version=True)

    # Evaluate products with versions
    # evaluate("Greedy with Versions", beam_width=1, products=vul_products_311_release, with_versions=True)
    # evaluate("Beam Search with Versions", beam_width=2, products=vul_products_311_release, with_versions=True)
    # evaluate("Beam Search with Versions (width=3)", beam_width=3, products=vul_products_311_release, with_versions=True)
    # evaluate("Latest Version with Versions", beam_width=1, products=vul_products_311_release, with_versions=True, latest_version=True)

    return results

# 获取结果并打印
if __name__ == "__main__":
    results = evaluate_strategies(vul_products_unique_random100, vul_products_311_release, graph_size_require)
    print('ok')
