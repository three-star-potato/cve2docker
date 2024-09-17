import pandas as pd
import os
import json
from tqdm import tqdm
from datetime import datetime
# 处理单个JSON文件
def process_json_file(file_path):
    try:
        with open(file_path, 'r') as json_file:
            json_data = json.load(json_file)

            # 初始化结果字典
            processed_data = {}

            # 提取CVE编号
            aliases = json_data.get('aliases', [''])

            for item in aliases:
                if 'CVE' in item:
                    cveId=item
                    break
                else:
                    cveId=None
                if not cveId:
                    return {}
            affected = json_data.get('affected', None)
            osv_detail = json_data.get('details', None)
            osv_sum=json_data.get('summary', None)
            if cveId and affected and osv_detail and osv_sum:

                processed_data[cveId] = {
                        'osv_detail': osv_detail,
                        'osv_sum': osv_sum,
                        'affected': affected,
                    }
                return processed_data
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return {}

def process_files(folder_path,specific_dirs):
    cve_edb = {}
    specific_paths = [os.path.join(folder_path, specific_dir) for specific_dir in specific_dirs]
    # 收集所有JSON文件路径，但只在特定目录中查找
    json_files = [os.path.join(root, file)
                  for root, dirs, files in os.walk(folder_path)
                  for file in files if file.endswith('.json') and root in specific_paths]
    
    # 使用tqdm创建进度条
    for file_path in tqdm(json_files, desc="Processing Files", unit="file"):
        data = process_json_file(file_path)
        if data:
            cve_edb.update(data)
    
    return cve_edb

# 主函数
def main():
    folder_path = 'osv'
    specific_dirs = [ 'npm','PyPI']
    
    # 处理JSON文件
    osv_edb = process_files(folder_path,specific_dirs)
    
    # 写入JSON文件
    with open('osv_cve_build.json', 'w') as json_file:
        json.dump(osv_edb, json_file, indent=4)
        print(f"字典已成功写入到文件: osv_cve_build.json")

if __name__ == "__main__":
    main()
