# 图谱构建


"""
最终输出格式：
{
product:{
package_version:{
    include_python_verion:[],
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

with open('python_3.11.6 (main, Nov 29 2023, 04:19:53) [GCC 12.2.0]_product_versions.json', 'r') as json_file:
    vul_products_311=json.load(json_file)



vul_products_311_release=[]


for vul_products_key in vul_products_311:
    for release_item in vul_products_311[vul_products_key]:
        vul_products_311_release.append(vul_products_key+'_'+release_item)  


keys_3_11 = set(vul_products_311.keys())
# 获取所有版本的键的并集


all_product={}
with open('python_size_require.json', 'r') as json_file:
    all_product=json.load(json_file)
    for key  in tqdm(keys_3_11,desc="Processing"):
        product={}
        if key in all_product:
            print('exist')
            continue
        else:
            print('download')   
        product_url = f"https://pypi.org/pypi/{key}/json"
        product_response = requests.get(product_url)
        if product_response.status_code == 200:
            product_data = product_response.json()
            # 现在你可以处理 JSON 数据了
            for release in tqdm(product_data['releases'],desc="Processing"):
                if release:
                    release_url=  f"https://pypi.org/pypi/{key}/{release}/json"
                    release_response=requests.get(release_url)
                    if release_response.status_code == 200:
                        release_data = release_response.json()
                        key_release=key+'_'+release
                        include_python_verion=[]

                        if key_release in vul_products_311_release:
                            include_python_verion.append('python311')

                        # time.sleep(1)
                        if release_data['urls']:
                            product[key_release]={
                                'size':release_data['urls'][0]['size'],
                            'requirelist': release_data['info']['requires_dist'],
                            'include_python_verion':include_python_verion
                            }
            

                    else:
                        print("版本请求失败，状态码：", release_response.status_code)
                    # print(product)
        else:
            print("包请求失败，状态码：", product_response.status_code)
        all_product[key]=product
        # print(all_product)
        with open('python_size_require.json', 'w') as json_file:
            json.dump(all_product, json_file, indent=4)
            # 总共爬了2825份