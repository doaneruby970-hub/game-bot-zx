import pyautogui
import pydirectinput
import time
import os
import sys

# 禁用保护，防止鼠标甩到角落报错
pyautogui.FAILSAFE = False


def auto_press_f_loop():
    # ================= 1. 路径与参数处理 =================
    # 获取当前脚本所在 core 目录
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    # 获取项目根目录 GameBot
    project_root = os.path.dirname(current_script_dir)

    target_img_path = ""

    # 判断是【被调用】还是【手动点击运行】
    if len(sys.argv) > 1:
        # A. 如果主程序传了参数
        input_arg = sys.argv[1].strip()

        if os.path.isabs(input_arg):
            # 如果传过来的是绝对路径（推荐方式），直接用
            target_img_path = input_arg
        else:
            # 如果传的是文件名，默认去诛仙目录下找（兼容旧逻辑）
            target_img_path = os.path.join(project_root, "ZhuXian", "imgs", "actions", input_arg)
    else:
        # B. 如果你是手动点这个脚本运行（调试用）
        # 这里手动指定一个你想测试的图片路径
        target_img_path = os.path.join(project_root, "ZhuXian", "imgs", "actions", "201Ice4.png")

    print(f">>> [子任务] 启动循环模式：看到目标就点 F (间隔3秒)")
    print(f"   📂 监控路径: {target_img_path}")

    # ================= 2. 存在性检查 =================
    if not os.path.exists(target_img_path):
        print(f"❌ [子任务] 找不到图片！")
        print(f"   请确认路径是否正确: {target_img_path}")
        # 停顿3秒让你看清错误再退出
        time.sleep(3)
        return

    # ================= 3. 无限循环找图点击 =================
    print("   👀 开始持续监控...")

    while True:
        try:
            # 找图 (相似度 0.7 适应背景变化)
            box = pyautogui.locateOnScreen(
                target_img_path,
                confidence=0.7,
                grayscale=True
            )

            if box:
                print(f"✅ [{time.strftime('%H:%M:%S')}] 发现目标 -> 按 F 键")

                # 执行按键
                pydirectinput.keyDown('f')
                time.sleep(0.1)  # 短暂按住
                pydirectinput.keyUp('f')

                # 点击后等待 3 秒
                print("   ⏳ 等待 3 秒...")
                time.sleep(3.0)
            else:
                # 没找到图，快速休眠继续找
                time.sleep(0.2)

        except Exception as e:
            # 发生异常（如截图权限问题）不退出，打印并重试
            print(f"⚠️ 监控中发生异常: {e}")
            time.sleep(0.5)


if __name__ == "__main__":
    auto_press_f_loop()