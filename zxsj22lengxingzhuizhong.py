import cv2
import numpy as np
import mss
import time
import serial
import keyboard
import atexit
import math


# ==========================================
# 1. 硬件控制类
# ==========================================
class ArduinoKeyboard:
    def __init__(self, port='COM5'):
        self.ser = None
        try:
            self.ser = serial.Serial(port, 115200, timeout=0.02)
            time.sleep(2)
            self.ser.reset_input_buffer()
            print(f"✅ 硬件连接成功: {port}")
        except Exception as e:
            print(f"❌ 硬件连接失败: {e}")

        atexit.register(self.release_all)

        self.KEY_MAP = {
            'w': 119, 'a': 97, 's': 115, 'd': 100,
            'pageup': 211, 'pagedown': 214,
        }

    def send_cmd(self, cmd):
        if not self.ser or not self.ser.is_open: return
        try:
            self.ser.write(f"{cmd}\n".encode())
        except:
            pass

    def hold(self, key):
        code = self.KEY_MAP.get(str(key).lower(), None)
        if code: self.send_cmd(f"HOLD:{code}")

    def release(self, key):
        code = self.KEY_MAP.get(str(key).lower(), None)
        if code: self.send_cmd(f"REL:{code}")

    def release_all(self):
        self.send_cmd("REL_ALL")

    def move_relative(self, dx, dy):
        if dx == 0 and dy == 0: return
        dx = max(-100, min(100, dx))
        self.send_cmd(f"MOVE:{int(dx)},0")


# ==========================================
# 2. 核心逻辑 (修复报错版)
# ==========================================
TEMPLATE_PATH = 'img_1.png'
FINISH_PATH = 'finish.png'

THRESHOLD = 0.60
TEXT_THRESHOLD = 0.7

# --- 🎯 参数调整区 ---
SPEED_FACTOR = 0.15  # 角度大建议： 把 0.04 改大。试一试 0.08 或 0.1不要超过 0.2，否则镜头会乱飞
MOUSE_INTERVAL = 0.2  # 频率慢试一试 0.15 (每秒转6次) 或 0.2 (每秒转5次)。

# 几何参数
PLAYER_FEET_Y = 620  # 脚底红线位置
STOP_RADIUS = 80
FAN_SPREAD_FACTOR = 1.0
FAN_BASE_WIDTH = 50
DEAD_ZONE = 60
W_INTERVAL = 0.2


