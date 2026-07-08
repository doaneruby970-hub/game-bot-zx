import cv2
import numpy as np
import mss
import time
import os
import sys
import pyautogui
import pydirectinput

# 禁用 pyautogui 的防故障保护
pyautogui.FAILSAFE = False

# ================= 配置区 (720p 专用) =================
# 既然你的环境是 720p，这里直接写死，不要让代码乱猜
BASE_WIDTH = 1280
BASE_HEIGHT = 720

# 720p 下右上角小地图的大致区域 (x, y, w, h)
# 1280分辨率下，小地图通常在 x=900 往后
BASE_MAP_REGION = (900, 0, 380, 300)

# 匹配阈值 (如果还不准，可以微调到 0.6)
MATCH_CONFIDENCE = 0.65


def auto_click_target():
    print("-" * 30)
    print(">>> [智能右键 - 720p专用版] 启动...")

    # ================= 1. 路径与参数处理 =================
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_script_dir)

    target_img_path = ""

    # 判断参数来源
    if len(sys.argv) > 1:
        input_arg = sys.argv[1].strip()
        if os.path.isabs(input_arg):
            # 绝对路径直接用
            target_img_path = input_arg
        else:
            # 文件名则去 actions 找
            target_img_path = os.path.join(project_root, "ZhuXian", "imgs", "actions", input_arg)
    else:
        # 调试模式默认图
        target_img_path = os.path.join(project_root, "ZhuXian", "imgs", "actions", "201fire5.png")

    print(f"   📂 目标图片路径: {target_img_path}")

    # ================= 2. 资源检查 =================
    if not os.path.exists(target_img_path):
        print(f"❌ 错误: 图片文件不存在 -> {target_img_path}")
        # 找不到图就别硬跑了，直接退
        return

    # 读取图片 (保持原样，不要缩放！)
    template = cv2.imread(target_img_path)
    if template is None:
        print("❌ 错误: 图片无法读取，请检查路径或格式")
        return

    th, tw = template.shape[:2]

    # ================= 3. 分辨率检查 =================
    w, h = pyautogui.size()
    print(f"   🖥️ 当前屏幕: {w}x{h}")

    if w != 1280 or h != 720:
        print("⚠️ 警告: 当前分辨率不是 1280x720，可能会导致识别偏移！")

    # ================= 4. 锁定扫描区域 =================
    # 直接使用配置好的区域，不做任何数学缩放
    scan_x, scan_y, scan_w, scan_h = BASE_MAP_REGION

    # 防止区域超出屏幕边界
    if scan_x + scan_w > w: scan_w = w - scan_x
    if scan_y + scan_h > h: scan_h = h - scan_y

    monitor_region = {"top": scan_y, "left": scan_x, "width": scan_w, "height": scan_h}
    print(f"   🔍 扫描区域: {monitor_region}")

    # ================= 5. 循环找图 =================
    start_t = time.time()
    timeout = 30  # 秒

    with mss.mss() as sct:
        while True:
            # 超时检测
            if time.time() - start_t > timeout:
                print("   ⌛ 超时: 未找到目标，跳过。")
                break

            try:
                # 截屏
                img_grab = sct.grab(monitor_region)
                img_np = np.array(img_grab)
                frame = cv2.cvtColor(img_np, cv2.COLOR_BGRA2BGR)

                # 匹配
                res = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, max_loc = cv2.minMaxLoc(res)

                if max_val >= MATCH_CONFIDENCE:
                    local_x, local_y = max_loc

                    # 还原回屏幕绝对坐标
                    center_x = scan_x + local_x + tw // 2
                    center_y = scan_y + local_y + th // 2

                    print(f"   ✅ 发现目标! 匹配度: {max_val:.2f}, 坐标: ({center_x}, {center_y})")

                    # 移动与点击逻辑
                    pydirectinput.moveTo(center_x, center_y)
                    # 稍微停顿一下确保鼠标到位
                    time.sleep(0.5)

                    pydirectinput.rightClick()
                    print("   👋 右键点击完成。")
                    break
                else:
                    # 没找到就稍微休息下，省点CPU
                    time.sleep(0.2)

            except Exception as e:
                print(f"   ⚠️ 运行报错: {e}")
                time.sleep(0.5)


if __name__ == "__main__":
    auto_click_target()