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
    # specific_error_patterns = {
    #     "need_retry": [re.compile(r"ECONNREFUSED")],
    #     "InvalidRequirepackage": [
    #         re.compile(r"stack Error"),
    #         re.compile(r"invalid reference format"),
    #         re.compile(r"InvalidRequirement"),
    #         re.compile(r"FileNotFoundError"),
    #         re.compile(r"package directory (.+) does not exist"),
    #         re.compile(r"AttributeError"),
    #         re.compile(r"No matching version found "),
    #         re.compile(r"NameError"),
    #         re.compile(r"ReferenceError"),
    #         re.compile(r'ERROR: HTTP error 404 while getting'),
    #     ],
    #     "Miss_sys_dependence": [
    #         re.compile(r"Missing CMake executable"),
    #         re.compile(r"No such file or directory: 'cmake'"),
    #         re.compile(r"command '(.+)' failed"),
    #         re.compile(r"CMake must be installed to build from source"),
    #         re.compile(r" error: Command \"gcc"),
    #         re.compile(r"error in (.+) command(.+)"),
    #         re.compile(r"Unable to find LZ4 headers"),
    #         re.compile(r"set SLUGIFY_USES_TEXT_UNIDECODE=yes "),
    #         re.compile(r"RuntimeError: The (.+) command appears not to be installed or"),
    #         re.compile(r"RuntimeError: Running cythonize failed"),
    #         re.compile(r"not available in the build environment"),
    #         re.compile(r"Could not find (.+) executable"),
    #         re.compile(r"subprocess.CalledProcessError: Command"),
    #         re.compile(r"is not installed or is not on PATH"),
    #         re.compile(r"command not found"),
    #         re.compile(r"Error: Unable to compile the binary module"),
    #         re.compile(r"Didn't find rst2man"),
    #         re.compile(r'Did not find CMake'),
    #     ],
    #     "node_versionError": [
    #         re.compile(r"SyntaxError"),
    #         re.compile(r"TypeError"),
    #         re.compile(r"ValueError: invalid mode:"),
    #         re.compile(r"values of (.+) dict\" must be a list of strings"),
    #         re.compile(r"not be supported in future versions."),
    #         re.compile(r"will be disallowed in a future version"),
    #         re.compile(r'unsupported version'),
    #         re.compile(r'does not work on any version of'),
    #     ],
    #     "conflicting dependencies": [re.compile(r"conflicting dependencies")],
    # }


    specific_error_patterns = {
        # 系统导致的问题
        "System_errors": [
                re.compile(r"code EBADPLATFORM"),
                re.compile(r"code ECONNRESET"),
                re.compile(r"code ENOENT"),
                re.compile(r"code ETIMEDOUT"),
                re.compile(r"code E403"),
                re.compile(r"code E404"),
                re.compile(r"ERROR 404: Not Found"),
                re.compile(r"Reached heap limit Allocation failed"),
                re.compile(r"node::OOMErrorHandler"),
                re.compile(r'idealTree'),
                re.compile(r'gyp ERR! stack Error'),
                re.compile(r"code EBADPLATFORM"),
                re.compile(r"code 128")#没有git登录
            ],


        # 版本更新导致的问题
        "Version_update_errors":  [
                re.compile(r"code ETARGET"),
                re.compile(r"code ENOVERSIONS"),
                re.compile(r"code ERESOLVE"),
            ],

        # 包内部代码出错导致的问题
        "Internal_package_errors": [
                re.compile(r"code \d"),
                re.compile(r"code EEXIST"),
            ],
        }



    # 读取错误日志文件
    with open(error_log_file, "r",encoding='utf-8') as f:
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
print((16790-total_errors)/16790)
print((total_errors))
print((16790-total_errors))



