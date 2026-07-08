import cv2
import numpy as np
import mss
import time
import serial
import keyboard
import atexit
import math
import os
import sys

# ==========================================
# 0. 预览窗口：等比缩放 + 黑边填充（不拉伸）
# ==========================================
def make_preview_keep_ratio(frame, out_w=410, out_h=280):
    h, w = frame.shape[:2]
    scale = min(out_w / w, out_h / h)  # 等比缩放
    new_w = int(w * scale)
    new_h = int(h * scale)

    resized = cv2.resize(frame, (new_w, new_h))
    canvas = np.zeros((out_h, out_w, 3), dtype=np.uint8)

    x0 = (out_w - new_w) // 2
    y0 = (out_h - new_h) // 2
    canvas[y0:y0 + new_h, x0:x0 + new_w] = resized
    return canvas


# ==========================================
# 1. Arduino 键盘
# ==========================================
class ArduinoKeyboard:
    def __init__(self, port='COM5'):
        self.ser = None
        try:
            self.ser = serial.Serial(port, 115200, timeout=0.02)
            time.sleep(2)
            self.ser.reset_input_buffer()
        except Exception as e:
            print(f"❌ 硬件连接失败: {e}")

        atexit.register(self.release_all)

        self.KEY_MAP = {
            'w': 119,
            'pageup': 211,
            'pagedown': 214,
        }

    def send_cmd(self, cmd):
        if self.ser and self.ser.is_open:
            try:
                self.ser.write(f"{cmd}\n".encode())
            except:
                pass

    def hold(self, key):
        code = self.KEY_MAP.get(key)
        if code:
            self.send_cmd(f"HOLD:{code}")

    def release(self, key):
        code = self.KEY_MAP.get(key)
        if code:
            self.send_cmd(f"REL:{code}")

    def release_all(self):
        self.send_cmd("REL_ALL")

    def move_relative(self, dx):
        dx = max(-100, min(100, dx))
        if dx != 0:
            self.send_cmd(f"MOVE:{dx},0")


# ==========================================
# 2. 720P 参数区
# ==========================================
SCREEN_W = 1280
SCREEN_H = 720

THRESHOLD = 0.60
TEXT_THRESHOLD = 0.70

# --- 走路逻辑 ---
W_INTERVAL = 0.12
STOP_RADIUS = 55
DEAD_ZONE = 28

# --- 扇形参数（更窄：更准）---
# 原来：FAN_BASE_WIDTH=55, FAN_SPREAD_FACTOR=1.05
# 改窄：基础更小、扩张更少
FAN_BASE_WIDTH = 20
FAN_SPREAD_FACTOR = 0.57
FAN_DRAW_LENGTH = 520

# --- 人物参考点（固定在屏幕中下方）---
PLAYER_Y_RATIO = 0.56
PLAYER_CIRCLE_R = 42

# --- 旋转手感：扇形外只旋转，幅度更大、速度更慢 ---
TURN_GAIN_IN = 0.22
TURN_INTERVAL_IN = 0.10

TURN_GAIN_OUT = 0.85
TURN_INTERVAL_OUT = 0.18

# --- 监视窗口 ---
PREVIEW_SIZE = (410, 280)


# ==========================================
# 3. 路径：兼容两种目录（imgs/actions 或 imgs）
# ==========================================
def resolve_paths(root, target_name):
    a_template = os.path.join(root, "imgs", "actions", target_name)
    a_finish = os.path.join(root, "imgs", "actions", "finish.png")

    b_template = os.path.join(root, "imgs", target_name)
    b_finish = os.path.join(root, "finish.png")

    if os.path.exists(a_template):
        return a_template, a_finish

    if os.path.exists(b_template):
        return b_template, b_finish

    return a_template, a_finish


# ==========================================
# 4. 可视化绘制（扇形线 + 圈 + 状态字）
# ==========================================
def draw_overlay(frame, player_pos, fan_left, fan_right, state_text):
    px, py = player_pos

    cv2.circle(frame, (px, py), PLAYER_CIRCLE_R, (255, 0, 255), 2)
    cv2.line(frame, (px, py), fan_left, (255, 0, 0), 2)
    cv2.line(frame, (px, py), fan_right, (255, 0, 0), 2)

    cv2.putText(frame, state_text, (px - 90, py - 70),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2, cv2.LINE_AA)


