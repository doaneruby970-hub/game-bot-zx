import sys
import os

# 1. 自动定位路径
current_script = os.path.abspath(__file__)
scripts_dir = os.path.dirname(current_script)
zhuxian_dir = os.path.dirname(scripts_dir)
project_root = os.path.dirname(zhuxian_dir)

# 2. 将 core 加入系统路径
core_path = os.path.join(project_root, "core")
if core_path not in sys.path:
    sys.path.append(core_path)

# 3. 导入引擎
try:
    from Main_Engine import GameEngine
except ImportError:
    print(f"❌ 导入失败！请检查: {core_path}")
    sys.exit(1)


def main():
    print("❄️ [子进程] 正在启动冰霜副本自动化流程...")

    # 4. 初始化引擎
    # game_name 决定了去哪里找图，task_file 决定了跑哪个表
    engine = GameEngine(game_name="ZhuXian", task_file="tasks_ice.csv")

    # 5. 【核心修复】调用 start 并传入 0
    # 这样它就会直接跳过“请输入序号”的菜单，直接跑第 1 行任务
    engine.start(start_step=0)


if __name__ == "__main__":
    main()