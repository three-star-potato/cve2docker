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

vul_products_311 = read_products('python_dockerfile/python_3.11.6vul_python_versions.json')
graph_size_require = read_products('python_size_require.json')
random.seed(1010)
vul_products_unique = get_unique_products(vul_products_311)
vul_products_unique_random100=random.sample(vul_products_unique, 100)

vul_products_311_release=[]


for vul_products_key in vul_products_311:
    for release_item in vul_products_311[vul_products_key]:
        vul_products_311_release.append(vul_products_key+'_'+release_item)  


def parse_version_constraint(constraint):
    try:
        constraint = re.sub(r'\s*;\s*extra\s*==\s*"[a-zA-Z0-9_-]+"', '', constraint)
        constraint = re.sub(r'\s+or\s+extra\s*==\s*"[^"]+"', '', constraint)
        constraint = re.sub(r'\sand\s.*', '', constraint)
        constraint = re.sub(r';.*', '', constraint)
        constraint = constraint.replace('*', '0')
        
        req = Requirement(constraint)
        package_name = req.name
        specifier_set = req.specifier
        min_version = None
        max_version = None

        for specifier in specifier_set:
            if specifier.operator in ('>=', '=='):
                min_version = specifier
            elif specifier.operator in ('<', '=='):
                max_version = specifier

        return package_name, str(min_version) if min_version else None, str(max_version) if max_version else None
    except Exception as e:
        # First, try to match the format with two version constraints
               # 尝试匹配没有版本约束的格式
        match = re.match(r'([^\s]+)$', constraint)
        if match:
            package_name = match.group(1)
            return package_name, None, None
        match = re.match(r'([^\s]+)\s+\((>=|<=|==|>|<)([^\s<>=]+)\s*,\s*(>=|<=|==|>|<)([^\s<>=]+)\)', constraint)
        if match:
            package_name = match.group(1)
            min_version_op = match.group(2)
            min_version = match.group(3)
            max_version_op = match.group(4)
            max_version = match.group(5)
            return package_name, min_version_op + min_version, max_version_op + max_version
        
        # If the first format does not match, try to match the format with a single version constraint
        match = re.match(r'([^\s]+)\s+\((>=|<=|==|>|<)([^\s<>=]+)\)', constraint)
        if match:
            package_name = match.group(1)
            version_op = match.group(2)
            version = match.group(3)
            if version_op in ('>=', '>'):
                min_version = version_op + version
                max_version = None
            else:
                min_version = None
                max_version = version_op + version
            return package_name, min_version, max_version
        else:
            print(f"Unrecognized constraint format: {constraint}")
            return None, None, None

def version_in_range(version, min_version, max_version):
    try:
        version_obj = Version(version)
    except InvalidVersion:
        return False
    try:
        min_version_obj = Version(min_version[2:]) if min_version else None
        max_version_obj = Version(max_version[1:]) if max_version else None
    except InvalidVersion as e:
        return False

    if min_version_obj and max_version_obj:
        return min_version_obj <= version_obj < max_version_obj
    elif min_version_obj:
        return min_version_obj <= version_obj
    elif max_version_obj:
        return version_obj < max_version_obj

    return True


def find_latest_version(package_versions, version_constraints):
    # 解析版本约束
    if version_constraints:
        package_name, min_version_constraint, max_version_constraint = parse_version_constraint(version_constraints)
    else:
        min_version_constraint = max_version_constraint = None
    if not package_name:
        return None

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
            package_name, min_version_constraint, max_version_constraint = parse_version_constraint(version_constraints)
            if not package_name:
                continue
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
            for required_constraint in list(set(requirelist)):
                required_package, min_version_constraint, max_version_constraint = parse_version_constraint(required_constraint)
                if required_package:
                    sub_path = dfs_latest(required_package, required_constraint, (0, []), visited.copy(), depth - 1)
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
                for required_constraint in list(set(requirelist)):
                    required_package, min_version_constraint, max_version_constraint = parse_version_constraint(required_constraint)
                    if required_package:
                        sub_path = dfs_beam(required_package, required_constraint, (0, []), visited.copy(), depth - 1)
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
        with open("python_time_results.txt", "a") as f:
            f.write(f"{strategy_name}: Time = {results[strategy_name]['Time']}\n")

        with open("python_dependency_paths.txt", "a") as f:
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
if __name__ == "__main__":
# 获取结果并打印
    results = evaluate_strategies(vul_products_unique_random100, vul_products_311_release, graph_size_require)
    print('ok')
