import cv2
import numpy as np
import pyautogui
import pytesseract
import re
import time

pytesseract.pytesseract.tesseract_cmd = r"E:\OCR\tesseract.exe"

# ✅ 绝对屏幕坐标 ROI：(x, y, w, h)
LEVEL_ROI = (793, 151, 26, 21)


def detect_level_once():
    print("⏳ 3 秒后开始截取等级…请切回游戏画面")
    time.sleep(3)

    # 截图
    shot = pyautogui.screenshot(region=LEVEL_ROI)
    raw = cv2.cvtColor(np.array(shot), cv2.COLOR_RGB2BGR)

    # 放大 + OTSU（二值化）
    img = cv2.resize(raw, None, fx=10, fy=10, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX)

    thresh = cv2.threshold(
        gray, 0, 255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )[1]

    # 轻微去噪
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)

    # OCR
    config = r"--oem 3 --psm 10 -c tessedit_char_whitelist=0123456789"
    text = pytesseract.image_to_string(thresh, config=config)
    text = re.sub(r"\D", "", text)

    if not text:
        return 0

    text = text[:2]  # 最多取两位

    if len(text) not in (1, 2):
        return 0

    lv = int(text)
    if not (1 <= lv <= 200):
        return 0

    return lv


if __name__ == "__main__":
    try:
        lv = detect_level_once()
        if lv == 0:
            print("❌ 未识别到等级")
        else:
            print(f"✅ 识别等级: {lv}")
    except Exception as e:
        print(f"❌ 出错：{e}")
