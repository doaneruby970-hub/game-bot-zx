# record_one_point.py
import json
import os
from pynput import mouse

DATA_DIR = "data"

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

print("请输入本次录制的文件名（不需要 .json）：")
file_name = input(">>> ").strip()
if not file_name:
    print("文件名不能为空，退出")
    exit()

save_path = os.path.join(DATA_DIR, file_name + ".json")

point = {}

def on_click(x, y, button, pressed):
    if pressed and button == mouse.Button.left:
        point["point"] = {"x": x, "y": y}
        print(f"已记录坐标: {point['point']}")
        return False  # 停止监听

print("程序启动")
print("请点击目标位置（左键一次）")

with mouse.Listener(on_click=on_click) as listener:
    listener.join()

with open(save_path, "w", encoding="utf-8") as f:
    json.dump(point, f, indent=2, ensure_ascii=False)

print(f"录制完成，已保存到 {save_path}")
