import cv2


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
