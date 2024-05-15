import os
import pandas as pd
import requests

# 设置Excel文件路径和APK下载目录
excel_file_path = 'source/1.xlsx'
apk_download_dir = 'path_to_apk_download_directory'
if not os.path.exists(apk_download_dir):
    os.makedirs(apk_download_dir)

# 读取Excel文件
df = pd.read_excel(excel_file_path)


# 下载APK文件
def download_apk(url, download_dir):
    local_filename = os.path.join(download_dir, url.split('/')[-1].split('?')[0])
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        return True
    except requests.exceptions.RequestException as e:
        print(f"下载失败: {e}")
        return False


# 遍历每个APK链接并处理
for index, row in df.iterrows():
    url = row['下载地址']

    # 下载APK
    download_success = download_apk(url, apk_download_dir)
    df.at[index, 'apk下载正常'] = '是' if download_success else '否'

# 保存结果回Excel
result_file_path = 'result.xlsx'
df.to_excel(result_file_path, index=False)
print(f"结果已保存到 {result_file_path}")
