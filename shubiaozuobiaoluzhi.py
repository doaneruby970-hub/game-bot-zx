# record.py
import json
import time
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

points = {}
step = "eye"  # 当前录制阶段：eye -> face


def on_click(x, y, button, pressed):
    global step

    if pressed and button == mouse.Button.left:
        if step == "eye":
            points["eye"] = {"x": x, "y": y}
            print(f"已记录【眼睛】坐标: {points['eye']}")
            print("请点击【脸部目标】位置")
            step = "face"

        elif step == "face":
            points["face"] = {"x": x, "y": y}
            print(f"已记录【脸部】坐标: {points['face']}")
            return False  # 停止监听


print("程序启动")
print("请点击【眼睛】位置")

with mouse.Listener(on_click=on_click) as listener:
    listener.join()

with open(save_path, "w", encoding="utf-8") as f:
    json.dump(points, f, indent=2, ensure_ascii=False)

print(f"录制完成，已保存到 {save_path}")