# ==========================================
# 5. 主逻辑
# ==========================================
def main():
    arduino = ArduinoKeyboard()

    target_name = sys.argv[1].strip() if len(sys.argv) > 1 else "target_template.png"
    root = os.path.dirname(os.path.abspath(__file__))

    template_path, finish_path = resolve_paths(root, target_name)

    if not os.path.exists(template_path):
        print(f"❌ 目标图片不存在: {template_path}")
        print("   你可以把目标图放到：")
        print("   1) imgs/actions/  或  2) imgs/")
        return

    template = cv2.imread(template_path)
    if template is None:
        print("❌ 目标图片读取失败（可能损坏）")
        return

    finish_template = cv2.imread(finish_path) if os.path.exists(finish_path) else None
    if finish_template is None:
        print("⚠️ 未加载 finish.png（找不到或读取失败），将不会自动判定终点")

    th, tw = template.shape[:2]

    is_running = False
    last_w = time.time()
    last_turn = time.time()

    print("🟢 PageUp 开始 | PageDown 暂停 | Q 退出")

    with mss.mss() as sct:
        monitor = {"top": 0, "left": 0, "width": SCREEN_W, "height": SCREEN_H}
        center_x = SCREEN_W // 2
        player_y = int(SCREEN_H * PLAYER_Y_RATIO)

        while True:
            # --- 热键 ---
            if keyboard.is_pressed("page up"):
                if not is_running:
                    is_running = True
                    arduino.release_all()
                    time.sleep(0.35)

            if keyboard.is_pressed("page down"):
                if is_running:
                    is_running = False
                    arduino.release_all()
                    time.sleep(0.35)

            if keyboard.is_pressed("q"):
                break

            if not is_running:
                time.sleep(0.05)
                continue

            # --- 截屏 ---
            img = np.array(sct.grab(monitor))
            frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

            # --- 找终点 ---
            if finish_template is not None:
                res_text = cv2.matchTemplate(frame, finish_template, cv2.TM_CCOEFF_NORMED)
                _, t_val, _, _ = cv2.minMaxLoc(res_text)
                if t_val > TEXT_THRESHOLD:
                    print("🏁 到达终点")
                    arduino.release_all()
                    break

            # --- 找目标 ---
            res = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)

            # --- 先画扇形（不管有没有识别到，都能看到参考）---
            player_pos = (center_x, player_y)
            y_far = max(0, player_y - FAN_DRAW_LENGTH)
            v = player_y - y_far  # >0
            allowed_far = int(v * FAN_SPREAD_FACTOR + FAN_BASE_WIDTH)
            fan_left = (center_x - allowed_far, y_far)
            fan_right = (center_x + allowed_far, y_far)

            if max_val < THRESHOLD:
                arduino.release("w")
                draw_overlay(frame, player_pos, fan_left, fan_right, "SEARCHING")

                preview = make_preview_keep_ratio(frame, PREVIEW_SIZE[0], PREVIEW_SIZE[1])
                cv2.imshow("Monitor", preview)
                cv2.waitKey(1)
                continue

            # 目标中心点
            cx = max_loc[0] + tw // 2
            cy = max_loc[1] + th // 2

            # 画目标框
            cv2.rectangle(frame, max_loc, (max_loc[0] + tw, max_loc[1] + th), (0, 255, 0), 2)

            # --- 后方(南方)绝不按W ---
            is_behind = (cy > player_y)
            dx = cx - center_x

            # 距离（用于停止）
            dist = math.hypot(cx - center_x, cy - player_y)
            now = time.time()

            if dist < STOP_RADIUS:
                arduino.release("w")
                state = "ARRIVED"
            else:
                # --- 扇形判断：只对“前方”生效 ---
                in_fan_zone = False
                if not is_behind:
                    h_diff = player_y - cy  # 前方时为正
                    fan_width = h_diff * FAN_SPREAD_FACTOR + FAN_BASE_WIDTH
                    if abs(dx) < fan_width:
                        in_fan_zone = True

                # --- 行为：扇形内按W，扇形外只转向 ---
                if is_behind:
                    arduino.release("w")
                    state = "TURNING(BEHIND)"
                    gain = TURN_GAIN_OUT
                    interval = TURN_INTERVAL_OUT

                elif in_fan_zone:
                    if now - last_w > W_INTERVAL:
                        arduino.hold("w")
                        last_w = now
                    state = "MOVING"
                    gain = TURN_GAIN_IN
                    interval = TURN_INTERVAL_IN
                else:
                    arduino.release("w")
                    state = "TURNING"
                    gain = TURN_GAIN_OUT
                    interval = TURN_INTERVAL_OUT

                # --- 转向执行 ---
                if abs(dx) > DEAD_ZONE and (now - last_turn) > interval:
                    move_x = int(dx * gain)
                    if abs(move_x) < 3:
                        move_x = 3 if move_x > 0 else -3
                    arduino.move_relative(move_x)
                    last_turn = now

            # --- 画 overlay（扇形线+圈+状态）---
            draw_overlay(frame, player_pos, fan_left, fan_right, state)

            # --- 预览窗口：等比缩放 + 黑边填充 ---
            preview = make_preview_keep_ratio(frame, PREVIEW_SIZE[0], PREVIEW_SIZE[1])
            cv2.imshow("Monitor", preview)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    arduino.release_all()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
