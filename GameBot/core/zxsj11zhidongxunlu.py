import cv2
import numpy as np
import mss
import time
import pydirectinput  # 修改：引入虚拟键盘库
import keyboard
import atexit
import math
import os
import sys

# ✅ 强制设置：管理员权限下运行更稳
pydirectinput.FAILSAFE = False
pydirectinput.PAUSE = 0.01


# ==========================================
# 1. 虚拟键盘类 (替代原 Arduino 类)
# ==========================================
class ArduinoKeyboard:
    def __init__(self, port='COM5'):
        # 兼容性：保留 port 参数但不使用，避免报错
        print("✅ 虚拟键盘模式已启动 (已跳过 COM5 连接)")
        print("⚠️ 请确保以管理员身份运行 PyCharm！")

        # 注册退出时的清理函数
        atexit.register(self.release_all)

        # 统一键名映射
        self.KEY_MAP = {
            'w': 'w',
            'a': 'a',
            's': 's',
            'd': 'd',
            'pageup': 'pageup',
            'pagedown': 'pagedown'
        }

    def hold(self, key):
        target_key = self.KEY_MAP.get(key, key)
        pydirectinput.keyDown(target_key)

    def release(self, key):
        target_key = self.KEY_MAP.get(key, key)
        pydirectinput.keyUp(target_key)

    def release_all(self):
        # 释放所有可能卡住的按键
        for k in ['w', 'a', 's', 'd', 'q', 'pageup', 'pagedown']:
            pydirectinput.keyUp(k)
        print("🛑 虚拟按键强制全停")

    def move_relative(self, dx):
        # 限制单次移动幅度，防止视角乱飞
        # 如果觉得视角转太快，把 100 改小点
        dx = max(-200, min(200, dx))
        if dx != 0:
            # 虚拟鼠标相对移动
            pydirectinput.moveRel(int(dx), 0, relative=True)


# ==========================================
# 2. 参数区（根据虚拟环境微调）
# ==========================================
SCREEN_W = 1280
SCREEN_H = 720
THRESHOLD = 0.60
TEXT_THRESHOLD = 0.70
W_INTERVAL = 0.12
STOP_RADIUS = 55
DEAD_ZONE = 28
FAN_BASE_WIDTH = 20
FAN_SPREAD_FACTOR = 0.57
FAN_DRAW_LENGTH = 520
PLAYER_Y_RATIO = 0.56
PLAYER_CIRCLE_R = 42

# 虚拟鼠标响应很快，稍微降低增益防止晃动
TURN_GAIN_IN = 0.22  # 原 0.22
TURN_INTERVAL_IN = 0.12
TURN_GAIN_OUT = 0.85  # 原 0.85
TURN_INTERVAL_OUT = 0.25


# ==========================================
# 3. 智能路径与参数解析（已修复逻辑错误）
# ==========================================
def parse_arguments_and_paths():
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_script_dir)  # 获取 core 的上一级 (GameBot)

    target_name = "target_template.png"
    time_limit = None

    # 解析命令行参数
    if len(sys.argv) > 1:
        raw_arg = sys.argv[1].strip()
        # 处理参数格式: XXX.png/30
        if '/' in raw_arg:
            parts = raw_arg.split('/')
            target_name = parts[0].strip()
            for p in parts[1:]:
                try:
                    time_limit = float(p)
                    print(f"⏱️ 设定限时: {time_limit} 秒")
                except:
                    pass
        else:
            target_name = raw_arg

    # 寻找图片路径
    template_path = ""

    # 情况A：绝对路径
    if os.path.isabs(target_name) and os.path.exists(target_name):
        template_path = target_name
    else:
        # 情况B：相对路径查找
        possible_paths = [
            os.path.join(project_root, "ZhuXian", "imgs", "actions", target_name),
            os.path.join(project_root, "ZhuXian", "imgs", target_name),
            target_name  # 当前目录下查找
        ]

        for p in possible_paths:
            if os.path.exists(p):
                template_path = p
                break

    # 终点图片路径 (默认在 actions 文件夹)
    finish_path = os.path.join(project_root, "ZhuXian", "imgs", "actions", "finish.png")

    return template_path, finish_path, time_limit


