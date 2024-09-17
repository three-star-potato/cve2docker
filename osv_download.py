import requests
import zipfile
import os
from tqdm import tqdm

# 假设这是你需要迭代的列表

list_of_xxx = ['AlmaLinux','Alpine','Android','Bitnami',
'CRAN','crates.io','Debian','GIT','GitHub Actions','Go','Hackage','Hex','Linux',
'Maven','npm','NuGet','OSS-Fuzz','Packagist',
'Pub','PyPI','Rocky Linux','RubyGems','SwiftURL','Ubuntu']

base_directory = "osv"

# 确保基础目录存在
if not os.path.exists(base_directory):
    os.makedirs(base_directory)

# 迭代列表并下载文件
for xxx in tqdm(list_of_xxx):
    url = f'https://osv-vulnerabilities.storage.googleapis.com/{xxx}/all.zip'
    response = requests.get(url, stream=True)

    # 确保请求成功
    if response.status_code == 200:
        # 设置文件名，通常使用URL的最后一部分
        filename = f"{xxx}.zip"
        filepath = os.path.join(base_directory, filename)
        # 创建一个目录名，基于xxx的值
        dirpath = os.path.join(base_directory, xxx)

        # 如果目录不存在，创建目录
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)

        # 打开文件准备写入
        with open(filepath, 'wb') as file:
            # 写入文件
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:  # 过滤掉保持连接的新块
                    file.write(chunk)
        print(f"{filename} 下载完成。")

        # 解压文件
        with zipfile.ZipFile(filepath, 'r') as zip_ref:
            # 解压到创建的对应目录中
            zip_ref.extractall(dirpath)
        print(f"{filename} 解压到 {dirpath} 完成。")

        # 如果你不需要保留zip文件，可以删除它
        os.remove(filepath)
        print(f"{filename} 已删除。")
    else:
        print(f"无法下载文件，URL: {url} 响应了状态码: {response.status_code}")
