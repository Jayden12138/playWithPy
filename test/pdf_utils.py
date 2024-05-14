import pdfplumber
import pandas as pd

def extract_tables_from_pdf(pdf_path):
    all_data = []
    total_amount = 0

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            # 提取“共x笔行程，合计xxx元”的信息
            for line in text.split('\n'):
                if '合计' in line:
                    total_amount += float(line.split('合计')[-1].replace('元', '').strip())
                    break

            table = page.extract_table()

            # 打印提取的表格以便调试
            print("Extracted table from page:", table)

            if table:
                headers = table[0]  # 表头
                data = table[1:]  # 数据
                df = pd.DataFrame(data, columns=headers)
                all_data.append(df)

    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
    else:
        combined_df = pd.DataFrame()

    return combined_df, total_amount