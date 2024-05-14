import pdfplumber
import pandas as pd

def extract_data_from_pdf(pdf_path):
    print(f"Extracting data from {pdf_path}")
    with pdfplumber.open(pdf_path) as pdf:
        text = pdf.pages[0].extract_text()
        print(f"Extracted text: {text}")

        lines = text.split('\n')

        # 去除空行
        lines = [line.strip() for line in lines if line.strip()]
        print(f"Processed lines: {lines}")

        # 提取倒数第几个对应的数据
        amount = lines[-1] if len(lines) >= 1 else None
        distance = lines[-7] if len(lines) >= 7 else None
        time = lines[-9] if len(lines) >= 9 else None
        date = lines[-10] if len(lines) >= 10 else None

        print(f"Extracted data - Amount: {amount}, Distance: {distance}, Time: {time}, Date: {date}")

    return amount, distance, time, date
