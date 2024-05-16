import os
import shutil
import pandas as pd
import requests
import subprocess
import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import threading
from tkinter import ttk

class App:
    # 在 __init__ 方法中添加一个进度条
    def __init__(self, root):
        self.root = root
        self.root.title("APK Installer and Uninstaller")

        self.adb_path = tk.StringVar()
        self.excel_file_path = tk.StringVar()
        self.apk_download_dir = 'path_to_apk_download_directory'
        self.device_serial = None

        self.create_widgets()

    def create_widgets(self):
        frame = tk.Frame(self.root)
        frame.pack(padx=10, pady=10)

        # ADB路径输入框
        tk.Label(frame, text="ADB路径:").grid(row=0, column=0, sticky="w")
        adb_entry = tk.Entry(frame, textvariable=self.adb_path, width=50)
        adb_entry.grid(row=0, column=1, padx=5, pady=5)

        # 浏览ADB路径按钮
        browse_adb_button = tk.Button(frame, text="浏览", command=self.browse_adb)
        browse_adb_button.grid(row=0, column=2, padx=5, pady=5)

        # Excel文件路径输入框
        tk.Label(frame, text="Excel文件路径:").grid(row=1, column=0, sticky="w")
        excel_entry = tk.Entry(frame, textvariable=self.excel_file_path, width=50)
        excel_entry.grid(row=1, column=1, padx=5, pady=5)

        # 浏览Excel文件按钮
        browse_excel_button = tk.Button(frame, text="浏览", command=self.browse_excel)
        browse_excel_button.grid(row=1, column=2, padx=5, pady=5)

        # 执行按钮
        execute_button = tk.Button(frame, text="执行", command=self.execute)
        execute_button.grid(row=2, column=0, columnspan=3, pady=10)

        # 卸载全部应用按钮
        uninstall_button = tk.Button(frame, text="卸载全部应用", command=self.uninstall_all_apps)
        uninstall_button.grid(row=3, column=0, columnspan=3, pady=10)

        # 打印信息文本框
        self.log_text = scrolledtext.ScrolledText(frame, width=80, height=20)
        self.log_text.grid(row=4, column=0, columnspan=3, pady=10)

        # 进度条
        self.progress = ttk.Progressbar(frame, orient='horizontal', mode='determinate', length=500)
        self.progress.grid(row=5, column=0, columnspan=3, pady=10)

        # 清空按钮
        clear_button = tk.Button(frame, text="清空", command=self.clear_log)
        clear_button.grid(row=6, column=0, columnspan=3, pady=10)

    def download_apk(self, url):
        local_filename = os.path.join(self.apk_download_dir, url.split('/')[-1].split('?')[0])
        try:
            self.log(f"开始下载: {url}")

            def download():
                with requests.get(url, stream=True) as r:
                    r.raise_for_status()
                    total_size = int(r.headers.get('content-length', 0))
                    chunk_size = 8192
                    num_bars = total_size // chunk_size
                    with open(local_filename, 'wb') as f:
                        for i, chunk in enumerate(r.iter_content(chunk_size=chunk_size)):
                            f.write(chunk)
                            self.progress['value'] = (i / num_bars) * 100
                            self.root.update_idletasks()

                self.log(f"下载完成: {local_filename}")
                self.progress['value'] = 0  # Reset progress bar after download
                return local_filename

            download_thread = threading.Thread(target=download)
            download_thread.start()
            download_thread.join()

            return local_filename
        except requests.exceptions.RequestException as e:
            self.log(f"下载失败: {e}")
            return None

    def browse_adb(self):
        path = filedialog.askopenfilename(title="选择ADB工具路径")
        if path:
            self.adb_path.set(path)

    def browse_excel(self):
        path = filedialog.askopenfilename(title="选择Excel文件", filetypes=[("Excel files", "*.xlsx")])
        if path:
            self.excel_file_path.set(path)

    def clear_log(self):
        self.log_text.delete(1.0, tk.END)

    def log(self, message):
        self.log_text.insert(tk.END, message + '\n')
        self.log_text.see(tk.END)
        self.root.update()

    def get_device_serial(self, adb_path):
        try:
            result = subprocess.run([adb_path, 'devices'], capture_output=True, text=True)
            lines = result.stdout.splitlines()
            devices = [line.split()[0] for line in lines if '\tdevice' in line]
            if len(devices) == 0:
                raise RuntimeError("没有找到任何设备")
            return devices[0]
        except subprocess.SubprocessError as e:
            self.log(f"获取设备列表异常: {e}")
            return None

    def execute(self):
        adb_path = self.adb_path.get()
        excel_file_path = self.excel_file_path.get()

        if not os.path.exists(adb_path):
            messagebox.showerror("错误", "无效的ADB路径")
            return

        if not os.path.exists(excel_file_path):
            messagebox.showerror("错误", "无效的Excel文件路径")
            return

        # 初始化下载目录
        if not os.path.exists(self.apk_download_dir):
            os.makedirs(self.apk_download_dir)

        # 清空下载目录
        self.clear_directory(self.apk_download_dir)

        # 读取Excel文件
        df = pd.read_excel(excel_file_path)
        df['apk下载正常'] = df.get('apk下载正常', '').astype(str)
        df['安装正常'] = df.get('安装正常', '').astype(str)
        df['APP联网'] = df.get('APP联网', '').astype(str)
        df['不需要登录'] = df.get('不需要登录', '').astype(str)

        self.device_serial = self.get_device_serial(adb_path)
        if not self.device_serial:
            return

        # 遍历每个APK链接并处理
        for index, row in df.iterrows():
            url = row['下载地址']
            try:
                apk_path = self.download_apk(url)
                if apk_path:
                    df.at[index, 'apk下载正常'] = '是'
                else:
                    df.at[index, 'apk下载正常'] = '否'
                    df.at[index, '安装正常'] = '否'
                    df.at[index, 'APP联网'] = '否'
                    df.at[index, '不需要登录'] = '否'
                    continue

                install_success = self.install_apk(adb_path, apk_path)
                df.at[index, '安装正常'] = '是' if install_success else '否'

                if install_success:
                    app_package_name = row['包名']
                    network_success = self.check_app_network(adb_path, app_package_name)
                    df.at[index, 'APP联网'] = '是' if network_success else '否'
                    df.at[index, '不需要登录'] = '暂未判断'
                else:
                    df.at[index, 'APP联网'] = '否'
                    df.at[index, '不需要登录'] = '否'
            except Exception as e:
                self.log(f"处理URL {url} 时出错: {e}")
                continue

        # 保存结果回Excel
        result_file_path = 'result.xlsx'
        if os.path.exists(result_file_path):
            existing_df = pd.read_excel(result_file_path)
            empty_rows = pd.DataFrame([[""] * len(existing_df.columns)] * 3, columns=existing_df.columns)
            combined_df = pd.concat([existing_df, empty_rows, df], ignore_index=True)
            combined_df.to_excel(result_file_path, index=False)
        else:
            df.to_excel(result_file_path, index=False)

        self.clear_directory(self.apk_download_dir)
        self.log("任务完成")

    def download_apk(self, url):
        if not url.startswith('http'):
            self.log(f"无效的URL: {url}")
            return None
        local_filename = os.path.join(self.apk_download_dir, url.split('/')[-1].split('?')[0])
        try:
            self.log(f"开始下载: {url}")
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(local_filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            self.log(f"下载完成: {local_filename}")
            return local_filename
        except requests.exceptions.RequestException as e:
            self.log(f"下载失败: {e}")
            return None

    def install_apk(self, adb_path, apk_path):
        try:
            self.log(f"开始安装: {apk_path}")
            result = subprocess.run([adb_path, '-s', self.device_serial, 'install', apk_path], capture_output=True,
                                    text=True)
            if 'Success' in result.stdout:
                self.log("安装成功")
                return True
            else:
                self.log(f"安装失败: {result.stdout} {result.stderr}")
                return False
        except subprocess.SubprocessError as e:
            self.log(f"安装异常: {e}")
            return False

    def check_app_network(self, adb_path, app_package_name):
        try:
            self.log("检查APP联网状态")
            result = subprocess.run(
                [adb_path, '-s', self.device_serial, 'shell', 'dumpsys', 'package', app_package_name],
                capture_output=True, text=True)
            if 'versionCode' in result.stdout:
                self.log("联网状态正常")
                return True
            else:
                self.log(f"联网检查失败: {result.stdout} {result.stderr}")
                return False
        except subprocess.SubprocessError as e:
            self.log(f"联网检查异常: {e}")
            return False

    def uninstall_all_apps(self):
        adb_path = self.adb_path.get()
        if not os.path.exists(adb_path):
            messagebox.showerror("错误", "无效的ADB路径")
            return

        self.device_serial = self.get_device_serial(adb_path)
        if not self.device_serial:
            return

        try:
            self.log("获取已安装应用程序包名")
            result = subprocess.run([adb_path, '-s', self.device_serial, 'shell', 'pm', 'list', 'packages'],
                                    capture_output=True, text=True)
            package_names = result.stdout.splitlines()

            for package_name in package_names:
                package_name = package_name.replace('package:', '').strip()
                uninstall_result = subprocess.run([adb_path, '-s', self.device_serial, 'uninstall', package_name],
                                                  capture_output=True, text=True)
                if uninstall_result.returncode == 0:
                    self.log(f"成功卸载应用程序: {package_name}")
                else:
                    self.log(f"无法卸载应用程序: {package_name}")
            self.log("卸载全部应用执行完毕")
        except subprocess.SubprocessError as e:
            self.log(f"卸载应用程序异常: {e}")

    def clear_directory(self, directory):
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                self.log(f"删除文件 {file_path} 时出错: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
