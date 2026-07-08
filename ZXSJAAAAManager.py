import subprocess
import time
import sys
import os
import pyautogui
import keyboard

# ================= 配置区 =================
TASK_MAP = {
    "imgs/04.png": "ZXSJ22ocr——1.py",
    # "imgs/renwu_finish.png": "quests/next_quest.py", # 示例：添加更多
}

PYTHON_EXEC = sys.executable


class GameManager:
    def __init__(self):
        self.active_process = None
        self.current_task = None
        self.is_running = False

    def toggle_start(self):
        if not self.is_running:
            print("\n" + "=" * 30)
            print("🚀 启动指令已收到！")
            # --- 新增：5秒倒计时 ---
            for i in range(5, 0, -1):
                print(f"⏳ 请在 {i} 秒内切换回游戏窗口...", end="\r")
                time.sleep(1)

            self.is_running = True
            print("\n▶️ 监控已正式开启！正在扫描屏幕...")
            print("=" * 30)

    def toggle_stop(self):
        self.is_running = False
        print("\n" + "=" * 30)
        print("⏸️ 已停止监控，正在清理后台任务...")
        self.stop_current_task()
        print("✅ 系统已进入静默状态。")
        print("=" * 30)

    def start_task(self, img_path, script_name):
        if self.current_task == script_name:
            # 已经在跑了，不刷屏，只保持状态
            return

        self.stop_current_task()
        print(f"\n🎯 [匹配成功] 场景图: {os.path.basename(img_path)}")
        print(f"执行脚本 -> {script_name}")

        self.active_process = subprocess.Popen([PYTHON_EXEC, script_name])
        self.current_task = script_name

    def stop_current_task(self):
        if self.active_process:
            print(f"[-] 终止旧任务: {self.current_task}")
            self.active_process.terminate()
            try:
                self.active_process.wait(timeout=2)
            except:
                self.active_process.kill()
            self.active_process = None
            self.current_task = None


# ================= 主程序逻辑 =================
def run_manager():
    mgr = GameManager()

    keyboard.add_hotkey('page up', mgr.toggle_start)
    keyboard.add_hotkey('page down', mgr.toggle_stop)

    print("========================================")
    print("   ZXSJ 自动化总控中心 (V2.0 增强版)")
    print("   [Page Up]   : 5秒后开启监控")
    print("   [Page Down] : 立即停止一切")
    print("========================================")

    try:
        while True:
            if mgr.is_running:
                found_task = False

                # 遍历字典，显示正在查找的任务
                for img_target, script_file in TASK_MAP.items():
                    # 提示当前正在尝试寻找的图像
                    # print(f"正在寻找: {os.path.basename(img_target)}...", end="\r")

                    try:
                        res = pyautogui.locateOnScreen(img_target, confidence=0.7, grayscale=True)
                        if res:
                            mgr.start_task(img_target, script_file)
                            found_task = True
                            break
                    except:
                        pass

                if not found_task:
                    if mgr.active_process:
                        # 正在执行脚本，但当前屏幕没看到触发图（正常，脚本正在跑）
                        pass
                    else:
                        print("📡 扫描中：未发现匹配场景...        ", end="\r")

            time.sleep(1)  # 降低扫描频率，防止占满CPU

    except KeyboardInterrupt:
        mgr.stop_current_task()
        print("\n[退出] 程序已彻底关闭。")


if __name__ == "__main__":
    run_manager()