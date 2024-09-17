import json
import os
import random
# 从 JSON 文件中加载数据
with open("python_3.11.6vul_python_versions.json", "r", encoding="utf-8") as json_file:
    packages_data = json.load(json_file)

# 生成 Dockerfile
def get_random_pypi_source():
    pypi_sources = [
        "https://pypi.org/simple/",
        "https://mirrors.aliyun.com/pypi/simple/",
        "https://pypi.tuna.tsinghua.edu.cn/simple/",
        # Add more PyPI sources as needed
    ]
    return random.choice(pypi_sources)

def generate_dockerfile(package, version):
    pypi_source = get_random_pypi_source()
    dockerfile_content = f"""
    FROM python:3.11.6
    RUN pip install -i {pypi_source} {package}=={version}
    CMD ["bash"]
    """
    return dockerfile_content
    # ENV PIP_INDEX_URL https://pypi.tuna.tsinghua.edu.cn/simple
# 保存 Dockerfile 到文件
def save_dockerfile(folder_name,package, version, dockerfile_content):
    os.makedirs(folder_name, exist_ok=True)
    package_folder = os.path.join(folder_name, f"{package}_{version}")
    os.makedirs(package_folder, exist_ok=True)
    file_path = os.path.join(package_folder, "Dockerfile")
    
    with open(file_path, "w", encoding="utf-8") as dockerfile:
        dockerfile.write(dockerfile_content)
    return file_path

# 主函数
def main():
    folder_names = [f"folder_{i}" for i in range(2, 11)]

    # 创建五个文件夹
    for folder_name in folder_names:
        os.makedirs(folder_name, exist_ok=True)

    # 遍历每个包及其版本信息
    for package, versions in packages_data.items():
        for folder_name in folder_names:
            if versions:
                # 随机选择一个版本
                version = random.choice(versions)

                # 生成 Dockerfile
                dockerfile_content = generate_dockerfile(package, version)

                # 保存 Dockerfile 到文件
                dockerfile_path = save_dockerfile(folder_name, package, version, dockerfile_content)
                print(f"Generated Dockerfile for {package} {version} in {folder_name}: {dockerfile_path}")

if __name__ == "__main__":
    main()