import json
import requests
import random
import time
from tqdm import tqdm

def save_lengths_to_file(stored_lengths, stored_path):
    with open(stored_path, 'w') as json_file:
        json.dump(stored_lengths, json_file)

def get_all_version(vul_keys, stored_lengths, stored_path):
    all_version_count = 0
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
    
    count = 0  # 计数器
    for vul_key in tqdm(vul_keys):
        # 如果已经存储了该 key 的长度，直接使用
        if vul_key in stored_lengths:
            all_version_count += stored_lengths[vul_key]
            continue  # 如果已经存在，跳过请求

        if stored_path.startswith('python'):
            product_url = f"https://pypi.org/pypi/{vul_key}/json"
        else:
            product_url = f"https://registry.npmjs.org/{vul_key}"

        selected_user_agent = random.choice(user_agents)

        headers = {
            'User-Agent': selected_user_agent
        }
        # print(product_url)
        product_response = requests.get(product_url, headers=headers)
        # product_response = requests.get(product_url)
        # print(product_response)
        if product_response.status_code == 200:
            product_data = product_response.json()
            
            if stored_path.startswith('python'):
                version_count = len(product_data.get('releases', []))
            else:
                version_count = len(product_data.get('versions', []))
            # Assuming the structure of npm response
            print(version_count)
            all_version_count += version_count
            stored_lengths[vul_key] = version_count  # 存储每个 key 的长度

            count += 1
            if count >= 50:  # 每50次存储一次
                save_lengths_to_file(stored_lengths, stored_path)  # 使用已声明的变量
                count = 0  # 重置计数器

            time.sleep(random.uniform(0.1, 1))  # 随机延迟以避免被封禁
        else:
            print(f"Failed to retrieve data for {vul_key}: {product_response.status_code}")

    # 在结束时保存剩余的数据
    save_lengths_to_file(stored_lengths, stored_path)  # 在结束时保存
    
    return all_version_count, stored_lengths
# 加载已存储的长度信息
python_stored_lengths = {}
node_stored_lengths = {}
python_stored_path='python_stored_lengths.json'
node_stored_path='node_stored_lengths.json'
try:
    with open(python_stored_path, 'r') as json_file:
        python_stored_lengths = json.load(json_file)
except FileNotFoundError:
    pass

try:
    with open(node_stored_path, 'r') as json_file:
        node_stored_lengths = json.load(json_file)
except FileNotFoundError:
    pass

# 处理 Python 数据
python_package_count = 0
python_release_count = 0
python_release_size_count = 0

with open('python_size_require.json', 'r') as json_file:
    vul_product = json.load(json_file)
    vul_keys = vul_product.keys()
    all_version_count=0#临时跳过，采用下面注释的内容
    # all_version_count, python_stored_lengths = get_all_version(vul_keys, python_stored_lengths, python_stored_path)
    
    for vul_key in vul_keys:
        if vul_product[vul_key]:
            python_package_count+=1
        else:
            continue
        for release in vul_product[vul_key]:
            python_release_count += 1
            if vul_product[vul_key][release]['size']:
                python_release_size_count += vul_product[vul_key][release]['size']

print("Python:", python_package_count, python_release_count, python_release_size_count, all_version_count)

# 处理 Node 数据
node_release_count = 0
node_release_size_count = 0
node_package_count=0
with open('node_size_require.json', 'r') as json_file:
    vul_product = json.load(json_file)
    vul_keys = vul_product.keys()
    
    all_version_count, node_stored_lengths = get_all_version(vul_keys, node_stored_lengths, node_stored_path)
    
    for vul_key in vul_keys:
        if vul_product[vul_key]:
            node_package_count+=1
        else:
            continue
        for release in vul_product[vul_key]:
            node_release_count += 1
            if vul_product[vul_key][release]['size']:
                node_release_size_count += vul_product[vul_key][release]['size']

print("Node:", len(vul_keys), node_release_count, node_release_size_count)

# 最后保存长度信息
save_lengths_to_file(python_stored_lengths, python_stored_path)
save_lengths_to_file(node_stored_lengths, node_stored_path)
