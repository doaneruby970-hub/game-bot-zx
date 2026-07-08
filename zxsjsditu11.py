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

# ================= 配置区 (基于 1080p 设计) =================
# 这是一个"基准"区域，代码会自动根据当前分辨率缩放它
# 1080p 下的右上角地图区域 (x, y, w, h)
BASE_MAP_REGION = (1400, 0, 520, 400)
BASE_WIDTH = 1920
BASE_HEIGHT = 1080


def auto_click_target():
    print("-" * 30)
    print(">>> [智能点击] 启动...")

    # ================= 1. 接收参数 =================
    target_name = "201fire211.png"  # 默认值
    if len(sys.argv) > 1:
        target_name = sys.argv[1].strip()

    # ================= 2. 路径与图片加载 =================
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_script_dir)
    target_img_path = os.path.join(project_root, "imgs", "actions", target_name)

    print(f"   📂 目标图片: {target_name}")

    if not os.path.exists(target_img_path):
        print(f"❌ 错误: 图片文件不存在 -> {target_img_path}")
        return

    # 读取原始图片 (假设是 1080p 下截取的)
    template_original = cv2.imread(target_img_path)
    if template_original is None:
        print("❌ 错误: 图片无法读取 (可能是格式损坏或路径含中文)")
        return

    # ================= 3. 获取屏幕分辨率 & 计算缩放比 =================
    w, h = pyautogui.size()
    scale_x = w / BASE_WIDTH
    scale_y = h / BASE_HEIGHT
    scale_ratio = min(scale_x, scale_y)  # 保持长宽比

    print(f"   🖥️ 检测屏幕: {w}x{h} (缩放系数: {scale_ratio:.2f})")

    # ================= 4. 关键：缩放资源 =================

    # [A] 缩放扫描区域 (防止 720p 下坐标越界崩溃)
    bx, by, bw, bh = BASE_MAP_REGION
    scan_x = int(bx * scale_x)
    scan_y = int(by * scale_y)
    scan_w = int(bw * scale_x)
    scan_h = int(bh * scale_y)

    # 修正：确保区域不超出屏幕边界
    if scan_x + scan_w > w: scan_w = w - scan_x

    monitor_region = {"top": scan_y, "left": scan_x, "width": scan_w, "height": scan_h}
    print(f"   🔍 实际扫描区域: {monitor_region}")

    # [B] 缩放目标图片 (防止 720p 下尺寸不匹配找不到)
    # 如果当前分辨率不是 1080p，就缩放图片
    if scale_ratio != 1.0:
        template = cv2.resize(template_original, None, fx=scale_ratio, fy=scale_ratio, interpolation=cv2.INTER_AREA)
        print("   📉 已自动调整图片尺寸以适配屏幕")
    else:
        template = template_original

    th, tw = template.shape[:2]  # 获取图片高宽

    # ================= 5. 循环找图 (OpenCV + MSS) =================
    start_t = time.time()
    timeout = 30

    # 初始化截图对象
    with mss.mss() as sct:
        while True:
            # 超时检测
            if time.time() - start_t > timeout:
                print("   ⌛ 超时: 未找到目标。")
                break

            try:
                # 1. 截取指定区域 (比全屏截图快很多)
                img_grab = sct.grab(monitor_region)
                img_np = np.array(img_grab)
                # mss 截出来是 BGRA，转成 BGR
                frame = cv2.cvtColor(img_np, cv2.COLOR_BGRA2BGR)

                # 2. 匹配
                res = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

                # 3. 判断是否找到 (阈值 0.7)
                if max_val >= 0.7:
                    # max_loc 是相对于截图区域左上角的坐标
                    local_x, local_y = max_loc

                    # 4. 转换为屏幕绝对坐标
                    # 绝对X = 区域左边 + 相对X + 图片一半宽
                    center_x = scan_x + local_x + tw // 2
                    center_y = scan_y + local_y + th // 2

                    print(f"   ✅ 找到目标! 相似度: {max_val:.2f} | 坐标: ({center_x}, {center_y})")

                    # 5. 执行点击
                    pydirectinput.moveTo(center_x, center_y)
                    time.sleep(0.1)
                    pydirectinput.click()
                    time.sleep(0.5)

                    print("   👋 点击完成。")
                    break
                else:
                    # 没找到，稍微休眠一下防止CPU占用过高
                    time.sleep(0.1)

            except Exception as e:
                print(f"   ⚠️ 运行报错: {e}")
                time.sleep(0.5)


if __name__ == "__main__":
    auto_click_target()