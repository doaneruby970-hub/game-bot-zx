import pyautogui
import pydirectinput
import time
import os
import sys

# 禁用 pyautogui 的自动防故障，防止游戏里误触
pyautogui.FAILSAFE = False


def auto_click_target():
    # ================= 1. 接收与解析参数 (核心修改) =================
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_script_dir)

    target_img_path = ""
    click_action = "LEFT"  # 默认动作

    if len(sys.argv) > 1:
        raw_arg = sys.argv[1].strip()

        # 🟢 A. 识别指令标记 (/A 代表右键)
        if '/' in raw_arg:
            parts = raw_arg.split('/')
            raw_path_part = parts[0].strip()
            if len(parts) > 1 and parts[1].strip().upper() == 'A':
                click_action = "RIGHT"
                print(f">>> [指令识别] 模式: 右键点击 (检测到 /A)")
        else:
            raw_path_part = raw_arg
            print(f">>> [指令识别] 模式: 左键点击 (默认)")

        # 🟢 B. 智能路径解析
        if os.path.isabs(raw_path_part):
            # 如果是绝对路径（主程序传过来的），直接使用
            target_img_path = raw_path_part
        else:
            # 如果只是文件名，默认去诛仙目录下找（手动调试用）
            target_img_path = os.path.join(project_root, "ZhuXian", "imgs", "actions", raw_path_part)
    else:
        # 手动运行调试默认值
        target_img_path = os.path.join(project_root, "ZhuXian", "imgs", "actions", "300A.png")
        print(f">>> [警告] 未接收到参数，进入调试模式")

    # ================= 2. 存在性检查 =================
    print(f">>> [子任务] 启动：寻找图片任务")
    print(f"   📂 目标路径: {target_img_path}")

    if not os.path.exists(target_img_path):
        print(f"❌ [子任务] 图片不存在！请检查路径是否正确。")
        time.sleep(3)
        return

    # ================= 3. 循环找图并执行动作 =================
    start_t = time.time()
    timeout = 30  # 设置超时时间

    while True:
        if time.time() - start_t > timeout:
            print("   ⌛ 超时未找到图片，跳过此步骤。")
            break

        try:
            box = pyautogui.locateOnScreen(
                target_img_path,
                confidence=0.7,
                grayscale=True
            )

            if box is not None:
                center_x = int(box.left + box.width / 2)
                center_y = int(box.top + box.height / 2)

                print(f"✅ 发现目标: ({center_x}, {center_y})")
                pydirectinput.moveTo(center_x, center_y)
                time.sleep(0.1)

                if click_action == "RIGHT":
                    print("   🖱️ 执行动作: [右键点击]")
                    pydirectinput.rightClick()
                else:
                    print("   🖱️ 执行动作: [左键点击]")
                    pydirectinput.click()

                time.sleep(1.0)
                print("👋 操作完成。")
                break
            else:
                time.sleep(0.2)

        except Exception as e:
            time.sleep(0.2)


if __name__ == "__main__":
    auto_click_target()