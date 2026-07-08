import pydirectinput
import time

# 建议：管理员身份运行
pydirectinput.FAILSAFE = False
pydirectinput.PAUSE = 0.05  # 给系统一点反应时间，别太急

def click_m():
    # 保险起见，先抬起修饰键，防止幽灵 Alt / Ctrl
    for k in ['alt', 'ctrl', 'shift']:
        pydirectinput.keyUp(k)

    print("⌛ 等待 3 秒，请切到目标窗口...")
    time.sleep(3)

    print("👉 点击 M 键")
    pydirectinput.keyDown('m')
    time.sleep(0.08)  # 模拟真人按住 80ms
    pydirectinput.keyUp('m')

    print("✅ 完成")

if __name__ == "__main__":
    click_m()
