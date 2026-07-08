import time
import json
import os
import sys
import pydirectinput
import keyboard  # 用于监听紧急停止

# ================= 配置 =================
# ⚠️ 必须设置：防止鼠标移动到角落时报错
pydirectinput.FAILSAFE = False
# ⚠️ 必须设置：设为0以保证连贯性，由代码控制延迟
pydirectinput.PAUSE = 0.001

STOP_KEY = 'pagedown'  # 紧急停止键

# 自动获取路径
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

# 键名映射表：将 pynput 录制的名称转换为 pydirectinput 能识别的名称
KEY_MAPPING = {
    # --- 1. 普通功能键 ---
    'Key.space': 'space',
    'Key.enter': 'enter',
    'Key.tab': 'tab',
    'Key.esc': 'esc',
    'Key.backspace': 'backspace',
    'Key.caps_lock': 'capslock',
    'Key.delete': 'delete',
    'Key.insert': 'insert',
    'Key.home': 'home',
    'Key.end': 'end',
    'Key.page_up': 'pageup',
    'Key.page_down': 'pagedown',
    'Key.print_screen': 'printscreen',
    'Key.scroll_lock': 'scrolllock',
    'Key.pause': 'pause',

    # --- 2. 方向键 ---
    'Key.left': 'left',
    'Key.right': 'right',
    'Key.up': 'up',
    'Key.down': 'down',

    # --- 3. 修饰键 (分左右) ---
    'Key.shift': 'shift',       # 有些系统不分左右
    'Key.shift_r': 'shiftright',
    'Key.ctrl_l': 'ctrlleft',
    'Key.ctrl_r': 'ctrlright',
    'Key.alt_l': 'altleft',
    'Key.alt_r': 'altright',
    'Key.cmd': 'win',           # Windows 键
    'Key.cmd_l': 'winleft',
    'Key.cmd_r': 'winright',
    'Key.menu': 'apps',         # 菜单键

    # --- 4. F 功能键 ---
    'Key.f1': 'f1', 'Key.f2': 'f2', 'Key.f3': 'f3', 'Key.f4': 'f4',
    'Key.f5': 'f5', 'Key.f6': 'f6', 'Key.f7': 'f7', 'Key.f8': 'f8',
    'Key.f9': 'f9', 'Key.f10': 'f10', 'Key.f11': 'f11', 'Key.f12': 'f12',

    # --- 5. 小键盘区 (Numpad) ---
    # 录制器修复后会输出这些名字，必须在这里接住
    'Key.num_lock': 'numlock',
    'Key.num_add': 'add',          # 小键盘 +
    'Key.num_sub': 'subtract',     # 小键盘 -
    'Key.num_mul': 'multiply',     # 小键盘 *
    'Key.num_div': 'divide',       # 小键盘 /
    'Key.num_decimal': 'decimal',  # 小键盘 . (点)
    'Key.num_enter': 'enter',      # 小键盘回车 (pydirectinput 通常不区分主回车和小回车，都叫 enter)

    # --- 6. 小键盘数字 (必须开启 NumLock) ---
    # 注意：pynput 在 NumLock 开启时通常录制为字符 '0'-'9'，但在某些驱动下可能识别为特定 Key 对象
    '<96>': 'num0',
    '<97>': 'num1',
    '<98>': 'num2',
    '<99>': 'num3',
    '<100>': 'num4',
    '<101>': 'num5',
    '<102>': 'num6',
    '<103>': 'num7',
    '<104>': 'num8',
    '<105>': 'num9',

    # 备用兼容 (以防录制器把小键盘数字记成了特殊对象)
    'Key.num_0': 'num0', 'Key.num_1': 'num1', 'Key.num_2': 'num2',
    'Key.num_3': 'num3', 'Key.num_4': 'num4', 'Key.num_5': 'num5',
    'Key.num_6': 'num6', 'Key.num_7': 'num7', 'Key.num_8': 'num8',
    'Key.num_9': 'num9',
}


def get_pydirectinput_key(raw_key):
    """ 将录制的键名转换为 pydirectinput 可用的键名 """
    if raw_key in KEY_MAPPING:
        return KEY_MAPPING[raw_key]
    return raw_key.replace("'", "").lower()


# ================= 核心功能函数 =================

