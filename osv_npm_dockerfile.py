import docker
import os
import json
import re
from tqdm import tqdm
#######################
#得到一批构建node包的漏洞文件,逻辑是之前已经通过osv_pypi_product获取到了漏洞产品所能得到的所有版本，然后取交集
from packaging import version

node_verion='node_v20.13.1'
# verion='node_v18.20.3'
# verion='node_v16.20.2'
# verion='node_v14.21.3'
# verion='node_v12.22.12'
def scan_json_file(directory):
    # 遍历指定目录下的所有文件和子目录
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.startswith(node_verion) and file.endswith('.json'):
                # 构建完整的文件路径并返回
                return os.path.join(root, file)
    
    # 如果没有找到匹配的文件，则返回None
    return None

filepath=scan_json_file('./')

with open('osv_cve_build.json', 'r') as json_file:
    json_data = json.load(json_file)

with open(filepath, 'r') as json_file:
    product_with_node_version = json.load(json_file)
vul_node_versions={}

# 定义一个正则表达式来匹配预发布版本
pre_release_pattern = re.compile(r'^[0-9]+\.[0-9]+\.[0-9]+$')


def strip_pre_release(version_str):
    """去掉预发布标签，只保留主要版本号"""
    return version_str.split('-')[0]

for item in tqdm(json_data):
    try:
        affected = json_data[item]['affected']
    except KeyError:
        print("ecosystem键值不存在")
        continue
    product_name=None
    product_lists=[]
    for affected_item in affected:
        if affected_item:
            ecosystem = affected_item.get('package', {}).get('ecosystem')
            is_exist_range=affected_item.get('ranges', None)
            if not is_exist_range:
                continue
            verions_range=is_exist_range[0].get('events')#这个地方npm和python不一样，没有直接的标明的版本，要引入语义化的解析工具计算它们之间的版本
            if verions_range:
                verion_start=strip_pre_release( verions_range[0]['introduced'])
                version_end = strip_pre_release (verions_range[1]['fixed'] )if len(verions_range) > 1 and 'fixed' in verions_range[1] else None#左闭右开
            if ecosystem == 'npm' and verions_range:
                product_name = affected_item['package'].get("name")
                product_version=product_with_node_version[product_name]
                # 筛选版本，过滤掉预发布版本
                filtered_versions = [ v for v in product_version if pre_release_pattern.match(v)]
                # print(filtered_versions)
                if version_end :
                    affected_versions = [ v for v in filtered_versions if version.parse(verion_start) <= version.parse(v) < version.parse(version_end)]
                else:
                    affected_versions = [ v for v in filtered_versions if version.parse(verion_start) <= version.parse(v) ]
                product_lists =product_lists+affected_versions
    if product_name and product_lists:
        vul_node_versions[product_name]= list(set(product_lists)) #交集

# 写入 JSON 文件
with open('node_dockerfile/'+node_verion+'vul_node_versions.json', 'w') as json_file:
    json.dump(vul_node_versions, json_file, indent=4)

print("完成")