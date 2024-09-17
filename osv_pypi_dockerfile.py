import docker
import os
import json
#######################
#得到一批构建python包的漏洞文件,逻辑是之前已经通过osv_pypi_product获取到了漏洞产品所能得到的所有版本，然后取交集


verion='python_3.11.6'

def scan_json_file(directory):
    # 遍历指定目录下的所有文件和子目录
    for root, dirs, files in os.walk(directory):
        for file in files:
            # 检查文件名是否以3.7开头并且以.json为扩展名
            if file.startswith(verion) and file.endswith('.json'):
                # 构建完整的文件路径并返回
                return os.path.join(root, file)
    
    # 如果没有找到匹配的文件，则返回None
    return None

filepath=scan_json_file('./')

with open('osv_cve_build.json', 'r') as json_file:
    json_data = json.load(json_file)

with open(filepath, 'r') as json_file:
    product_with_python_version = json.load(json_file)
vul_python_versions={}
for item in json_data:
    try:
        affected = json_data[item]['affected']
    except KeyError:
        print("ecosystem键值不存在")
        continue
    product_name=None
    for affected_item in affected:
        product_lists=[]
        if affected_item:
            ecosystem = affected_item.get('package', {}).get('ecosystem')
            verions=affected_item.get('versions', None)
            print(verions)
            if ecosystem == 'PyPI' and verions:
                product_lists =product_lists+affected_item.get("versions")
                product_name = affected_item['package'].get("name")
    if product_name and product_lists:
        vul_intersection = list(set( product_with_python_version[product_name]) & set(product_lists)) #交集
        vul_python_versions[product_name]=vul_intersection

# 写入 JSON 文件
with open('python_dockerfile/'+verion+'vul_python_versions.json', 'w') as json_file:
    json.dump(vul_python_versions, json_file, indent=4)

print("完成")