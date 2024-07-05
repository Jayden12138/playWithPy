import os
import pandas as pd
import json
from datetime import datetime

# 设置文件夹路径
folder_path = './source'  # 修改为你的文件夹路径
json_output = {}

# 初始化id计数器
id_counter = 1

# 遍历文件夹中的所有xlsx文件
for file_name in os.listdir(folder_path):
    if file_name.endswith('.xlsx'):
        # 分割文件名获取所需的信息
        parts = file_name.split('（')
        disease_name = parts[0]
        base_name = parts[1].replace('）.xlsx', '')

        # 读取xlsx文件
        file_path = os.path.join(folder_path, file_name)
        df = pd.read_excel(file_path)

        # 构造data数组，并按照value降序排序
        data_list = df.rename(columns={df.columns[0]: 'countryZh', df.columns[1]: 'value'}).to_dict(orient='records')
        data_list.sort(key=lambda x: x['value'], reverse=True)

        # 构造json结构
        json_output[disease_name] = {
            'base': base_name,
            'id': str(id_counter),
            'data': data_list
        }

        # 递增id计数器
        id_counter += 1

# 生成当前日期时间字符串
current_time = datetime.now().strftime('%Y%m%d%H%M%S')

# 输出json文件
output_file_name = f'output_{current_time}.json'
with open(output_file_name, 'w', encoding='utf-8') as f:
    json.dump(json_output, f, ensure_ascii=False, indent=4)

print(f"JSON 文件已生成：{output_file_name}")
