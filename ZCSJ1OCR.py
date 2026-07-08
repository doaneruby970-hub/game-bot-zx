import cv2
import numpy as np
import pyautogui
import time
import os

# --- 核心设置 ---
# 如果你的图片都在一个叫 imgs 的文件夹里，可以把这个改成 "imgs"
# 如果就在当前目录，就留空 ""
IMAGE_FOLDER = "imgs"


def get_image_path(filename):
    """处理文件路径，兼容文件夹"""
    if IMAGE_FOLDER:
        return os.path.join(IMAGE_FOLDER, filename)
    return filename


def find_image_ignore_bg(template_path, threshold=200):
    """
    之前的二值化找图逻辑 (核心识别功能)
    """
    # 1. 截屏
    screenshot = pyautogui.screenshot()
    screen_np = np.array(screenshot)
    screen_img = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)

    # 2. 读图
    template = cv2.imread(template_path)
    if template is None:
        print(f"❌ 错误：找不到文件 {template_path}")
        return None

    # 3. 二值化处理
    screen_gray = cv2.cvtColor(screen_img, cv2.COLOR_BGR2GRAY)
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    _, screen_bin = cv2.threshold(screen_gray, threshold, 255, cv2.THRESH_BINARY)
    _, template_bin = cv2.threshold(template_gray, threshold, 255, cv2.THRESH_BINARY)

    # 4. 匹配
    result = cv2.matchTemplate(screen_bin, template_bin, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    if max_val > 0.8:  # 相似度阈值
        h, w = template_bin.shape
        center_x = max_loc[0] + w // 2
        center_y = max_loc[1] + h // 2
        return (center_x, center_y)

    return None


def wait_and_click(image_name, timeout=10, step_name="未知步骤"):
    """
    智能等待点击函数
    :param image_name: 图片文件名
    :param timeout: 最长等待多少秒
    :param step_name: 这一步叫什么(方便看日志)
    :return: 是否成功
    """
    full_path = get_image_path(image_name)
    print(f"⏳ [{step_name}] 正在寻找: {image_name} (最长等待 {timeout} 秒)...")

    start_time = time.time()

    while True:
        # 1. 尝试找图
        coords = find_image_ignore_bg(full_path)

        if coords:
            print(f"✅ [{step_name}] 找到了！点击坐标: {coords}")
            pyautogui.moveTo(coords[0], coords[1], duration=0.2)
            pyautogui.click()
            return True

        # 2. 检查是否超时
        if time.time() - start_time > timeout:
            print(f"❌ [{step_name}] 超时！{timeout} 秒内未找到目标。")
            return False

        # 3. 没找到就休息 0.5 秒再找，防止 CPU 占用过高
        time.sleep(0.5)


# --- ⭐ 这里是你的“任务清单” ---
if __name__ == "__main__":
    print("脚本启动，请在 3 秒内切回游戏...")
    time.sleep(3)

    # === 第一步 ===
    success1 = wait_and_click("step2.png", timeout=30, step_name="第一步：询问蜈蚣")

    if success1:
        # 第一步和第二步之间可能需要等待
        print("等待剧情动画...")
        time.sleep(40)  # 根据实际需求调整时间

        # === 第二步 ===
        success2 = wait_and_click("04.png", timeout=20, step_name="第二步：询问身份")

        if success2:
            # 第二步和第三步之间也可以加个小延迟，确保 UI 刷新
            time.sleep(25)

            # === 第三步：在这里添加你的新步骤 ===
            # 你需要准备一张名为 step3.png 的截图放在 imgs 文件夹里
            success3 = wait_and_click("step3.png", timeout=20, step_name="第三步：确认任务")

            if success3:
                print("🎉 所有步骤均已完成！")
            else:
                print("❌ 第三步失败。")
        else:
            print("❌ 第二步失败。")
    else:
        print("❌ 第一步失败，脚本停止。")