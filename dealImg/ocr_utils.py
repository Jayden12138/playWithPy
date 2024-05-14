import cv2
import pytesseract

def preprocess_image(image_path):
    # 读取图像
    image = cv2.imread(image_path)

    # 转换为灰度图像
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 自适应阈值二值化
    threshold_img = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 11, 4)

    # 图像平滑处理
    smoothed_img = cv2.medianBlur(threshold_img, 3)

    return smoothed_img

def ocr_image_to_text(image_path):
    # Preprocess the image
    preprocessed_image = preprocess_image(image_path)

    # Perform OCR on the preprocessed image
    text = pytesseract.image_to_string(preprocessed_image, lang='chi_sim+eng')  # 中英文混合识别

    return text
