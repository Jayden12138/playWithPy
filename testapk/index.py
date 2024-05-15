import os
import shutil
import pandas as pd
import requests
import subprocess
import tkinter as tk
from tkinter import simpledialog

# 设置Excel文件路径和APK下载目录
excel_file_path = 'source/1.xlsx'
apk_download_dir = 'path_to_apk_download_directory'

# 尝试从环境变量中获取ADB路径
adb_path = os.getenv('ADB_PATH', 'D:\\work\\platform-tools\\adb.exe')  # 默认路径


def prompt_adb_path():
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    adb_path = simpledialog.askstring("ADB路径", "请输入ADB工具的路径:")
    if adb_path:
        os.environ['ADB_PATH'] = adb_path
        return adb_path
    else:
        print("未指定ADB路径，退出程序")
        exit(0)

# 检查ADB路径是否有效
if not os.path.exists(adb_path) or not os.path.isfile(adb_path):
    adb_path = prompt_adb_path()

# 检查下载目录是否存在，如果不存在则创建
if not os.path.exists(apk_download_dir):
    os.makedirs(apk_download_dir)

# 在执行脚本前检查目标文件夹是否为空，如果不为空，则清空文件夹
if os.path.exists(apk_download_dir):
    print(f"清空目录: {apk_download_dir}")
    for file in os.listdir(apk_download_dir):
        file_path = os.path.join(apk_download_dir, file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"删除文件 {file_path} 时出错: {e}")

# 读取Excel文件
df = pd.read_excel(excel_file_path)

# 显式地将相关列转换为字符串类型
df['apk下载正常'] = df.get('apk下载正常', '').astype(str)
df['安装正常'] = df.get('安装正常', '').astype(str)
df['APP联网'] = df.get('APP联网', '').astype(str)
df['不需要登录'] = df.get('不需要登录', '').astype(str)

# 获取设备列表
def get_device_serial(adb_path):
    try:
        result = subprocess.run([adb_path, 'devices'], capture_output=True, text=True)
        lines = result.stdout.splitlines()
        devices = [line.split()[0] for line in lines if '\tdevice' in line]
        if len(devices) == 0:
            raise RuntimeError("没有找到任何设备")
        else:
            # 如果有多个设备，默认选择第一个设备
            return devices[0]
    except subprocess.SubprocessError as e:
        print(f"获取设备列表异常: {e}")
        exit(1)

device_serial = get_device_serial(adb_path)

# 下载APK文件
def download_apk(url, download_dir):
    if not url.startswith('http'):
        print(f"无效的URL: {url}")
        return None
    local_filename = os.path.join(download_dir, url.split('/')[-1].split('?')[0])
    try:
        print(f"开始下载: {url}")
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"下载完成: {local_filename}")
        return local_filename
    except requests.exceptions.RequestException as e:
        print(f"下载失败: {e}")
        return None

# 安装APK文件
def install_apk(adb_path, apk_path):
    try:
        print(f"开始安装: {apk_path}")
        result = subprocess.run([adb_path, '-s', device_serial, 'install', apk_path], capture_output=True, text=True)
        if 'Success' in result.stdout:
            print("安装成功")
            return True
        else:
            print(f"安装失败: {result.stdout} {result.stderr}")
            return False
    except subprocess.SubprocessError as e:
        print(f"安装异常: {e}")
        return False

# 检查APP联网状态
def check_app_network(adb_path, app_package_name):
    try:
        print("检查APP联网状态")
        result = subprocess.run([adb_path, '-s', device_serial, 'shell', 'dumpsys', 'package', app_package_name],
                                capture_output=True, text=True)
        if 'versionCode' in result.stdout:
            print("联网状态正常")
            return True
        else:
            print(f"联网检查失败: {result.stdout} {result.stderr}")
            return False
    except subprocess.SubprocessError as e:
        print(f"联网检查异常: {e}")
        return False

# 遍历每个APK链接并处理
for index, row in df.iterrows():
    url = row['下载地址']

    try:
        # 下载APK
        apk_path = download_apk(url, apk_download_dir)
        if apk_path:
            df.at[index, 'apk下载正常'] = '是'
        else:
            df.at[index, 'apk下载正常'] = '否'
            df.at[index, '安装正常'] = '否'
            df.at[index, 'APP联网'] = '否'
            df.at[index, '不需要登录'] = '否'
            continue

        # 安装APK
        install_success = install_apk(adb_path, apk_path)
        df.at[index, '安装正常'] = '是' if install_success else '否'

        if install_success:
            # 这里假设包名可以从Excel表格中获取
            app_package_name = row['包名']

            # 检查APP联网状态
            network_success = check_app_network(adb_path, app_package_name)
            df.at[index, 'APP联网'] = '是' if network_success else '否'

            # 检查“不需要登录”状态（这里假设无法自动判断）
            df.at[index, '不需要登录'] = '无法判断'
        else:
            df.at[index, 'APP联网'] = '否'
            df.at[index, '不需要登录'] = '否'

    except Exception as e:
        print(f"处理URL {url} 时出错: {e}")
        continue

# 保存结果回Excel
result_file_path = 'result.xlsx'

# 如果结果文件存在，先读取已有数据
existing_df = None
if os.path.exists(result_file_path):
    existing_df = pd.read_excel(result_file_path)

# 如果已有数据不为空，将新数据与已有数据合并
if existing_df is not None:
    # 添加空行
    empty_rows = pd.DataFrame([[""] * len(existing_df.columns)] * 3, columns=existing_df.columns)
    combined_df = pd.concat([existing_df, empty_rows, df], ignore_index=True)
    combined_df.to_excel(result_file_path, index=False)
else:
    df.to_excel(result_file_path, index=False)
