import time
import os
import sys
import pydirectinput
import pyautogui
import ctypes

# ================= 1. 基础设置 =================
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CORE_PATH = os.path.join(CURRENT_DIR, "core")
if CORE_PATH not in sys.path:
    sys.path.append(CORE_PATH)

try:
    from Main_Engine import GameEngine
    from shibiedengji import detect_level_once
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)

# 定义需要检查的图片路径（请替换为实际文件名）
TARGET_IMAGES = [
    os.path.join(CURRENT_DIR, "ZhuXian", "imgs", "actions", "XXX.png"),
    os.path.join(CURRENT_DIR, "ZhuXian", "imgs", "actions", "XXX1.png")
]


# ================= 2. 核心按键工具 =================

def press_ctrl_hardcore(duration=0.2):
    """ 使用 Windows API 发送强力 Ctrl 信号 """
    # 0x11 是虚拟键码 VK_CONTROL
    ctypes.windll.user32.keybd_event(0x11, 0, 0, 0)  # 按下
    time.sleep(duration)
    ctypes.windll.user32.keybd_event(0x11, 0, 2, 0)  # 弹起


# ================= 3. 功能函数 =================

def check_level_active():
    """ 主动按C查等级 """
    print("   📋 [Master] 检查等级中...")
    pydirectinput.press('c')
    time.sleep(2.0)
    lv = detect_level_once()
    print(f"   🧐 [Master] 识别结果: {lv} 级")
    pydirectinput.press('c')
    time.sleep(1.0)
    return lv


def find_any_target():
    """ 内部辅助：寻找列表中的任意一张图，找到则返回中心坐标，否则返回 None """
    for img_path in TARGET_IMAGES:
        if not os.path.exists(img_path):
            continue
        try:
            # 这里的 confidence 可以根据实际识别效果微调
            box = pyautogui.locateOnScreen(img_path, confidence=0.7, grayscale=True)
            if box:
                return pyautogui.center(box)
        except Exception:
            pass
    return None


def check_and_click_special_status():
    """
    逻辑：
    1. 2次5秒轮询确认是否有图片。
    2. 若有：呼出鼠标 -> 进入循环点击(直到识别不到) -> 关闭鼠标。
    """
    print("   🔍 [Master] 开始状态识别 (初始轮询)...")
    found_pos = None

    # --- 阶段 A: 初始轮询 (2次 5秒间隔) ---
    for i in range(2):
        print(f"      - 第 {i + 1} 次寻找目标图片...")
        found_pos = find_any_target()
        if found_pos:
            break
        if i == 0:
            time.sleep(5)

    # --- 阶段 B: 循环点击过程 ---
    if found_pos:
        print("   💡 识别到目标！执行强力模式呼出鼠标并开启循环点击...")
        press_ctrl_hardcore(0.2)  # 呼出鼠标
        time.sleep(0.5)

        click_count = 0
        while True:
            # 再次确认图片是否还在（每一轮点击前都重新找一次，确保位置准确）
            current_pos = find_any_target()

            if current_pos:
                click_count += 1
                pydirectinput.moveTo(int(current_pos.x), int(current_pos.y))
                pydirectinput.click()
                print(f"      🖱️ 点击第 {click_count} 次，坐标: ({int(current_pos.x)}, {int(current_pos.y)})")
                # 等待游戏 UI 刷新，如果点击后消失得慢，可以稍微调大这个值
                time.sleep(0.8)
            else:
                print("   ✅ 屏幕上已无目标图片，退出点击循环。")
                break

            # 安全阀：防止因为识别错误导致死循环（可选）
            if click_count > 10:
                print("   ⚠️ 警告：点击次数过多，可能识别异常，强制停止。")
                break

        time.sleep(0.5)
        print("   💡 执行强力模式关闭鼠标...")
        press_ctrl_hardcore(0.2)  # 关闭鼠标
        time.sleep(1.0)
        return True
    else:
        print("   ✅ [Master] 未识别到目标，跳过此步骤。")
        return False


# ================= 4. 运行逻辑 =================

def run_stage(game_name, csv_file, target_level):
    """ 通用阶段运行器 """
    print(f"\n⚡ [启动阶段] 加载任务: {csv_file} | 目标: {target_level} 级")
    while True:
        # 1. 检查等级
        current_lv = check_level_active()

        # 2. 判断是否换本
        if current_lv > 0 and current_lv >= target_level:
            print(f"🎉 目标达成：{current_lv}级 >= {target_level}级")
            break

        # 3. 识图判定（只要有图就一直点，直到没图）
        check_and_click_special_status()

        # 4. 运行副本流程
        print(f"⚔️ 等级未到，执行副本: {csv_file}")
        engine = GameEngine(game_name=game_name, task_file=csv_file)
        engine.start(start_step=0)

        print("💤 本轮结束，休息 20 秒...")
        time.sleep(20)


def main():
    GAME_NAME = "ZhuXian"
    for i in range(1, 4):
        print(f"\n################ 正在挂第 {i} 个角色 ################")
        # 第一阶段：12级副本 -> 目标 30级
        run_stage(GAME_NAME, "tasks_12.csv", 30)
        time.sleep(5)
        # 第二阶段：30级副本 -> 目标 45级
        run_stage(GAME_NAME, "tasks_30.csv", 30)

        print(f"✅ 第 {i} 个角色完成！换号...")
        GameEngine(game_name=GAME_NAME, task_file="tasks_logout.csv").start(start_step=0)
        time.sleep(20)


if __name__ == "__main__":
    print("⏳ 脚本已启动！请在 3 秒内切换到游戏窗口...")
    time.sleep(3)
    main()