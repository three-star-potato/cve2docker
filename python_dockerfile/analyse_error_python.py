import re
import random
from collections import defaultdict
import os
import re
import random
from collections import defaultdict

def classify_errors(error_log_file):
    # 定义一个字典来存储错误类型及其对应的包名
    error_types = defaultdict(list)

    # 定义一个正则表达式来匹配包名和错误信息
    error_pattern = re.compile(r"Error occurred while building image for package (.+): DEPRECATED:(.+)", re.DOTALL)

    # 定义一个字典来存储具体的错误类型正则表达式
    specific_error_patterns = {
        "need_retry": [re.compile(r"NewConnectionError")],
        "InvalidRequirepackage": [
            re.compile(r"No matching distribution found"),
            re.compile(r"RuntimeError: (.+) does not support wheel. This error is safe to ignore"),
            re.compile(r"Packages installed from PyPI cannot depend on packages which are not also hosted on PyPI."),
            re.compile(r"PEP 440 version"),
            re.compile(r"invalid reference format"),
            re.compile(r"not appear to be a Python project: neither 'setup.py' nor 'pyproject.toml' found"),
###################################################################################################
            re.compile(r"InvalidRequirement"),
            re.compile(r"FileNotFoundError"),
            re.compile(r"package directory (.+) does not exist"),
            re.compile(r"AttributeError"),
            re.compile(r"ModuleNotFoundError"),
            re.compile(r"NameError"),
            re.compile(r"ImportError"),
            re.compile(r'ERROR: HTTP error 404 while getting'),
            re.compile(r'Cython.Compiler.Errors.CompileError:'),
            ############################################
            re.compile(r"conflicting dependencies")
        ],
        "Miss_sys_dependence": [
            re.compile(r"Missing CMake executable"),
            re.compile(r"No such file or directory: 'cmake'"),
            re.compile(r"command '(.+)' failed"),
            re.compile(r"CMake must be installed to build from source"),
            re.compile(r" error: Command \"gcc"),
            re.compile(r"error in (.+) command(.+)"),
            re.compile(r"Unable to find LZ4 headers"),
            re.compile(r"set SLUGIFY_USES_TEXT_UNIDECODE=yes "),
            re.compile(r"RuntimeError: The (.+) command appears not to be installed or"),
            re.compile(r"RuntimeError: Running cythonize failed"),
            re.compile(r"not available in the build environment"),
            re.compile(r"Could not find (.+) executable"),
            re.compile(r"subprocess.CalledProcessError: Command"),
            re.compile(r"is not installed or is not on PATH"),
            re.compile(r"command not found"),
            re.compile(r"Error: Unable to compile the binary module"),
            re.compile(r"Didn't find rst2man"),
            re.compile(r'Did not find CMake'),
            re.compile(r'requires the 2to3 tool'),
        ],
        "python_versionError": [
            re.compile(r"SyntaxError"),
            re.compile(r"TypeError"),
            re.compile(r"ValueError: invalid mode:"),
            re.compile(r"values of (.+) dict\" must be a list of strings"),
            re.compile(r"RuntimeError: Python version (.+) is required."),
            re.compile(r"not be supported in future versions."),
            re.compile(r"will be disallowed in a future version"),
            re.compile(r"requires a Python (.+) version newer"),
            re.compile(r'mechanize only works on python'),
            re.compile(r'unsupported version'),
            re.compile(r'does not work on any version of'),
            re.compile(r'is deprecated [-Werror=deprecated-declarations]'),
        ],
    }

    # 读取错误日志文件
    with open(error_log_file, "r") as f:
        log_content = f.read()

    # 分割每个包的错误信息
    error_entries = log_content.split("Error occurred while building image for package")
    # 处理每个错误条目
    for entry in error_entries:
        entry = entry.strip()  # 去除前后空白
        if entry:  # 确保条目非空
            match = error_pattern.search("Error occurred while building image for package " + entry)
            if match:
                package_name = match.group(1)
                error_message = match.group(2).strip()

                # 检查具体的错误类型
                classified = False
                for error_type, patterns in specific_error_patterns.items():
                    for pattern in patterns:
                        if pattern.search(error_message):
                            error_types[error_type].append((package_name, error_message))
                            classified = True
                            break
                    if classified:
                        break

                # 如果没有匹配到具体的错误类型，则归类到"UnknownError"
                if not classified:
                    error_types["UnknownError"].append((package_name, error_message))

    # 随机打印一个没有归类的错误信息
    if error_types["UnknownError"]:
        random_error = random.choice(error_types["UnknownError"])
        print("Random Unclassified Error:")
        print(f"  Package: {random_error[0]}")
        print(f"  Error Message: {random_error[1]}")
    else:
        print("No unclassified errors found.")

    # 打印各已归类错误信息的数量
    print("\nError Type Counts:")
    for error_type, details in error_types.items():
        print(f"{error_type}: {len(details)}")

    return error_types

def aggregate_error_types(directory):
    total_error_types = {}
    
    for file_name in os.listdir(directory):
        if file_name.startswith("error_log_batch") and file_name.endswith(".txt"):
            error_log_file = os.path.join(directory, file_name)
            error_types = classify_errors(error_log_file)
            # print(error_types)
            for error_type, details in error_types.items():
                if error_type in total_error_types:
                    total_error_types[error_type] += len(details)
                else:
                    total_error_types[error_type] = len(details)
    
    return total_error_types


directory = "./"
total_error_types = aggregate_error_types(directory)
print(total_error_types)

# 打印错误类型占比
total_errors = sum(total_error_types.values())
print(total_errors)
print((7030-total_errors)/7030)
print((7030-total_errors))


# 生成 Dockerfile
def generate_dockerfile(package, version):
    dockerfile_content = f"""
    FROM python:3.11.6
    RUN pip install {package}=={version}
    CMD ["bash"]
    """
    return dockerfile_content
    # ENV PIP_INDEX_URL https://pypi.tuna.tsinghua.edu.cn/simple
# 保存 Dockerfile 到文件
def save_dockerfile(package, version, dockerfile_content):
    folder_name = "retry"
    os.makedirs(folder_name, exist_ok=True)
    package_folder = os.path.join(folder_name, f"{package}_{version}")
    os.makedirs(package_folder, exist_ok=True)
    file_path = os.path.join(package_folder, "Dockerfile")
    with open(file_path, "w", encoding="utf-8") as dockerfile:
        dockerfile.write(dockerfile_content)
    return file_path
# for item in error_types["need_retry"]:
#                 # 生成 Dockerfile
#     package, version=item[0].split("_")
#     dockerfile_content = generate_dockerfile(package, version)

#             # 保存 Dockerfile 到文件
#     dockerfile_path = save_dockerfile(package, version, dockerfile_content)
#     print(f"Generated Dockerfile for {package} {version}: {dockerfile_path}")
