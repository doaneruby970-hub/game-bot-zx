import pyautogui
import pydirectinput
import time
import os
import sys

# 禁用保护
pyautogui.FAILSAFE = False


def auto_press_f_once():
    # ================= 1. 路径与参数处理 =================
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_script_dir)

    target_img_path = ""

    # 判断是【被调用】还是【手动点击运行】
    if len(sys.argv) > 1:
        input_arg = sys.argv[1].strip()
        if os.path.isabs(input_arg):
            # A. 接收来自主程序的全路径（推荐）
            target_img_path = input_arg
        else:
            # B. 接收文件名，默认去诛仙目录下找
            target_img_path = os.path.join(project_root, "ZhuXian", "imgs", "actions", input_arg)
    else:
        # C. 手动运行调试模式（默认找 04.png）
        target_img_path = os.path.join(project_root, "ZhuXian", "imgs", "actions", "04.png")

    print(f">>> [子任务] 启动：正在寻找目标图片并按 F 键")
    print(f"   📂 目标路径: {target_img_path}")

    # ================= 2. 存在性检查 =================
    if not os.path.exists(target_img_path):
        print(f"❌ [子任务] 依然找不到图片！")
        print(f"   检查路径是否正确: {target_img_path}")
        time.sleep(3)
        return

    # ================= 3. 循环找图 =================
    start_t = time.time()
    # 60秒超时防止卡死
    timeout = 60

    print("   👀 正在扫描屏幕...")

    while True:
        if time.time() - start_t > timeout:
            print("   ⌛ 超时未找到，退出。")
            break

        try:
            box = pyautogui.locateOnScreen(
                target_img_path,
                confidence=0.8,
                grayscale=True
            )

            if box:
                print(f"✅ 发现目标！按下 F 键")
                pydirectinput.press('f')
                time.sleep(1.0)
                print("👋 动作完成，脚本退出。")
                break
            else:
                # 降低 CPU 占用
                time.sleep(0.2)

        except Exception as e:
            # 异常处理，防止崩溃
            time.sleep(0.2)


if __name__ == "__main__":
    auto_press_f_once()