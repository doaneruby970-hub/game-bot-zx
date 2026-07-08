import pyautogui
import pydirectinput
import time
import os

# ================= 1. 配置区域 =================
# 定义 OCR 扫描区域 (x, y, width, height)
# 如果是 None，代表全屏
REGION_FULL = None
REGION_TOP_LEFT = (0, 0, 800, 600)  # 示例：只看左上角
REGION_BOTTOM = (0, 700, 1920, 380)  # 示例：只看底部对话框

# ===【核心：任务流水线清单】===
# 按照你想要的顺序，一行行往下写
QUEST_FLOW = [
    {
        "step_name": "第一步：接受任务",
        "target_text": "第一个任务",  # 1. 找这个字
        "ocr_region": REGION_FULL,  # (全屏找)
        "target_image": "imgs/accept.png"  # 2. 点这个图
    },
    {
        "step_name": "第二步：提交任务",
        "target_text": "提交",  # 1. 找这个字
        "ocr_region": REGION_TOP_LEFT,  # (只在左上角找，省资源)
        "target_image": "imgs/submit.png"  # 2. 点这个图
    },
    {
        "step_name": "第三步：关闭弹窗",
        "target_text": "完成",
        "ocr_region": REGION_FULL,
        "target_image": "imgs/close.png"
    }
]


# ================= 2. 工具函数层 =================

def my_ocr_function(region):
    """
    【重要】你需要在这里接入你的 OCR 库
    参数 region: (x, y, w, h) 或者 None
    返回: 识别到的所有文字字符串
    """
    # 截图
    if region:
        screenshot = pyautogui.screenshot(region=region)
    else:
        screenshot = pyautogui.screenshot()

    # --- 这里接入你的 OCR 代码 ---
    # 伪代码示例：
    # text = ZCSJ1OCR.recognize(screenshot)
    # return text

    # 模拟返回（测试用，你正式跑的时候把下面这行删掉）
    # print(f"   [模拟OCR] 正在扫描区域: {region if region else '全屏'}")
    return "第一个任务 提交 完成"  # 假装总能找到


def click_image(img_path):
    """寻找图片并点击"""
    if not os.path.exists(img_path):
        print(f"❌ 图片文件不存在: {img_path}")
        return False

    try:
        # 找图
        box = pyautogui.locateOnScreen(img_path, confidence=0.8, grayscale=True)
        if box:
            x, y = pyautogui.center(box)
            print(f"   ✅ 找到图片，点击 -> ({x}, {y})")
            pydirectinput.moveTo(x, y)
            pydirectinput.click()
            return True
        else:
            return False
    except Exception:
        return False


# ================= 3. 执行引擎 =================

def run_workflow():
    print("=== 游戏自动化流水线启动 ===")

    total_steps = len(QUEST_FLOW)

    for index, step in enumerate(QUEST_FLOW):
        step_name = step["step_name"]
        target_text = step["target_text"]
        ocr_region = step["ocr_region"]
        img_path = step["target_image"]

        print(f"\n👉 [{index + 1}/{total_steps}] 正在执行: {step_name}")
        print(f"   目标文字: [{target_text}] | 目标图片: {img_path}")

        # --- 计时器初始化 ---
        start_time = time.time()
        timeout_seconds = 300  # 5分钟超时

        step_finished = False

        # --- 单步死循环 (直到完成或超时) ---
        while not step_finished:
            # 1. 检查超时
            elapsed = time.time() - start_time
            if elapsed > timeout_seconds:
                print(f"\n❌ [严重错误] 步骤超时！")
                print(f"   在 {timeout_seconds} 秒内未能完成步骤: {step_name}")
                print("   程序终止。")
                return  # 退出整个程序

            # 2. OCR 找文字
            detected_text = my_ocr_function(region=ocr_region)

            if target_text in detected_text:
                print(f"   ✅ 发现文字: [{target_text}] -> 正在寻找图片...")

                # 3. 找图片并点击
                if click_image(img_path):
                    print(f"   🎉 步骤 [{step_name}] 完成！")
                    step_finished = True  # 跳出当前 while，进入下一轮 for
                else:
                    print("   ⚠️ 看到字了，但没找到图，继续寻找...", end="\r")
            else:
                print(f"   ⏳ ({int(elapsed)}s) 未发现文字，继续扫描...", end="\r")

            # 降低 CPU 占用
            time.sleep(1)

        # --- 步骤完成后的冷却 ---
        print("\n   💤 等待 3 秒进入下一步...")
        time.sleep(3)

    print("\n✅✅✅ 所有任务全部执行完毕！")


if __name__ == "__main__":
    run_workflow()