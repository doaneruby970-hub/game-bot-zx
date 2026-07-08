import cv2
import numpy as np
import pyautogui
import time

SAVE_DEBUG = True

# ✅ 这个就是你要验证的“相对游戏窗口左上角”的ROI (x, y, w, h)
LEVEL_ROI = (20, 657, 27, 27)

def detect_once():
    print("⏳ 3 秒后开始…请把游戏窗口点到最前面（激活）")
    time.sleep(3)

    win = pyautogui.getActiveWindow()
    if not win:
        print("❌ 没拿到当前活动窗口，请确保激活的是游戏窗口。")
        return

    wx, wy = win.left, win.top

    rx, ry, rw, rh = LEVEL_ROI  # ✅ 用 LEVEL_ROI，不要用不存在的 REL_ROI
    screen_roi = (wx + rx, wy + ry, rw, rh)

    shot = pyautogui.screenshot(region=screen_roi)
    raw = cv2.cvtColor(np.array(shot), cv2.COLOR_RGB2BGR)

    if SAVE_DEBUG:
        cv2.imwrite("dbg_raw.png", raw)

    # 二值图仅用于你肉眼确认“里面有没有数字/杂物”
    img = cv2.resize(raw, None, fx=8, fy=8, interpolation=cv2.INTER_LINEAR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    if SAVE_DEBUG:
        cv2.imwrite("dbg_thresh.png", thresh)

    print("✅ 已保存 dbg_raw.png / dbg_thresh.png")
    print(f"📌 当前使用的屏幕ROI: {screen_roi}")
    print(f"📌 当前活动窗口: left={win.left}, top={win.top}, w={win.width}, h={win.height}")

if __name__ == "__main__":
    detect_once()
