# -*- coding: utf-8 -*-
import subprocess
import time
from utils.get_yaml_value import get_yaml_value

def kill_process(process_name, interval=1):
    """
    循环执行 taskkill 命令以终止指定的进程。

    :param process_name: 要终止的进程名称
    :param interval: 每次执行之间的等待时间（秒）
    """
    while True:
        if get_yaml_value('regulatory_taskkill'):
            try:
                # 执行 taskkill 命令
                subprocess.run(['taskkill', '/F', '/IM', process_name], check=True)
                print(f"已终止进程: {process_name}")
            except subprocess.CalledProcessError:
                print(f"未找到进程: {process_name}，可能已经被终止。")

            # 等待指定的时间
            time.sleep(interval)
if __name__ == '__main__':
    kill_process("SeewoAbility.exe")