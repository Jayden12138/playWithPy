import re
from ocr_utils import ocr_image_to_text

def extract_data_from_image(image_path):
    print(f"Performing OCR on {image_path}")
    text = ocr_image_to_text(image_path)
    print(f"Extracted text: {text}")

    # Process the extracted text to find relevant data
    lines = text.split('\n')
    print(f"Processed lines: {lines}")

    amount = None
    distance = None
    time = None
    date = None

    for line in lines:
        if "金额" in line or "Fare" in line:
            amount = re.search(r'¥([\d.]+)', line)
            if amount:
                amount = float(amount.group(1))
        if "里程" in line or "Distance" in line:
            distance = re.search(r'([\d.]+)\s*km', line)
            if distance:
                distance = float(distance.group(1))
        if "时间" in line or "Time" in line:
            time = re.search(r'(\d{2}:\d{2})', line)
            if time:
                time = time.group(1)
        if "日期" in line or "Date" in line:
            date = re.search(r'(\d{4}-\d{2}-\d{2})', line)
            if date:
                date = date.group(1)

    print(f"Extracted data - Amount: {amount}, Distance: {distance}, Time: {time}, Date: {date}")
    return amount, distance, time, date
