import sys
import os
# 👇 这句话是告诉Python：去上一级文件夹找找看
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 👇 然后才是你的导入代码
from Main_Engine import GameEngine

print("❄️ 正在加载冰霜副本任务表...")
# 注意：这里 CSV 就在根目录，所以直接写名字，不用加 ../
GameEngine("tasks_ice.csv").start(start_step=0)