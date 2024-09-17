import os
import json

# 获取当前目录
current_directory = os.getcwd()

# 获取当前目录下的所有文件
files = os.listdir(current_directory)

# 选取所有json文件
json_files = [file for file in files if file.endswith('.json')]

# 统计每个json文件键对应的值不为空列表的键个数
for json_file in json_files:
    with open(json_file, 'r') as f:
        file_data = json.load(f)
        non_empty_keys_count = sum(1 for value in file_data.values() if value != [])
        print(f"{json_file}: {non_empty_keys_count} non-empty keys")
