import os
import subprocess
from tqdm import tqdm
import sys

# 构建镜像函数
def build_image(package_name, directory, error_log_file):
    os.chdir(directory)
    try:
        output = subprocess.check_output(["docker", "build", "-t", package_name, "./"], stderr=subprocess.STDOUT)
        print('Build successful.')
        print(output.decode())
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while building image for package {package_name}: {e.output.decode()}")
        with open(error_log_file, "a") as f:
            f.write(f"Error occurred while building image for package {package_name}: {e.output.decode()}\n")
        return False
    return True

# 删除镜像函数
def delete_image(image_name):
    os.system(f"docker rmi {image_name}")

# 主函数
def main(start_percentage, end_percentage,folder):
    python_dir = os.getcwd()
    current_dir = os.getcwd()
    dockerfile_dir = os.path.join(current_dir, folder)
    
    sorted_dirs = sorted(os.listdir(dockerfile_dir))
    total_packages = len(sorted_dirs)  # 获取总包数
    
    # 计算出实际需要处理的包的起始和结束索引
    start_index = int(total_packages * (start_percentage / 100))
    end_index = int(total_packages * (end_percentage / 100))
    
    # 为每个批次创建不同的错误日志文件和最后处理的包文件
    error_log_file = os.path.join(python_dir, f"error_log_batch_{start_index}_to_{end_index}_{folder}.txt")
    last_processed_file = os.path.join(python_dir, f"last_processed_batch_{start_index}_to_{end_index}_{folder}.txt")

    # 从上次处理的地方开始
    if os.path.exists(last_processed_file):
        with open(last_processed_file, "r") as f:
            last_processed = f.readline().strip()
            if last_processed in sorted_dirs:
                start_index = sorted_dirs.index(last_processed) + 1

    # 使用计算出的实际范围作为进度条的总数
    for package_dir in tqdm(sorted_dirs[start_index:end_index], total=(end_index - start_index)):
        package_name = os.path.basename(package_dir)
        try:
            is_build = build_image(package_name, os.path.join(dockerfile_dir, package_dir), error_log_file)
            if not is_build:
                continue
            print(f"Image built for package: {package_name}")

            # 删除构建的镜像
            delete_image(package_name)
            print(f"Deleted image: {package_name}")
            
        except Exception as e:
            print(e)
            print(f"Error occurred while processing package {package_name}: {e}")
            with open(error_log_file, "a") as f:
                f.write(f"Error occurred while processing package {package_name}: {e}\n")
        finally:
            # 无论是否发生异常，都更新最后处理的包名
            with open(last_processed_file, "w") as f:
                f.write(package_name)
            sys.stdout.flush()

# 在命令行中接受参数
if __name__ == "__main__":
    print(len(sys.argv))
    if len(sys.argv) == 4:
        start_percentage=0
        end_percentage=100
        start_percentage = float(sys.argv[1])
        end_percentage = float(sys.argv[2])
        folder=(sys.argv[3])
        main(start_percentage, end_percentage,folder)
    else:
        print("Usage: python script_name.py <start_percentage> <end_percentage> <floder>")
        sys.exit(1)
