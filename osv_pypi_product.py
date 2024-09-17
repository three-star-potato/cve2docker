import re
import subprocess
import sys
import json
from tqdm import tqdm
#用来查看下载python包所支持的版本的小脚本，脚本在pypi_get_from_docker中使用
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
    command='pip install '+product+'=='
    return command

def get_version(product):
    command = build_comand(product)

    # 运行命令并获取输出
    output = run_command(command)
    print(output)
    # 输出结果

    # 找到 "(from versions:" 的位置
    match = re.search(r'\(from versions:', output)
    endmatch=re.search(r'ERROR: No matching distribution found for',output)

    if match:
        # 获取匹配到的位置的索引
        start_index = match.start() + len('(from versions:')
        
        # 从这个索引开始，到字符串末尾
        version_part = output[start_index:endmatch.start()].strip()[:-1]

        # 去掉前后空格，然后用逗号分割
        versions = [version.strip() for version in version_part.split(',')]

        return versions
    else:
        print("未找到 '(from versions:'")
        return[]
######################################################################



with open('osv_cve_build.json', 'r') as json_file:
    json_data = json.load(json_file)

pypiproduct = set()  # 使用集合来存储唯一的PyPI产品名称

for item in json_data:
    try:
        affected = json_data[item]['affected']
    except KeyError:
        print("ecosystem键值不存在")
        continue
    for affected_item in affected:
        if affected_item:
            ecosystem = affected_item.get('package', {}).get('ecosystem')
            if ecosystem == 'PyPI':
                product_name = affected_item['package'].get("name")
                if product_name:
                    pypiproduct.add(product_name)  # 将产品名称添加到集合中


print(len(pypiproduct))
product_vertion_json={}
python_version = sys.version
print("当前 Python 版本：", python_version)
for product in tqdm(pypiproduct, desc="获取版本信息"):
    product_vertion_json[product]=get_version(product)

# 写入 JSON 文件
with open('python_'+python_version+'_product_versions.json', 'w') as json_file:
    json.dump(product_vertion_json, json_file, indent=4)

print("产品版本信息已写入 product_versions.json 文件")