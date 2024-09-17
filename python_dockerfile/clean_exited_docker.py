import subprocess
import time

def remove_exited_containers():
    try:
        # 删除所有Exited状态的容器
        subprocess.run("docker rm $(docker ps -a -q -f status=exited)", shell=True, check=True)
        print("Removed all exited containers.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    print("Container cleanup script started. Exited containers will be removed every 30 minutes.")
    while True:
        remove_exited_containers()
        # 等待30分钟，每分钟更新一次剩余时间
        for remaining in range(30, 0, -1):
            print(f"Next cleanup in {remaining} minute(s).", end="\r", flush=True)
            time.sleep(60)
        print("\nTime for cleanup!")
