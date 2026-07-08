# shubiaozuobiaobofang.py
import json
import time
import random
from ArduinoKeyboard import ArduinoKeyboard

# ================== 参数区 ==================
PORT = "COM5"

# 锚点（已知起点）
ANCHOR_X = 50
ANCHOR_Y = 50

# 拖拽拆分步数
MIN_STEPS = 18
MAX_STEPS = 28

# 启动缓冲时间（给你切回游戏）
START_DELAY = 3.0
# ============================================

kb = ArduinoKeyboard(PORT)

print("请输入要播放的 json 文件名（不需要 .json）：")
name = input(">>> ").strip()
json_path = f"data/{name}.json"

with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

eye = data["eye"]
face = data["face"]

print(f"\n将在 {START_DELAY} 秒后开始动作，请切回游戏窗口...")
time.sleep(START_DELAY)

# ===== 1. 强制归位到锚点 =====
print("鼠标归位中...")
kb.move_relative(-2000, -2000)  # 先甩到左上
time.sleep(0.1)
kb.move_relative(ANCHOR_X, ANCHOR_Y)
time.sleep(0.2)

# ===== 2. 移动到眼睛 =====
dx_eye = eye["x"] - ANCHOR_X
dy_eye = eye["y"] - ANCHOR_Y
kb.move_relative(dx_eye, dy_eye)
time.sleep(0.15)

# ===== 3. 按下左键 =====
kb.send_cmd("MP:l")
time.sleep(random.uniform(0.08, 0.15))

# ===== 4. 人味拖拽（eye → face）=====
total_dx = face["x"] - eye["x"]
total_dy = face["y"] - eye["y"]

steps = random.randint(MIN_STEPS, MAX_STEPS)

cur_dx = 0
cur_dy = 0

for i in range(steps):
    remain_dx = total_dx - cur_dx
    remain_dy = total_dy - cur_dy

    step_dx = remain_dx / (steps - i)
    step_dy = remain_dy / (steps - i)

    # 手抖
    step_dx += random.uniform(-2, 2)
    step_dy += random.uniform(-2, 2)

    kb.move_relative(int(step_dx), int(step_dy))

    cur_dx += step_dx
    cur_dy += step_dy

    # 后段慢下来
    time.sleep(random.uniform(0.01, 0.025) + i * 0.001)

# ===== 5. 松开 =====
time.sleep(random.uniform(0.05, 0.1))
kb.send_cmd("MR:l")

print("播放完成")
