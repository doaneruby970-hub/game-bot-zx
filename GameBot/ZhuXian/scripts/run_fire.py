import sys
import os

current_script = os.path.abspath(__file__)
scripts_dir = os.path.dirname(current_script)
zhuxian_dir = os.path.dirname(scripts_dir)
project_root = os.path.dirname(zhuxian_dir)

core_path = os.path.join(project_root, "core")
if core_path not in sys.path:
    sys.path.append(core_path)

from Main_Engine import GameEngine


def main():
    print("🔥 [子进程] 正在启动火系副本自动化流程...")

    # 锁定火系任务表
    engine = GameEngine(game_name="ZhuXian", task_file="tasks_fire.csv")

    # 强制直接运行
    engine.start(start_step=0)


if __name__ == "__main__":
    main()