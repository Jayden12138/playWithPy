import subprocess

adb_path = 'D:\\platform-tools\\adb.exe'  # 确认ADB工具的路径

# 获取设备列表
def get_device_serial():
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

device_serial = get_device_serial()

# 列出已安装的应用程序包名
result = subprocess.run([adb_path, '-s', device_serial, 'shell', 'pm', 'list', 'packages'], capture_output=True, text=True)
package_names = result.stdout.splitlines()

# 遍历应用程序包名列表并卸载每个应用程序
for package_name in package_names:
    package_name = package_name.replace('package:', '').strip()
    uninstall_result = subprocess.run([adb_path, '-s', device_serial, 'uninstall', package_name], capture_output=True, text=True)
    if uninstall_result.returncode == 0:
        print(f"成功卸载应用程序: {package_name}")
    else:
        print(f"无法卸载应用程序: {package_name}")
