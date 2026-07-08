import csv
import time
import os
import sys
import subprocess
import pyautogui
import pydirectinput
import keyboard

# 引入你的 OCR 识别功能
# 确保 shibiedengji.py 和 Main_Engine.py 在同一个文件夹，或者在 python 路径里
try:
    from shibiedengji import detect_level_once
except ImportError:
    print("⚠️ 没找到 Level_Monitor.py，无法识别等级！")
    def detect_level_once(): return 0
# ================= 配置区 =================
# 全屏扫描 (REGION_MISSION_BAR = None)
REGION_MISSION_BAR = None
# 找图相似度
IMG_CONFIDENCE = 0.8


# ================= 核心引擎类 =================

class GameEngine:
    def __init__(self, game_name='ZhuXian', task_file='tasks.csv'):
        # 1. 定位 core 文件夹
        core_dir = os.path.dirname(os.path.abspath(__file__))
        # 2. 自动定位项目根目录 (GameBot)，即 core 的上一级
        self.project_root = os.path.dirname(core_dir)

        # 3. 定义当前游戏的资源根目录
        # 这样 self.game_path 就会变成 E:\...\GameBot\ZhuXian 或 NiShuiHan
        self.game_path = os.path.join(self.project_root, game_name)

        # 4. 加载任务表 (去对应的游戏文件夹下找)
        self.task_csv = os.path.join(self.game_path, task_file)

        # 检查文件是否存在，防止闪退
        if not os.path.exists(self.task_csv):
            print(f"❌ 找不到任务表，请检查路径: {self.task_csv}")
            self.tasks = []
        else:
            self.tasks = self.load_tasks(self.task_csv)

        self.current_process = None

    def get_full_path(self, rel_path):
        """将相对路径转换为当前游戏文件夹下的绝对路径"""
        # 关键改动：所有相对路径（如 imgs/xx.png）现在都相对于 self.game_path
        return os.path.join(self.game_path, rel_path)

    def load_tasks(self, filepath):
        """读取 CSV 任务表"""
        tasks = []
        if not os.path.exists(filepath):
            print(f"❌ 找不到任务表，请检查路径: {filepath}")
            return []
        try:
            with open(filepath, mode='r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    tasks.append(row)

            # 🟢 这里的修改能让你清楚看到加载的是哪个资源文件夹
            game_folder = os.path.basename(os.path.dirname(filepath))
            print(f"✅ 成功加载 [{game_folder}] 资源下的 {os.path.basename(filepath)}，共 {len(tasks)} 个任务。")
            return tasks
        except Exception as e:
            print(f"❌ 读取任务表失败: {e}")
            return []

    def check_state(self, state_img_path):
        """检查图片是否存在"""
        if not state_img_path: return False

        full_path = self.get_full_path(state_img_path)
        if not os.path.exists(full_path):
            return False

        try:
            res = pyautogui.locateOnScreen(
                full_path,
                region=REGION_MISSION_BAR,
                confidence=0.85,
                grayscale=True
            )
            return res is not None
        except Exception:
            return False

    def wait_for_state_image(self, state_img, timeout=360):
        """等待任务图标出现"""
        print(f"🔍 [等待触发] {os.path.basename(state_img)}")
        start_time = time.time()

        while True:
            elapsed = time.time() - start_time
            if elapsed > timeout:
                print(f"\n❌ 超时！{timeout}秒内未检测到任务图标。")
                return False

            if self.check_state(state_img):
                print(f"   ✅ 任务图标已出现！")
                return True
            time.sleep(1)

    def wait_for_multi_state(self, img_list, timeout=360):
        """同时等待多张图片，返回最先出现的那张图的【索引】和【图片名】"""
        print(f"🔍 [分支判断] 正在同时监测: {img_list}")
        start_time = time.time()

        while True:
            elapsed = time.time() - start_time
            if elapsed > timeout:
                print(f"\n❌ 超时！{timeout}秒内未检测到任何分支图片。")
                return -1, None

            for index, img_name in enumerate(img_list):
                if self.check_state(img_name):
                    print(f"   ⚡ 命中分支: {os.path.basename(img_name)} (索引: {index})")
                    return index, img_name
            time.sleep(0.5)

    def run_script_safe(self, script_path, next_stop_img, timeout=360, arg=None):
        """核心修复：智能识别绝对路径和游戏相对路径"""
        # 如果是绝对路径（如 core/bofangqi.py），直接用；否则拼上游戏目录
        if os.path.isabs(script_path):
            full_path = script_path
        else:
            full_path = self.get_full_path(script_path)

        if not os.path.exists(full_path):
            print(f"❌ 脚本文件缺失: {full_path}")
            return False

        cmd = [sys.executable, full_path]
        if arg: cmd.append(arg)

        arg_str = f" [参数: {arg}]" if arg else ""
        print(f"      ▶️ 执行: {os.path.basename(script_path)}{arg_str}")

        self.current_process = subprocess.Popen(cmd)
        start_t = time.time()

        while self.current_process.poll() is None:
            if time.time() - start_t > timeout:
                print("      ⌛ 子任务超时，强制停止。")
                self.current_process.terminate()
                return False

            if next_stop_img and self.check_state(next_stop_img):
                print(f"      ✨ 检测到下一关图片！立即终止子步骤。")
                self.current_process.terminate()
                self.current_process.wait()
                return True  # 被中断
            time.sleep(0.5)
        return False

    def execute_click(self, img_path):
        """简单的识图点击"""
        full = self.get_full_path(img_path)
        if os.path.exists(full):
            try:
                res = pyautogui.locateOnScreen(full, confidence=IMG_CONFIDENCE)
                if res:
                    pydirectinput.click(pyautogui.center(res).x, pyautogui.center(res).y)
                    time.sleep(0.5)
            except:
                pass

    def execute_sequence_logic(self, seq_file, next_stop_img, global_timeout=360):
        """读取 txt 清单一步步执行"""
        full_seq_path = self.get_full_path(seq_file)
        if not os.path.exists(full_seq_path):
            print(f"❌ 找不到清单文件: {seq_file}")
            return

        steps = []
        with open(full_seq_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if '|' in line and not line.startswith('#'):
                    steps.append(line.split('|'))

        print(f"   📜 载入序列: {len(steps)} 步")
        start_time = time.time()

        for idx, (action_type, action_target) in enumerate(steps):
            if time.time() - start_time > global_timeout:
                print("   ⌛ 序列整体超时。")
                return
            if next_stop_img and self.check_state(next_stop_img):
                print("   ✨ (步骤前) 发现下一关，跳过剩余步骤！")
                return

            print(f"   👉 第 {idx + 1} 步: {action_type}")
            interrupted = False

            if action_type == 'JSON':
                # 🟡 修复：强制指向 core 播放器
                player_script = os.path.join(self.project_root, "core", "bofangqi.py")
                full_json_path = self.get_full_path(action_target)
                interrupted = self.run_script_safe(player_script, next_stop_img, arg=full_json_path)

            elif action_type == 'SCRIPT':
                interrupted = self.run_script_safe(action_target, next_stop_img)

            elif action_type == 'AUTO_F':
                script_path = os.path.join(self.project_root, "core", "zxsjFFocr.py")  # 确保指向 core
                full_img_path = self.get_full_path(action_target)
                interrupted = self.run_script_safe(script_path, next_stop_img, arg=full_img_path)


            elif action_type == 'AUTO_CLICK':
                script_path = os.path.join(self.project_root, "core", "zxsj22ocr.py")
                raw_target = action_target.strip()
                img_name, flag = (raw_target.split('/') + [None])[:2] if '/' in raw_target else (raw_target, None)
                # 🟢 关键修改：如果你的图都在 imgs 文件夹里，这里要补上
                # 这样路径就会变成 ZhuXian\imgs\mission_bar\201Ice.png
                full_img_path = self.get_full_path(os.path.join("imgs", "actions", img_name))
                final_arg = f"{full_img_path}/{flag}" if flag else full_img_path
                interrupted = self.run_script_safe(script_path, next_stop_img, arg=final_arg)

            elif action_type == 'PLAY_JSON':
                script_path = os.path.join(self.project_root, "core", "shubiaozuobiaobofang.py")
                json_file = action_target.strip() if action_target.endswith(
                    ".json") else action_target.strip() + ".json"
                full_json_path = self.get_full_path(os.path.join("imgs", "tools", json_file))
                interrupted = self.run_script_safe(script_path, next_stop_img, arg=full_json_path)


            elif action_type == 'AUTO_RUN':
                script_path = os.path.join(self.project_root, "core", "zxsj11zhidongxunlu.py")
                # 拆分参数
                parts = action_target.strip().split('/')
                img_name = parts[0].strip()
                other_args = "/".join(parts[1:]) if len(parts) > 1 else ""
                # 🟢 关键修改：强制指向 imgs/actions 文件夹
                full_img_path = self.get_full_path(os.path.join("imgs", "actions", img_name))
                final_arg = f"{full_img_path}/{other_args}" if other_args else full_img_path
                interrupted = self.run_script_safe(script_path, next_stop_img, arg=final_arg)

            elif action_type == 'AUTO_RIGHT_CLICK':
                script_path = os.path.join(self.project_root, "core", "zxsjditu11.py")
                # 补全路径 (这里逻辑是对的，指向 imgs/actions)
                full_img_path = self.get_full_path(os.path.join("imgs", "actions", action_target))
                # 🟢 修正：确保这里传入的是上面定义的 script_path
                interrupted = self.run_script_safe(script_path, next_stop_img, arg=full_img_path)

            elif action_type == 'PLAY_RIGHT':
                script_path = os.path.join(self.project_root, "core", "shubiaozuobiaobofang11.py")
                json_file = action_target.strip() if action_target.endswith(
                    ".json") else action_target.strip() + ".json"
                full_json_path = self.get_full_path(os.path.join("imgs", "tools", json_file))
                interrupted = self.run_script_safe(script_path, next_stop_img, arg=full_json_path)

            elif action_type == 'SEQUENCE':
                print(f"      🔗 链接到子序列: {os.path.basename(action_target)}")
                self.execute_sequence_logic(action_target, next_stop_img)

            elif action_type == 'CLICK':
                self.execute_click(action_target)

            if interrupted:
                print("   ✨ (步骤中) 发现下一关，序列终止。")
                return

            if idx < len(steps) - 1:
                print("   💤 等待 3 秒...", end="\r")
                for _ in range(30):
                    time.sleep(0.1)
                    if next_stop_img and self.check_state(next_stop_img):
                        print("\n   ✨ (等待中) 发现下一关！")
                        return
                print("")

    def auto_locate_start_point(self):
        """自动扫描进度"""
        print("🔍 正在扫描当前进度...")
        for i, task in enumerate(self.tasks):
            if self.check_state(task['state_img']):
                print(f"📍 定位成功！从第 {i + 1} 步开始")
                return i
        print("❓ 未找到匹配状态，从第 1 步开始")
        return 0

    def select_start_task(self):
        """手动选关菜单"""
        print("\n============= 任务选关 =============")
        for index, task in enumerate(self.tasks):
            print(f"[{index + 1}] {task['description']}")
        print("===================================")
        print("👉 请输入序号 (例如 2)，或直接按 [回车] 自动扫描")

        user_input = input("你的选择: ").strip()
        if not user_input: return self.auto_locate_start_point()
        try:
            idx = int(user_input) - 1
            if 0 <= idx < len(self.tasks):
                print(f"✅ 已手动锁定：从第 {idx + 1} 步开始！")
                return idx
            else:
                return self.auto_locate_start_point()
        except ValueError:
            return self.auto_locate_start_point()

    def start(self, start_step=None):
        print("===================================")
        print("   ZXSJ 智能引擎 V8.1 (分支增强版)")
        print("===================================")

        if start_step is not None:
            try:
                i = int(start_step)
                print(f"⚡ 接收到自动指令，直接从第 {i + 1} 步启动！")
            except:
                i = self.select_start_task()
        else:
            i = self.select_start_task()

        while i < len(self.tasks):
            task = self.tasks[i]
            raw_time = task.get('timeout', '360')
            task_timeout = int(raw_time) if raw_time.isdigit() else 360

            print(f"\nTask [{i + 1}]: {task['description']} (⏱️ 限时: {task_timeout}秒)")

            state_imgs = task['state_img'].split('|')
            action_targets = task['action_target'].split('|')

            next_img = self.tasks[i + 1]['state_img'].split('|')[0] if i + 1 < len(self.tasks) else None
            final_target = None

            if len(state_imgs) > 1:
                print("   🔀 进入分支模式...")
                idx, _ = self.wait_for_multi_state(state_imgs, timeout=task_timeout)
                if idx == -1: break
                final_target = action_targets[idx] if idx < len(action_targets) else action_targets[0]
            else:
                if not self.wait_for_state_image(state_imgs[0], timeout=task_timeout): break
                final_target = action_targets[0]

            time.sleep(2)
            action_type = task['action_type']
            interrupted = False

            if action_type == 'SEQUENCE':
                print(f"   🚀 执行分支序列: {os.path.basename(final_target)}")
                self.execute_sequence_logic(final_target, next_img, global_timeout=task_timeout)


            elif action_type == 'AUTO_F':

                script_path = os.path.join(self.project_root, "core", "zxsjFFocr.py")

                full_img_path = self.get_full_path(final_target)

                interrupted = self.run_script_safe(script_path, next_img, timeout=task_timeout, arg=full_img_path)


            elif action_type == 'CLICK':

                self.execute_click(final_target)

                # ====================================================

                # 🟢 新增指令：循环直到等级达标

                # ====================================================

            elif action_type == 'LOOP_UNTIL_LV':

                try:

                    # 1. 解析参数

                    raw_params = final_target.split(',')

                    if len(raw_params) < 4:
                        print(f"❌ 参数不足！这一行需要4个参数，当前: {len(raw_params)}")

                        # 跳过这一行，防止卡死

                        i += 1

                        continue

                    target_lv = int(raw_params[0])  # 目标等级

                    json_open = raw_params[1].strip()  # 打开C

                    json_close = raw_params[2].strip()  # 关闭C

                    json_farm = raw_params[3].strip()  # 练级动作

                    print(f"   🔄 [循环挂机] 目标: {target_lv}级 | 动作: {json_farm}")

                    player_script = os.path.join(self.project_root, "core", "bofangqi.py")

                    while True:

                        # --- A. 打开面板 ---

                        print("      📂 1. 打开面板...")

                        full_open = self.get_full_path(json_open)

                        self.run_script_safe(player_script, next_img, timeout=task_timeout, arg=full_open)

                        time.sleep(2.0)  # 等动画

                        # --- B. 看一眼 ---

                        current_lv = detect_level_once()

                        print(f"      👀 2. 识别结果: {current_lv} 级 (目标 {target_lv})")

                        # --- C. 关闭面板 ---

                        print("      CX 3. 关闭面板...")

                        full_close = self.get_full_path(json_close)

                        self.run_script_safe(player_script, next_img, timeout=task_timeout, arg=full_close)

                        time.sleep(1.0)

                        # --- D. 决断 ---

                        if current_lv >= target_lv and current_lv > 0:
                            print(f"      🎉 恭喜！到达 {target_lv} 级，跳出循环！")

                            break  # 🟢 成功！跳出死循环

                        # --- E. 没到等级，去刷一轮 ---

                        print(f"      ⚔️ 等级不足，去刷一轮副本...")

                        full_farm = self.get_full_path(json_farm)

                        if json_farm.endswith('.json'):

                            self.run_script_safe(player_script, next_img, timeout=task_timeout, arg=full_farm)

                        else:

                            self.run_script_safe(full_farm, next_img, timeout=task_timeout)

                        print("      💤 休息3秒准备下一轮检查...")

                        time.sleep(3)


                except Exception as e:

                    print(f"❌ LOOP指令出错: {e}")

                    break


            elif action_type == 'JSON':

                player_script = os.path.join(self.project_root, "core", "bofangqi.py")

                full_json_path = self.get_full_path(final_target)

                interrupted = self.run_script_safe(player_script, next_img, timeout=task_timeout, arg=full_json_path)


            elif action_type == 'SCRIPT':

                interrupted = self.run_script_safe(final_target, next_img, timeout=task_timeout)

            print("   ✅ 本级任务结束，准备下一级。")

            i += 1

            time.sleep(3)


if __name__ == "__main__":
    GameEngine(game_name='ZhuXian', task_file='tasks.csv').start()