def main():
    arduino = ArduinoKeyboard(port='COM5')

    print("读取图片模板...")
    template = cv2.imread(TEMPLATE_PATH)
    if template is None:
        print("❌ 错误：找不到 target_template.png")
        return
    th, tw = template.shape[:2]

    finish_template = cv2.imread(FINISH_PATH)
    if finish_template is not None:
        print("✅ 已加载终点文字识别")

    is_running = False

    # 计时器
    last_w_time = time.time()
    last_mouse_time = time.time()

    print("\n🟢 [脚本已就绪] 按 PageUp 开始，PageDown 停止")

    with mss.mss() as sct:
        monitor = sct.monitors[1]
        screen_h = monitor['height']
        screen_w = monitor['width']

        # 🟢 修复点：补上了 center_y 的定义
        center_x = screen_w // 2
        center_y = screen_h // 2

        feet_pos = (center_x, PLAYER_FEET_Y)

        while True:
            # --- 1. 启动逻辑 ---
            if keyboard.is_pressed('page up'):
                if not is_running:
                    print("🚀 启动中... (重置状态)")
                    arduino.release_all()
                    if arduino.ser: arduino.ser.reset_input_buffer()

                    current_t = time.time()
                    last_w_time = current_t + 1.0
                    last_mouse_time = current_t

                    is_running = True
                    time.sleep(0.5)

            # --- 2. 停止逻辑 ---
            if keyboard.is_pressed('page down'):
                if is_running:
                    print("🛑 停止！")
                    is_running = False
                    arduino.release_all()
                    time.sleep(0.5)
                continue

            if not is_running:
                time.sleep(0.1)
                continue

            # --- 3. 视觉识别 ---
            try:
                img = np.array(sct.grab(monitor))
                frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

                # 找黄框
                res = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

                # 找文字
                text_found = False
                if finish_template is not None:
                    res_text = cv2.matchTemplate(frame, finish_template, cv2.TM_CCOEFF_NORMED)
                    _, t_max_val, _, _ = cv2.minMaxLoc(res_text)
                    if t_max_val > TEXT_THRESHOLD:
                        text_found = True
            except:
                continue

            # --- 4. 逻辑判定 ---
            target_found = (max_val >= THRESHOLD)
            current_time = time.time()

            dx = 0
            is_arrived = False
            in_fan_zone = False
            is_behind = False

            # A. 文字到达判定
            if text_found:
                print(f"🔤 识别到终点文字 -> 🛑 自动暂停")
                is_running = False
                arduino.release_all()
                time.sleep(1.0)
                continue

                # B. 黄框判定
            elif target_found:
                top_left = max_loc
                cx = top_left[0] + tw // 2
                cy = top_left[1] + th // 2
                dx = cx - center_x

                # 身后检测
                if cy > PLAYER_FEET_Y:
                    is_behind = True

                # 进圈判定
                dist = math.sqrt((cx - feet_pos[0]) ** 2 + (cy - feet_pos[1]) ** 2)
                if dist < STOP_RADIUS:
                    is_arrived = True

                # 扇形判定
                if not is_behind:
                    h_diff = feet_pos[1] - cy
                    allowed = (h_diff * FAN_SPREAD_FACTOR) + FAN_BASE_WIDTH
                    if abs(dx) < allowed:
                        in_fan_zone = True

                # 绘图
                color = (0, 0, 255) if is_arrived else (0, 255, 0)
                cv2.rectangle(frame, top_left, (top_left[0] + tw, top_left[1] + th), color, 2)

                # 画扇形辅助线
                top_w = (feet_pos[1] * FAN_SPREAD_FACTOR) + FAN_BASE_WIDTH
                cv2.line(frame, feet_pos, (int(feet_pos[0] - top_w), 0), (255, 0, 0), 2)
                cv2.line(frame, feet_pos, (int(feet_pos[0] + top_w), 0), (255, 0, 0), 2)

                # 状态显示
                status_text = "MOVING"
                if is_arrived:
                    status_text = "ARRIVED"
                elif is_behind:
                    status_text = "TURNING (BEHIND!)"
                elif not in_fan_zone:
                    status_text = "TURNING (ALIGNING)"

                # 这里就是之前报错的地方，现在 center_y 已经定义了
                cv2.putText(frame, status_text, (center_x - 100, center_y - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                            (0, 255, 255), 2)

            # --- 5. 硬件执行 ---
            if arduino.ser:
                if is_arrived:
                    arduino.release('w')
                elif target_found:

                    # 🚶 走路逻辑 (扇形内且不在身后)
                    if in_fan_zone and not is_behind:
                        if current_time - last_w_time > W_INTERVAL:
                            arduino.hold('w')
                            last_w_time = current_time
                    else:
                        arduino.release('w')

                    # 🔄 转向逻辑
                    if abs(dx) > DEAD_ZONE:
                        if current_time - last_mouse_time > MOUSE_INTERVAL:
                            move_x = int(dx * SPEED_FACTOR)
                            if abs(move_x) > 3:
                                arduino.move_relative(move_x, 0)
                                last_mouse_time = current_time
                else:
                    arduino.release('w')

            # --- 6. 监视窗 ---
            # 红线
            cv2.line(frame, (0, PLAYER_FEET_Y), (screen_w, PLAYER_FEET_Y), (0, 0, 255), 2)
            cv2.putText(frame, "NO WALK ZONE (BEHIND)", (10, PLAYER_FEET_Y + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                        (0, 0, 255), 2)

            cv2.circle(frame, feet_pos, STOP_RADIUS, (255, 0, 255), 2)
            small = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
            cv2.imshow("Monitor", small)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    arduino.release_all()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()