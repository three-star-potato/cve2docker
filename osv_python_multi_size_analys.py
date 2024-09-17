#写一个读取width=3写出来的文件，俩俩组合 四四组合 五五组合  比较冲突数和平均大小
#再sort一下，因为字母序近的说不定依赖关系比较多
import json,re

import json  
from collections import defaultdict  
def find_line_numbers(filename, search_string):  
    line_numbers = []  
    with open(filename, 'r', encoding='utf-8') as file:  
        for line_num, line in enumerate(file, start=1):  
            if search_string in line:  
                line_numbers.append(line_num)  
    return line_numbers  
  

  
def get_lines_between_markers(filename, start_marker, end_marker=None):
    start_line_numbers = find_line_numbers(filename, start_marker)
    end_line_numbers = find_line_numbers(filename, end_marker) if end_marker else None
    
    # 确保找到了起始标记
    if not start_line_numbers:
        return []
    
    # 假设我们想要的是第一个起始标记和第一个结束标记之间的内容
    start_line = start_line_numbers[0]
    
    if end_marker:
        # 确保找到了结束标记
        if not end_line_numbers:
            return []
        end_line = end_line_numbers[0]
        
        # 如果结束标记在起始标记之前，则没有内容可提取
        if end_line <= start_line:
            return []
    else:
        end_line = None
    
    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        if end_line:
            return lines[start_line:end_line-1]
        else:
            return lines[start_line:]
  

  
def merge_json_tuples(data, merge_count):  
    if not isinstance(data, dict) or not isinstance(merge_count, int) or merge_count <= 0:  
        raise ValueError("Invalid input: data must be a dictionary and merge_count must be a positive integer.")  
    count=0 
    merged_data = {}  
    keys = list(data.keys())  
      
    for i in range(0, len(keys), merge_count):  
        group_tuples = []  
        for key in keys[i:i+merge_count]:  
            if isinstance(data[key], list):  
                group_tuples.extend(data[key])  # 假设值是元组列表  
          
        # 检查是否有冲突的元组  
        has_conflict = False  
        for tup in group_tuples:  
            if any(other_tup[0] == tup[0] and other_tup[1] != tup[1] for other_tup in group_tuples):  
                has_conflict = True  
                break  
          
        # 如果没有冲突，检查是否需要去重  
        if not has_conflict:  
            # 使用集合来去重  
            unique_tuples = list(set(group_tuples))  
              
            # 如果去重后列表长度变化，说明有重复  
            if len(unique_tuples) < len(group_tuples):  
                # 去重后写入  
                merged_key = f'merged_unique_{i // merge_count}'  
                merged_data[merged_key] = unique_tuples  
            else:  
                # 没有重复，原样写入  
                merged_key = f'merged_{i // merge_count}'  
                merged_data[merged_key] = group_tuples  
        else:  
            # 如果有冲突，整个组原样写入  
            merged_key = f'conflicted_{i // merge_count}'  
            merged_data[merged_key] = group_tuples  
            count=count+1
      
    return merged_data,count  
def read_products(filename):
    with open(filename, 'r') as json_file:
        return json.load(json_file)


def size_sum(dependencies,graph_size_require):
    size=0
    for product_item in dependencies:
        for dependence_item in set(dependencies[product_item]):
            # print(graph_size_require[dependence_item[0]][dependence_item[1]])
            size=size+graph_size_require[dependence_item[0]][dependence_item[1]]['size']
    return size


def parse_dependency_paths(lines):
    dependencies = {}
    for line in lines:
        try:
            product_name, raw_dependencies = line.split(':')
            product_dependence = []
            dependencies_list = eval(raw_dependencies.strip())
            while any(isinstance(item, list) for item in dependencies_list):
                new_dependencies_list = []
                for item in dependencies_list:
                    if isinstance(item, list):
                        new_dependencies_list.extend(item)
                    else:
                        new_dependencies_list.append(item)
                dependencies_list = new_dependencies_list
            product_dependence = dependencies_list
        except:
            continue
        dependencies[product_name] = product_dependence
    return dependencies


graph_size_require = read_products('python_size_require.json')
depend_path='python_dependency_paths.txt'
dependencies = {} 

Beam_Search_1=get_lines_between_markers(depend_path, 'Greedy Paths:', 'Beam Search Paths:')
Beam_Search_2=get_lines_between_markers(depend_path, 'Beam Search Paths:','Beam Search (width=3) Paths:')
Beam_Search_3 = get_lines_between_markers(depend_path, 'Beam Search (width=3) Paths:', 'Latest Version Paths:')  
last_path=get_lines_between_markers(depend_path, 'Latest Version Paths:') 
dependencies_1 = parse_dependency_paths(Beam_Search_1)
dependencies_2 = parse_dependency_paths(Beam_Search_2)
dependencies_3 = parse_dependency_paths(Beam_Search_3)
dependencies_last = parse_dependency_paths(last_path)

size_1 = size_sum(dependencies_1, graph_size_require)
size_2 = size_sum(dependencies_2, graph_size_require)
size_3 = size_sum(dependencies_3, graph_size_require)
size_last = size_sum(dependencies_last, graph_size_require)

print(f"Size of dependencies for Beam_Search_1: {size_1}")
print(f"Size of dependencies for Beam_Search_2: {size_2}")
print(f"Size of dependencies for Beam_Search_3: {size_3}")
print(f"Size of dependencies for last_path: {size_last}")
print(size_last-size_1,size_last-size_2,size_last-size_3,)

# Perform the merge for dependencies_1
merge_count = 4
merged_data_1, conflict_1 = merge_json_tuples(dependencies_1, merge_count)
merged_size_1 = size_sum(merged_data_1, graph_size_require)

# Perform the merge for dependencies_2
merged_data_2, conflict_2 = merge_json_tuples(dependencies_2, merge_count)
merged_size_2 = size_sum(merged_data_2, graph_size_require)

# Perform the merge for dependencies_3
merged_data_3, conflict_3 = merge_json_tuples(dependencies_3, merge_count)
merged_size_3 = size_sum(merged_data_3, graph_size_require)

# Perform the merge for dependencies_last
merged_data_last, conflict_last = merge_json_tuples(dependencies_last, merge_count)
merged_size_last = size_sum(merged_data_last, graph_size_require)

# Print conflict information
print(f"Conflicts during merge for Beam_Search_1: {conflict_1}")
print(f"Conflicts during merge for Beam_Search_2: {conflict_2}")
print(f"Conflicts during merge for Beam_Search_3: {conflict_3}")
print(f"Conflicts during merge for last_path: {conflict_last}")

# Print the merged sizes
print(f"Size of dependencies after merging for Beam_Search_1: {merged_size_1}")
print(f"Size of dependencies after merging for Beam_Search_2: {merged_size_2}")
print(f"Size of dependencies after merging for Beam_Search_3: {merged_size_3}")
print(f"Size of dependencies after merging for last_path: {merged_size_last}")

# Compare sizes before and after merging
print(f"Size difference after merging for Beam_Search_1: {size_last-merged_size_1}")
print(f"Size difference after merging for Beam_Search_2: {size_last-merged_size_2}")
print(f"Size difference after merging for Beam_Search_3: {size_last-merged_size_3 }")
print(f"Size difference after merging for last_path: {merged_size_last - size_last}")