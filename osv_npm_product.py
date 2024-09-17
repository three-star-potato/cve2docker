import re
import subprocess
import sys
import json
from tqdm import tqdm
#用来查看下载node包所支持的版本的小脚本，脚本在npm_get_from_docker中使用
#########################################################
def run_command(command):
    try:
        # 执行命令并捕获输出
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        # 如果命令成功执行，则返回标准输出
        if result.returncode == 0:
            return result.stdout
        # 如果命令执行失败，则返回标准错误
        else:
            return result.stderr
    except Exception as e:
        return str(e)
def build_comand(product):
    command='npm show '+product+' versions'
    return command

def get_version(product):
    command = build_comand(product)

      # 运行命令并获取输出
    output = run_command(command)
    # print(output)
    # 输出结果

    
    versions = re.findall(r'\b\d+\.\d+\.\d+\b(?<!-)', output)#不匹配什么预发布版本了
    versions=list(set(versions))

    if versions:
        # print(versions)
        return versions
    else:
        print(command,"未找到'")
        return[]

######################################################################



with open('osv_cve_build.json', 'r') as json_file:
    json_data = json.load(json_file)

npmproduct = set()  # 使用集合来存储唯一的产品名称
count=0
for item in json_data:
    try:
        affected = json_data[item]['affected']
    except KeyError:
        print("ecosystem键值不存在")
        continue
    for affected_item in affected:
        if affected_item:
            ecosystem = affected_item.get('package', {}).get('ecosystem')
            if ecosystem == 'npm':
                product_name = affected_item['package'].get("name")
                if product_name:
                    npmproduct.add(product_name)  # 将产品名称添加到集合中


print(len(npmproduct))
product_vertion_json={}
# 获取当前安装的Node.js版本
def get_node_version():
    try:
        # 使用node命令行工具查询其版本
        result = subprocess.run(['node', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # 如果命令执行成功，返回版本信息
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"Error: {result.stderr}"
    except FileNotFoundError:
        return "Node.js is not installed."
node_version = get_node_version()
print("当前 node 版本：", node_version)
for product in tqdm(npmproduct, desc="获取版本信息"):
    print(product)
    product_vertion_json[product]=get_version(product)

    # 写入 JSON 文件
    with open('node_'+node_version+'_product_versions.json', 'w') as json_file:
        json.dump(product_vertion_json, json_file, indent=4)

print("产品版本信息已写入 product_versions.json 文件")