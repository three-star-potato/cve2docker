import json
import os
import random

# 从 JSON 文件中加载数据
with open("node_v20.13.1vul_node_versions.json", "r", encoding="utf-8") as json_file:
    packages_data = json.load(json_file)
#    RUN npm config set registry https://registry.npmmirror.com \
#         # && 
# 生成 Dockerfile

# 安装 coreutils 包以获取 timeout 命令
# RUN apt-get update && apt-get install -y coreutils
#   RUN timeout 300 npm install
def generate_dockerfile(package, version):
    # List of npm registry mirrors
    npm_mirrors = [
        "https://registry.npmmirror.com ",
        "https://registry.npmjs.org/"
    ]
    
    # Randomly select an npm mirror
    selected_mirror = random.choice(npm_mirrors)
    
    dockerfile_content = f"""
    FROM node:20
    RUN npm config set registry {selected_mirror}\
    && npm set progress=false
    RUN npm install -g --omit=dev {package}@{version}
    CMD ["bash"]
    """
    return dockerfile_content

# 保存 Dockerfile 到文件
def save_dockerfile(folder_name, package, version, dockerfile_content):
    os.makedirs(folder_name, exist_ok=True)
    package = package.replace('/', '_').replace('@', 'at_').lower()

    package_folder = os.path.join(folder_name, f"{package}_{version}")
    print(package_folder)
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
