import pydirectinput
import time

# =================配置=================
# 必须以管理员身份运行 PyCharm！
pydirectinput.PAUSE = 0.05


def quick_press(key_name):
    """
    最简单的单键点击代码
    """
    # 1. 强制重置修饰键，防止出现 M + Alt 的幽灵情况
    for mod in ['alt', 'ctrl', 'shift']:
        pydirectinput.keyUp(mod)

    # 2. 执行按键动作
    print(f"🚀 正在点击: {key_name}")
    pydirectinput.keyDown(key_name)
    time.sleep(0.1)  # 模拟人类按下 100 毫秒，确保游戏引擎能捕捉到
    pydirectinput.keyUp(key_name)


# =================测试执行=================
if __name__ == "__main__":
    print("等待 3 秒让你把窗口切到游戏...")
    time.sleep(3)

    # 示例 1: 点击 M 键
    quick_press('m')

    time.sleep(1)

    # 示例 2: 点击 左 Ctrl 键
    # pydirectinput 中左 Ctrl 的键名是 'ctrlleft'
    quick_press('ctrlleft')

    print("✅ 执行完毕")