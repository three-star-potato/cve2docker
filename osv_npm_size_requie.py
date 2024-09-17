

"""
最终输出格式：
{
product:{
package_version:{
    size:''
    requirelist:[]
    },

    }

}

"""
import json
import requests
import time
from tqdm import tqdm
import os 
import re
with open('node_v20.13.1_product_versions.json', 'r') as json_file:
    vul_products_20=json.load(json_file)



vul_products_20_release=[]


for vul_products_key in vul_products_20:
    for release_item in vul_products_20[vul_products_key]:
        vul_products_20_release.append(vul_products_key+'_'+release_item)  


count=0
with open('language_node_repositories.txt', 'r', encoding='utf-8') as file:
    repo_names = file.readlines()
requirements_dir = 'language_node_package_files'
repo_products=[]
for repo_name in tqdm(repo_names, desc='Processing repositories'):
    repo_name = repo_name.strip()  # Remove any leading/trailing whitespace
    file_path = os.path.join(requirements_dir, f"{repo_name.replace('/', '_')}_package.json")

    # Check if we already have the file
    if os.path.isfile(file_path):
        with open (file_path,'r', encoding='utf-8') as require_file:
            # try:
            require_content = json.load(require_file)
            if 'dependencies' in require_content:
                require_dependencies=require_content['dependencies']
            else:
                require_dependencies=None
                # print(file_path)
            # except Exception as e:
            #     print(f"Error: {e}")
            #     require_content=None
                
    else:
        continue
    if not require_dependencies:
        count=count+1
        print(count)
        continue
    repo_product = [key for key, value in require_dependencies.items() if 'workspace' not in value and 'link:'not in value]#不需要从外部依赖下载
    # print(repo_product)
    repo_products += repo_product
print(len(set(repo_products)))
print(repo_products[:10])

all_keys = set(vul_products_20.keys())

reqiurelist=[]

all_product={}
with open('node_size_require.json', 'r', encoding='utf-8') as json_file:
    vul_product=json.load(json_file)
    vul_keys=vul_product.keys()
    
    for vul_key in vul_keys:
        for release in vul_product[vul_key]:
            if vul_product[vul_key][release]['requirelist']:
                reqiurelist+=vul_product[vul_key][release]['requirelist'].keys()
    print(reqiurelist[:10])


    requirelist=list(set(reqiurelist))
    print(len(requirelist))
    repo_products=list(set(repo_products))
    vul_repo_requirelist=list(set(repo_products+requirelist+list(all_keys)))#集合漏洞版本 漏洞需求版本和所有的requirelist
    print(len(vul_repo_requirelist))
                                      
    vul_repo_requirelist.sort() 
    print(vul_repo_requirelist[:10])
    all_product=vul_product
    for key  in tqdm(vul_repo_requirelist,desc="Processing"):
        product={}
        if key in all_product:
            print(key,'exist')
            continue
        else:
            print(key,'download')   
        product_url = f"https://registry.npmjs.org/{key}"
        product_response = requests.get(product_url)
        if product_response.status_code == 200:
            product_data = product_response.json()
            # print(product_data)
            time.sleep(2)
            if 'versions' not in product_data:
                all_product[key]=product
                continue
            for release in tqdm(product_data['versions'],desc="Processing"):
                # print(release)
                if all(part.isdigit() for part in release.split('.')):
                    key_release=key+'_'+release
                    if 'unpackedSize' in product_data['versions'][release]['dist'] and 'dependencies' in product_data['versions'][release]:
                        product[key_release]={
                            'size':product_data['versions'][release]['dist']['unpackedSize'],
                            'requirelist': product_data['versions'][release]['dependencies'],
                        }
            
        else:
            print("包请求失败，状态码：", product_response.status_code)
            time.sleep(120)  # 等待两分钟后重试
        all_product[key]=product
        # print(all_product)
        with open('node_size_require.json', 'w', encoding='utf-8') as json_file:
            json.dump(all_product, json_file, indent=4)