def play_json_task(task_info, auto_mode=False):
    """执行单个 JSON 任务"""
    full_path = task_info['full_path']
    task_name = task_info['name']

    if not os.path.exists(full_path):
        print(f"[Player] ❌ 文件不存在: {full_path}")
        return

    try:
        with open(full_path, "r", encoding='utf-8') as f:
            events = json.load(f)
    except Exception as e:
        print(f"[Player] ❌ JSON 文件损坏: {e}")
        return

    print(f"[Player] ▶️ 执行: {task_name} ({os.path.basename(full_path)})")

    if not auto_mode:
        print(f"🛑 紧急停止: 按 [{STOP_KEY.upper()}]")
        for i in range(3, 0, -1):
            print(f"⏳ 倒计时 {i} 秒...", end="\r")
            time.sleep(1)
        print("\n🚀 开始行动！")
    else:
        # 自动模式稍微缓冲一下，防止切换太快
        time.sleep(0.5)

    start_play_time = time.time()

    # 遍历 JSON 中的每一个动作
    for i, event in enumerate(events):
        # 1. 紧急停止检测
        if keyboard.is_pressed(STOP_KEY):
            print("\n🛑 !!! 用户触发紧急停止 !!!")
            # 这里的 release_all 只需要简单的松开常用键即可
            for k in ['w', 'a', 's', 'd', 'shift', 'ctrl', 'alt']:
                pydirectinput.keyUp(k)
            if auto_mode: sys.exit()
            return

        # 2. 时间同步控制
        # 兼容旧格式(data[i]['t']) 和 新格式(event['time'])
        target_time = event.get('time', event.get('t', 0))
        current_elapsed = time.time() - start_play_time

        wait_time = target_time - current_elapsed
        if wait_time > 0:
            time.sleep(wait_time)

        # 3. 动作分发 (纯软件驱动)
        action_type = event.get('type', event.get('action'))  # 兼容新旧字段名

        try:
            if action_type == 'key_down':
                key = get_pydirectinput_key(event['key'])
                pydirectinput.keyDown(key)

            elif action_type == 'key_up':
                key = get_pydirectinput_key(event['key'])
                pydirectinput.keyUp(key)

            elif action_type == 'mouse_move':
                # 新格式用 dx/dy
                dx = int(event.get('dx', 0))
                dy = int(event.get('dy', 0))
                if dx != 0 or dy != 0:
                    pydirectinput.moveRel(dx, dy, relative=True)

            # 兼容旧格式的 'move' (虽然纯软件模式下推荐用 mouse_move)
            elif action_type == 'move':
                pass  # 旧版绝对坐标逻辑较难完全复刻，建议重录

            elif action_type == 'mouse_down':
                # 新格式用 button 名，旧格式可能不同，这里做兼容
                btn = event.get('button', 'left')
                if btn == 'Key.left': btn = 'left'  # 兼容旧数据脏数据
                pydirectinput.mouseDown(button=btn)

            elif action_type == 'mouse_up':
                btn = event.get('button', 'left')
                pydirectinput.mouseUp(button=btn)

            elif action_type == 'scroll':
                # pydirectinput scroll 大概 120 为一格
                delta = event.get('dy', event.get('delta', 0))
                pydirectinput.scroll(int(delta * 120))

        except Exception as e:
            # 容错处理，防止某一行数据坏了导致整个崩溃
            print(f"⚠️ 动作执行失败 [{i}]: {e}")

    print(f"[Player] ✅ {task_name} 播放完毕")


# ================= 主程序入口 =================

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # A. 自动模式：由 Main_Engine 传全路径过来
        # 你的主程序是通过 subprocess.Popen([python, bofangqi.py, json_path]) 调用的
        json_path = sys.argv[1].strip()

        auto_task = {
            "id": "AUTO",
            "name": "自动任务",
            "full_path": json_path
        }
        play_json_task(auto_task, auto_mode=True)
        sys.exit()
    else:
        # B. 手动调试模式
        print("💡 建议通过根目录的启动脚本运行游戏。")
        # 尝试找一个默认文件调试
        debug_json = os.path.join(PROJECT_ROOT, "ZhuXian", "imgs", "actions", "按一下B.json")

        # 如果找不到，就弹窗让用户选（复刻你喜欢的交互）
        if not os.path.exists(debug_json):
            print("未找到默认调试文件，请输入文件路径:")
            # 这里简单处理，实际调试建议直接拖文件进来
            pass
        else:
            play_json_task({"id": "DEBUG", "name": "调试任务", "full_path": debug_json})