# ==========================================
# 4. 主逻辑（已修复变量引用）
# ==========================================
def main():
    # 初始化虚拟键盘
    arduino = ArduinoKeyboard()

    # 获取路径参数
    template_path, finish_path, time_limit = parse_arguments_and_paths()

    print(f">>> 目标: {os.path.basename(template_path) if template_path else '未找到'}")

    if not template_path or not os.path.exists(template_path):
        print(f"❌ 错误: 找不到图片 {template_path}")
        print("   请检查 Main_Engine.py 传过来的参数是否正确。")
        return

    # 读取图片
    template = cv2.imread(template_path)
    if template is None:
        print("❌ 图片文件损坏，无法读取")
        return

    th, tw = template.shape[:2]

    finish_template = None
    if os.path.exists(finish_path):
        finish_template = cv2.imread(finish_path)

    # 状态变量初始化
    last_w = time.time()
    last_turn = time.time()
    script_start_ts = time.time()

    print("🚀 自动寻路已启动（虚拟模式，Q / PageDown 停止）")

    with mss.mss() as sct:
        monitor = {"top": 0, "left": 0, "width": SCREEN_W, "height": SCREEN_H}
        center_x = SCREEN_W // 2
        player_y = int(SCREEN_H * PLAYER_Y_RATIO)

        while True:
            # 超时检测
            if time_limit is not None and time.time() - script_start_ts > time_limit:
                print("⏰ 时间到，任务终止")
                break

            # 手动停止
            if keyboard.is_pressed("pagedown") or keyboard.is_pressed("q"):
                print("🛑 手动停止")
                break

            # 截图与处理
            try:
                img = np.array(sct.grab(monitor))
                frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            except Exception as e:
                print(f"⚠️ 截图失败: {e}")
                continue

            # 终点检测
            if finish_template is not None:
                res_finish = cv2.matchTemplate(frame, finish_template, cv2.TM_CCOEFF_NORMED)
                _, f_val, _, _ = cv2.minMaxLoc(res_finish)
                if f_val > TEXT_THRESHOLD:
                    print("🏁 到达终点")
                    break

            # 目标检测
            res = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)

            # 没找到目标 -> 停下 W，继续找
            if max_val < THRESHOLD:
                arduino.release("w")
                continue

            cx = max_loc[0] + tw // 2
            cy = max_loc[1] + th // 2

            is_behind = (cy > player_y)
            dx = cx - center_x
            dist = math.hypot(cx - center_x, cy - player_y)
            now = time.time()

            # 距离太近 -> 停
            if dist < STOP_RADIUS:
                arduino.release("w")
            else:
                # 扇形区域判断逻辑 (保持原样)
                in_fan_zone = False
                if not is_behind:
                    h_diff = player_y - cy
                    fan_width = h_diff * FAN_SPREAD_FACTOR + FAN_BASE_WIDTH
                    if abs(dx) < fan_width:
                        in_fan_zone = True

                # 决策逻辑
                if is_behind:
                    arduino.release("w")
                    gain, interval = TURN_GAIN_OUT, TURN_INTERVAL_OUT
                elif in_fan_zone:
                    # 只有在扇形区内才前进
                    if now - last_w > W_INTERVAL:
                        arduino.hold("w")
                        last_w = now
                    gain, interval = TURN_GAIN_IN, TURN_INTERVAL_IN
                else:
                    # 在扇形区外，只转弯不走
                    arduino.release("w")
                    gain, interval = TURN_GAIN_OUT, TURN_INTERVAL_OUT

                # 转弯执行
                if abs(dx) > DEAD_ZONE and (now - last_turn) > interval:
                    move_x = int(dx * gain)
                    # 最小移动阈值防止抖动
                    if abs(move_x) < 3:
                        move_x = 3 if move_x > 0 else -3

                    arduino.move_relative(move_x)
                    last_turn = now

    # 退出前清理
    arduino.release_all()


if __name__ == "__main__":
    main()