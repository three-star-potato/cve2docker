# 这个代码是为了解决只有漏洞的大小，没有依赖的大小的问题
import json 
from tqdm import tqdm
import requests 
import re,os
import random
import string
reqiurelist=[]
import time

# 列表中包含了不同的User-Agent字符串
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1",
    "Mozilla/5.0 (Linux; Android 8.0; SM-G960F Build/R16NW) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.84 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 7.0; SM-G930V Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.83 Mobile Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:50.0) Gecko/20100101 Firefox/50.0"
]


# 现在你可以使用这个headers字典来发送请求

# proxy_list = [
#     'http://66.235.200.74',
#     'http://172.67.253.207',
#     # ... 更多代理
# ]

# def get_proxy():
#     return random.choice(proxy_list)
def is_valid_line(line):
    """ Check if the line is valid: does not contain non-printable characters, '#', '\\',
    or start with '-e ' or '-r ' """
    if not all(char in string.printable for char in line):
        return False
    if '#' in line or '\\' in line:
        return False
    if line.strip().startswith('-') or line.strip().startswith('https://') :
        return False
    return True
with open('language_python_repositories.txt', 'r') as file:
    repo_names = file.readlines()
requirements_dir = 'language_python_files'
repo_products=[]
for repo_name in tqdm(repo_names, desc='Processing repositories'):
    repo_name = repo_name.strip()  # Remove any leading/trailing whitespace
    file_path = os.path.join(requirements_dir, f"{repo_name.replace('/', '_')}_requirements.txt")

    # Check if we already have the file
    if os.path.isfile(file_path):
        with open (file_path,'r') as require_file:
            require_content=require_file.readlines()
    else:
        continue
    repo_product = [
        re.sub(r'[>=<;!([~].*', '', require_package).strip()
        for require_package in require_content
        if is_valid_line(require_package)
    ]
    repo_products += repo_product
print(len(set(repo_products)))
print(repo_products[:10])

with open('python_size_require.json', 'r') as json_file:
    vul_product=json.load(json_file)
    vul_keys=vul_product.keys()
    
    for vul_key in vul_keys:
        for release in vul_product[vul_key]:
            if vul_product[vul_key][release]['requirelist']:
                reqiurelist+=vul_product[vul_key][release]['requirelist']
    print(reqiurelist[:10])

    just_product_requirelist = [re.sub(r'[>=<;!([~].*', '', item).strip() for item in reqiurelist]
    print(just_product_requirelist[:10])
    just_product_requirelist=list(set(just_product_requirelist))
    print(len(just_product_requirelist))
    repo_products=list(set(repo_products))
    just_product_requirelist=list(set(repo_products+just_product_requirelist))
    print(len(just_product_requirelist))
                                      
    just_product_requirelist.sort() 
    print(just_product_requirelist[:10])
    all_product=vul_product
    for key  in tqdm(just_product_requirelist,desc="Processing"):
        product={}
        if key in all_product:
            print(key,'exist')
            continue
        else:
            print(key,'download')   
        product_url = f"https://pypi.org/pypi/{key}/json"
        time.sleep(1)
        # proxy = get_proxy()
        # proxies = {'http': proxy, 'https': proxy}
        # 随机选择一个User-Agent
        selected_user_agent = random.choice(user_agents)

        # 创建请求头
        headers = {
            'User-Agent': selected_user_agent
        }

        product_response = requests.get(product_url, headers=headers)
        if product_response.status_code == 200:
            product_data = product_response.json()
            # 现在你可以处理 JSON 数据了
            for release in tqdm(product_data['releases'],desc="Processing"):
                if release:
                    release_url=  f"https://pypi.org/pypi/{key}/{release}/json"
                    release_response=requests.get(release_url, headers=headers)
                    if release_response.status_code == 200:
                        release_data = release_response.json()
                        key_release=key+'_'+release
                        include_python_verion=None
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
            print("包请求失败，状态码：", product_response.status_code,key)
        all_product[key]=product
        # print(all_product)
        with open('python_size_require.json', 'w') as json_file:
            json.dump(all_product, json_file, indent=4)
