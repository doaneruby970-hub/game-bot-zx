import time
import json
import os
import keyboard  # 用于监听 PageDown 紧急停止
from ArduinoKeyboard import ArduinoKeyboard

# --- 配置区 ---
PORT = 'COM5'
QUEST_FOLDER = "./quests"
STOP_KEY = 'pagedown'  # 紧急停止键

# 初始化 (移除了 HumanMouse)
kb = ArduinoKeyboard(PORT)


def list_files():
    if not os.path.exists(QUEST_FOLDER): return []
    files = [f for f in os.listdir(QUEST_FOLDER) if f.endswith(".json")]
    files.sort()
    return files


def play_file(filename):
    path = os.path.join(QUEST_FOLDER, filename)
    with open(path, "r", encoding='utf-8') as f:
        data = json.load(f)

    print(f"\n准备执行任务: {filename}")
    print(f">>> 按 {STOP_KEY} 可紧急停止")
    print(">>> 请立即切换回游戏窗口！")

    for i in range(3, 0, -1):
        print(f"倒计时: {i} 秒...", end="\r")
        time.sleep(1)
    print(">>> 开始行动！(高性能模式) \n")

    # 初始坐标 (如果录制文件里有 start 动作)
    last_x, last_y = 0, 0
    if data and data[0].get('action') == 'start':
        last_x = data[0].get('x', 0)
        last_y = data[0].get('y', 0)
        start_idx = 1
    else:
        start_idx = 0

    start_play_time = time.time()

    # 移除手动补偿变量，完全依赖系统时钟的绝对差值，这是最精准的防漂移方式

    for i in range(start_idx, len(data)):
        # 紧急停止检测
        if keyboard.is_pressed(STOP_KEY):
            print("\n!!! 紧急停止 !!!")
            kb.release_all()
            return

        point = data[i]
        target_time = point['t']

        # 计算应该睡多久
        # 使用绝对时间差 (target_time) 减去 (当前流逝时间)，自动修正上一帧的执行误差
        current_elapsed = time.time() - start_play_time
        wait_time = target_time - current_elapsed

        if wait_time > 0:
            # 只有当等待时间大于0才休眠，保证动作严格按照时间戳触发
            time.sleep(wait_time)

        action = point.get('action')

        # --- 1. 移动 (相对移动) ---
        if action == 'move':
            # 计算这一帧和上一帧的相对位移
            cur_x = point.get('x', last_x)
            cur_y = point.get('y', last_y)

            dx = cur_x - last_x
            dy = cur_y - last_y

            if dx != 0 or dy != 0:
                # 直接发送原始位移，不经过任何算法处理
                kb.move_relative(dx, dy)

            last_x, last_y = cur_x, cur_y

        # --- 2. 专用转身 ---
        elif action == 'turn_left_30':
            # 移除 print 以节省 I/O 时间
            kb.turn_camera('left_30')

        elif action == 'turn_right_30':
            kb.turn_camera('right_30')

        # --- 3. 滚轮 ---
        elif action == 'scroll':
            delta = point.get('delta', 0)
            kb.scroll(delta)

        # --- 4. 键盘按键 ---
        elif action == 'key_down':
            key = point['key']
            kb.hold(key)

        elif action == 'key_up':
            key = point['key']
            kb.release(key)

        # --- 5. 鼠标按键 (左/右/中) ---
        elif action == 'mouse_down':
            key = point['key']

            # 如果按下时坐标变了，先移过去
            cur_x = point.get('x', last_x)
            cur_y = point.get('y', last_y)
            dx = cur_x - last_x
            dy = cur_y - last_y
            if dx != 0 or dy != 0:
                kb.move_relative(dx, dy)
                last_x, last_y = cur_x, cur_y

            # 执行按下
            if key == 'left':
                kb.send_cmd("MP:l")
            elif key == 'right':
                kb.send_cmd("MP:r")
            elif key == 'middle':
                kb.send_cmd("MP:m")

        elif action == 'mouse_up':
            key = point['key']
            if key == 'left':
                kb.send_cmd("MR:l")
            elif key == 'right':
                kb.send_cmd("MR:r")
            elif key == 'middle':
                kb.send_cmd("MR:m")

    print("\n✅ 任务执行完毕")
    kb.release_all()  # 保险起见，松开所有键


if __name__ == "__main__":
    while True:
        print("\n--- 任务列表 ---")
        files = list_files()
        if not files:
            print("没有找到录制文件！")
            print("请先运行录制器生成 .json 文件。")
            time.sleep(2)
            continue

        for i, f in enumerate(files):
            print(f"[{i + 1}] {f}")

        print(f"\n[Q] 退出")
        choice = input("请选择 (输入序号): ")

        if choice.lower() == 'q': break

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(files):
                play_file(files[idx])
            else:
                print("❌ 序号无效")
        except ValueError:
            print("❌ 请输入数字")