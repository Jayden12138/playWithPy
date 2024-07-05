
## 处理jky 模拟疾病数据

读取source文件夹下的所有.xlsx文件

整理数据成json

json格式为

```

{
    '文件名1': {
        base: '文件名2',
        data: [
            {
                countryZh: '',
                value: ''
            }
        ]
    }
}

```
