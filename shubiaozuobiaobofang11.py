# shubiao_youjian_bofang.py
import json
import time
from ArduinoKeyboard import ArduinoKeyboard

# ================== 参数区 ==================
PORT = "COM5"

# 锚点（已知起点）
ANCHOR_X = 50
ANCHOR_Y = 50

# 启动缓冲时间（给你切回窗口）
START_DELAY = 3.0
# ===========================================

kb = ArduinoKeyboard(PORT)

print("请输入要播放的 json 文件名（不需要 .json）：")
name = input(">>> ").strip()
json_path = f"data/{name}.json"

with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# 只需要一个点
point = data["point"]

print(f"\n将在 {START_DELAY} 秒后执行右键点击，请切回目标窗口...")
time.sleep(START_DELAY)

# ===== 1. 强制归位到锚点 =====
print("鼠标归位中...")
kb.move_relative(-2000, -2000)  # 甩到左上角
time.sleep(0.1)
kb.move_relative(ANCHOR_X, ANCHOR_Y)
time.sleep(0.2)

# ===== 2. 移动到目标点 =====
dx = point["x"] - ANCHOR_X
dy = point["y"] - ANCHOR_Y
kb.move_relative(dx, dy)
time.sleep(0.12)

# ===== 3. 右键点击一次 =====
kb.send_cmd("MP:r")
time.sleep(0.06)
kb.send_cmd("MR:r")

print("右键点击完成")
