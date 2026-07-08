import pyautogui
import keyboard
import mouse
import time
import json
import os
import string
from ArduinoKeyboard import ArduinoKeyboard

# --- 配置 ---
SAVE_FOLDER = "./quests"
RECORD_KEY_START = 'pageup'
RECORD_KEY_STOP = 'pagedown'
PORT = 'COM5'

if not os.path.exists(SAVE_FOLDER): os.makedirs(SAVE_FOLDER)

print(f"正在连接 Arduino ({PORT}) 以便在录制时实时响应转身...")
kb = ArduinoKeyboard(PORT)

# --- 1. 定义监听按键列表 ---
list_abc = list(string.ascii_lowercase)
list_123 = [str(i) for i in range(10)]
list_f = [f'f{i}' for i in range(1, 13)]
list_spec = [
    'alt', 'ctrl', 'shift', 'space', 'tab', 'esc', 'enter', 'backspace',
    'up', 'down', 'left', 'right', 'delete', 'end',
    'pagedown', 'pageup',
    '`', '-', '=', '[', ']', '\\', ';', '\'', ',', '.', '/'
]
list_numpad = [
    'num 0', 'num 1', 'num 2', 'num 3', 'num 4',
    'num 5', 'num 6', 'num 7', 'num 8', 'num 9',
    'add', 'subtract', 'multiply', 'divide', 'decimal', 'num enter', 'num lock'
]
list_turn = ['insert', 'home']

WATCH_KEYS = list_abc + list_123 + list_f + list_spec + list_turn + list_numpad

actions = []
start_time = 0


def on_mouse_event(event):
    global actions, start_time
    if start_time == 0: return
    if isinstance(event, mouse.WheelEvent):
        # 【高精度修改】不进行四舍五入，保留原始时间戳
        current_time = time.time() - start_time
        # 【高精度修改】移除 print，防止 I/O 阻塞
        actions.append({"t": current_time, "action": "scroll", "delta": int(event.delta)})


def record_task():
    global actions, start_time
    print(f"\n=== 全能录制器 (高精度无损版) ===")
    print(f"1. 按 {RECORD_KEY_START} 开始，{RECORD_KEY_STOP} 结束")
    print(f"注意：录制过程中不再打印按键信息，以保证最大采样率！")

    keyboard.wait(RECORD_KEY_START)
    # 给一点缓冲时间防止把启动键录进去
    time.sleep(0.3)
    print("\n>>> 开始录制！(高性能模式运行中...)")

    actions = []
    start_time = time.time()
    start_x, start_y = pyautogui.position()
    actions.append({"t": 0, "x": start_x, "y": start_y, "action": "start"})

    mouse.hook(on_mouse_event)

    key_states = {k: False for k in WATCH_KEYS}
    mouse_states = {'left': False, 'right': False, 'middle': False}

    try:
        while True:
            # 极速循环检测，任何阻塞都会导致丢帧
            if keyboard.is_pressed(RECORD_KEY_STOP):
                break

            # 【高精度修改】使用原始浮点数时间
            current_time = time.time() - start_time
            x, y = pyautogui.position()

            # 1. 移动
            last_action = actions[-1] if actions else {}
            last_x = last_action.get('x', -1)
            last_y = last_action.get('y', -1)

            # 只有坐标发生变化才记录，避免数据冗余，但检查频率极高
            if x != last_x or y != last_y:
                actions.append({"t": current_time, "x": x, "y": y, "action": "move"})

            # 2. 鼠标按键
            for btn in ['left', 'right', 'middle']:
                if mouse.is_pressed(btn):
                    if not mouse_states[btn]:
                        # 【高精度修改】移除 print
                        actions.append({"t": current_time, "x": x, "y": y, "action": "mouse_down", "key": btn})
                        mouse_states[btn] = True
                else:
                    if mouse_states[btn]:
                        actions.append({"t": current_time, "x": x, "y": y, "action": "mouse_up", "key": btn})
                        mouse_states[btn] = False

            # 3. 键盘
            for k in WATCH_KEYS:
                try:
                    is_pressed = keyboard.is_pressed(k)
                except:
                    is_pressed = False

                if is_pressed and not key_states[k]:
                    if k == 'insert':
                        # 【保留】Arduino 硬件操作逻辑不变
                        actions.append({"t": current_time, "action": "turn_left_30"})
                        kb.turn_camera('left_30')
                    elif k == 'home':
                        actions.append({"t": current_time, "action": "turn_right_30"})
                        kb.turn_camera('right_30')
                    else:
                        actions.append({"t": current_time, "action": "key_down", "key": k})
                    key_states[k] = True

                elif not is_pressed and key_states[k]:
                    if k not in ['insert', 'home']:
                        actions.append({"t": current_time, "action": "key_up", "key": k})
                    key_states[k] = False

            # 【高精度修改】极限休眠，防止 CPU 100% 占用的同时保证约 1000Hz 轮询率
            # 0.02秒会导致每秒只有50帧，改为0.001秒
            time.sleep(0.001)

    finally:
        mouse.unhook(on_mouse_event)
        # 记录结束时的松开动作
        end_time = time.time() - start_time
        for k, is_down in key_states.items():
            if is_down and k not in ['insert', 'home']:
                actions.append({"t": end_time, "action": "key_up", "key": k})
        for btn in ['left', 'right', 'middle']:
            if mouse_states[btn]:
                actions.append({"t": end_time, "action": "mouse_up", "key": btn})
        start_time = 0

    print(f"\n>>> 录制结束！共 {len(actions)} 动作")

    while True:
        try:
            name = input("任务名 (q退出): ")
        except:
            name = "temp"
        if name.lower() == 'q': break
        if not name.endswith(".json"): name += ".json"

        full_path = os.path.join(SAVE_FOLDER, name)
        with open(full_path, "w", encoding='utf-8') as f:
            # 写入时保持完整精度
            json.dump(actions, f, ensure_ascii=False, indent=4)
        print(f"✅ 保存成功: {full_path}")
        break


if __name__ == "__main__":
    while True: record_task()