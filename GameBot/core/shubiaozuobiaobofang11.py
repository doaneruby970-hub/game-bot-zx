import json
import time
import sys
import os
import pydirectinput  # 👈 核心修改：引入纯软件驱动

# ================== 配置区 ==================
# 禁用防故障保护
pydirectinput.FAILSAFE = False
pydirectinput.PAUSE = 0.01

START_DELAY = 1.0  # 软件模式不需要等太久，1秒够了


def main():
    # ================= 1. 路径与参数处理 =================
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_script_dir)

    json_path = ""

    # 接收参数
    if len(sys.argv) > 1:
        raw_arg = sys.argv[1].strip()

        if os.path.isabs(raw_arg):
            json_path = raw_arg
        else:
            json_name = raw_arg if raw_arg.endswith(".json") else raw_arg + ".json"
            json_path = os.path.join(project_root, "ZhuXian", "imgs", "tools", json_name)
    else:
        # 手动调试默认值
        json_path = os.path.join(project_root, "ZhuXian", "imgs", "tools", "玄火队友.json")

    print(f">>> [指令] 准备执行右键点击: {json_path}")

    # ================= 2. 资源检查与读取 =================
    if not os.path.exists(json_path):
        print(f"❌ 找不到文件！路径无效: {json_path}")
        time.sleep(3)
        return

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            point = data["point"]
    except Exception as e:
        print(f"❌ JSON 格式错误: {e}")
        return

    # ================= 3. 纯软件执行动作 =================
    # 既然是纯软件，不需要初始化硬件，也不需要等待串口复位
    print(f"⏳ 等待 {START_DELAY} 秒...")
    time.sleep(START_DELAY)

    # 1. 直接移动到目标坐标 (绝对移动，不再需要计算相对距离)
    target_x = int(point["x"])
    target_y = int(point["y"])

    print(f"   1. 移动至 ({target_x}, {target_y})")
    pydirectinput.moveTo(target_x, target_y)

    # 稍微停顿，模拟真人瞄准
    time.sleep(0.2)

    # 2. 右键点击
    print("   2. 执行右键")
    # 为了更稳，拆分成按下和松开
    pydirectinput.mouseDown(button='right')
    time.sleep(0.08)  # 按住 80ms
    pydirectinput.mouseUp(button='right')

    print("✅ 动作完成")


if __name__ == "__main__":
    main()