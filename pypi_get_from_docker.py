import docker
import os
#######################
#使用osv_pypi_product.py和osv_cve_build.json从不同版本的python镜像中获取对含有漏洞的产品所支持的不同版本

# 创建 Docker 客户端
client = docker.from_env()

# 定义 Dockerfile 内容
dockerfile_content = """
# 使用官方 Python 3.11.6 镜像作为基础镜像
FROM python:3.11.6

# 安装所需依赖
RUN pip install --no-cache-dir tqdm

# 设置工作目录
WORKDIR /app

# 将当前目录下的 osv_pypi_product.py 文件复制到容器的工作目录
COPY osv_pypi_product.py .

# 将当前目录下的 osv_cve_build 文件复制到容器的工作目录
COPY osv_cve_build.json .

# 运行 Python 脚本
CMD ["python", "osv_pypi_product.py"]

"""

# 将 Dockerfile 内容写入文件
with open('Dockerfile', 'w') as f:
    f.write(dockerfile_content)

# 构建 Docker 镜像
print("开始构建 Docker 镜像...")
image, build_log = client.images.build(path='.', tag='my-python-app', quiet=False)
for line in build_log:
    print(line)
print("Docker 镜像构建完成:", image.tags)

# 运行 Docker 容器，并将当前目录挂载到容器的工作目录
print("开始运行 Docker 容器...")
container = client.containers.run(image=image.tags[0], remove=True, volumes={os.getcwd(): {'bind': '/app', 'mode': 'rw'}})
print("Docker 容器运行完成.")


# 打印容器输出
print(container.decode('utf-8'))


