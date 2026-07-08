import json
import time
import random
import sys
import os
import pydirectinput  # 👈 核心修改：直接引入驱动库

# ================== 配置区 ==================
# 禁用防故障保护
pydirectinput.FAILSAFE = False
pydirectinput.PAUSE = 0.01  # 设置微小延迟确保稳定

ANCHOR_X = 50
ANCHOR_Y = 50
MIN_STEPS = 18
MAX_STEPS = 28
START_DELAY = 3.0


def main():
    # ================= 1. 路径与参数处理 =================
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_script_dir)

    json_path = ""

    if len(sys.argv) > 1:
        raw_arg = sys.argv[1].strip()
        if os.path.isabs(raw_arg):
            json_path = raw_arg
        else:
            json_name = raw_arg if raw_arg.endswith(".json") else raw_arg + ".json"
            json_path = os.path.join(project_root, "ZhuXian", "imgs", "tools", json_name)
    else:
        json_path = os.path.join(project_root, "ZhuXian", "imgs", "tools", "default.json")

    print(f">>> [指令] 准备播放动作资源: {json_path}")

    # ================= 2. 文件读取 =================
    if not os.path.exists(json_path):
        print(f"❌ 找不到 JSON 文件: {json_path}")
        time.sleep(3)
        return

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        eye = data["eye"]
        face = data["face"]
    except Exception as e:
        print(f"❌ JSON 数据解析失败: {e}")
        return

    # ================= 3. 准备阶段 (无硬件连接) =================
    print(f"⏳ 等待 {START_DELAY} 秒 (准备鼠标操作)...")
    time.sleep(START_DELAY)

    # ================= 4. 纯软件运动逻辑 =================

    # 1. 鼠标归位 (直接瞬移到锚点，比相对移动更准)
    print("🖱️ 鼠标初始化归位...")
    pydirectinput.moveTo(ANCHOR_X, ANCHOR_Y)
    time.sleep(0.2)

    # 2. 移动到起始点 (Eye)
    # 现在的逻辑是：绝对坐标移动，更稳
    pydirectinput.moveTo(int(eye["x"]), int(eye["y"]))
    time.sleep(0.15)

    # 3. 按下左键 (替代 send_cmd("MP:l"))
    print("👇 按住左键")
    pydirectinput.mouseDown()
    time.sleep(random.uniform(0.08, 0.15))

    # 4. 模拟真人轨迹拖拽
    start_x = eye["x"]
    start_y = eye["y"]
    end_x = face["x"]
    end_y = face["y"]

    total_dx = end_x - start_x
    total_dy = end_y - start_y
    steps = random.randint(MIN_STEPS, MAX_STEPS)

    cur_dx, cur_dy = 0, 0

    print(f"🌊 开始平滑拖拽 (步数: {steps})...")
    for i in range(steps):
        remain_dx = total_dx - cur_dx
        remain_dy = total_dy - cur_dy

        # 计算这一小步走多远
        step_dx = remain_dx / (steps - i) + random.uniform(-2, 2)
        step_dy = remain_dy / (steps - i) + random.uniform(-2, 2)

        # 执行相对移动
        pydirectinput.moveRel(int(step_dx), int(step_dy))

        cur_dx += step_dx
        cur_dy += step_dy

        # 模拟人类的不均匀停顿
        time.sleep(random.uniform(0.01, 0.025) + i * 0.001)

    # 5. 松开左键 (替代 send_cmd("MR:l"))
    time.sleep(random.uniform(0.05, 0.1))
    print("👆 松开左键")
    pydirectinput.mouseUp()

    print("✅ 动作播放完成")


if __name__ == "__main__":
    main()