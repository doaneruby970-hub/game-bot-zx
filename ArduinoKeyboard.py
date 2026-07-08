import pydirectinput
import time

# 全局设置：给系统一点反应缓冲
pydirectinput.FAILSAFE = False
pydirectinput.PAUSE = 0.01


class ArduinoKeyboard:
    def __init__(self, port='COM5'):
        # --- 1. 假装连接 (兼容主程序) ---
        print(f"⚠️ [模式切换] 已启用虚拟键盘模式 (忽略端口 {port})")
        print("✅ 请务必以【管理员身份】运行 PyCharm！")

        # --- 2. 启动时的“休克疗法” (关键！) ---
        print("🧹 正在执行启动清理，请勿触碰键盘...")
        # 强制弹起所有可能的修饰键
        for k in ['alt', 'ctrl', 'shift', 'altleft', 'altright', 'ctrlleft', 'shiftleft']:
            pydirectinput.keyUp(k)

        print("⏳ 系统冷却中 (等待 3 秒)...")
        time.sleep(3)  # 让系统消息队列彻底清空
        print("🚀 准备就绪！")

        # 转身参数 (保持原版灵敏度)
        self.PIXELS_PER_30_DEG = 166

        # --- 3. 虚拟按键映射 ---
        # 你的代码习惯用 'left_ctrl'，这里转成 pydirectinput 能认的
        self.KEY_TRANSLATE = {
            'left_ctrl': 'ctrlleft', 'right_ctrl': 'ctrlright', 'ctrl': 'ctrl',
            'left_shift': 'shiftleft', 'right_shift': 'shiftright', 'shift': 'shift',
            'left_alt': 'altleft', 'right_alt': 'altright', 'alt': 'alt',
            'esc': 'esc', 'enter': 'enter', 'space': 'space',
            'tab': 'tab', 'backspace': 'backspace',
            # 小键盘映射 (视情况而定，通常用数字即可)
            'num 1': '1', 'num 2': '2', 'num 3': '3'
        }

    def _map_key(self, key_name):
        k = str(key_name).lower()
        return self.KEY_TRANSLATE.get(k, k)

    # ==========================================
    # 核心动作：带“扫雷”逻辑的按键
    # ==========================================
    def press(self, key_name, duration=None):
        key = self._map_key(key_name)

        # 1. [扫雷] 每次按键前，先强制关掉 Alt，防止幽灵组合键
        # 尤其是按功能键的时候，多加一层保险
        if key in ['m', 'c', 'i', 'b', 'esc', 'enter']:
            pydirectinput.keyUp('alt')
            pydirectinput.keyUp('altleft')

        # 2. [执行] 分解动作：按下 -> 死等 -> 弹起
        # 如果主程序没指定时长，默认按 0.08 秒 (模拟真人)
        hold_time = duration if (duration is not None and duration > 0) else 0.08

        pydirectinput.keyDown(key)
        time.sleep(hold_time)  # 关键！死等 80ms 让游戏看清楚
        pydirectinput.keyUp(key)

    def hold(self, key_name):
        """ 走路专用：只按不松 """
        key = self._map_key(key_name)
        pydirectinput.keyDown(key)

    def release(self, key_name):
        """ 松开按键 """
        key = self._map_key(key_name)
        pydirectinput.keyUp(key)

    def release_all(self):
        """ 紧急停止时清理现场 """
        for k in ['w', 'a', 's', 'd', 'alt', 'ctrl', 'shift']:
            pydirectinput.keyUp(k)
        pydirectinput.mouseUp(button='left')
        pydirectinput.mouseUp(button='right')

    # ==========================================
    # 鼠标动作
    # ==========================================
    def move_relative(self, dx, dy=0):  # 兼容有时候只传一个参数的情况
        pydirectinput.moveRel(int(dx), int(dy), relative=True)

    def click(self):
        self.left_click()

    def left_click(self):
        # 鼠标点击也加上延时，防止点太快无效
        pydirectinput.mouseDown(button='left')
        time.sleep(0.08)
        pydirectinput.mouseUp(button='left')

    def right_click(self):
        pydirectinput.mouseDown(button='right')
        time.sleep(0.08)
        pydirectinput.mouseUp(button='right')

    def middle_click(self):
        pydirectinput.mouseDown(button='middle')
        time.sleep(0.08)
        pydirectinput.mouseUp(button='middle')

    def scroll(self, amount):
        pydirectinput.scroll(int(amount))

    # ==========================================
    # 辅助与兼容
    # ==========================================
    def turn_camera(self, angle_type):
        if angle_type == 'left_30':
            self.move_relative(-self.PIXELS_PER_30_DEG, 0)
        elif angle_type == 'right_30':
            self.move_relative(self.PIXELS_PER_30_DEG, 0)

    # 留空函数：为了不让主程序报错
    def send_cmd(self, cmd):
        pass