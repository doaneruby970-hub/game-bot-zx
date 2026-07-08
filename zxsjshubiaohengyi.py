from ArduinoKeyboard import ArduinoKeyboard
import time


def main():
    print("========== 程序启动 ==========")

    # 1. 连接 Arduino
    bot = ArduinoKeyboard(port="COM5")
    time.sleep(1)

    print("Arduino 已连接")
    print("请输入指令：")
    print("R = 右转 90°")
    print("L = 左转 90°")
    print("Q = 退出程序")

    while True:
        cmd = input("\n请输入指令并回车：").strip().upper()

        if cmd == "Q":
            print("退出程序")
            break

        if cmd not in ("R", "L"):
            print("无效指令，请输入 R / L / Q")
            continue

        print("指令已接收，3 秒后执行，请切回游戏窗口...")
        time.sleep(3)

        if cmd == "R":
            print("执行：右转 90°")
            bot.turn_precise_angle(90)

        elif cmd == "L":
            print("执行：左转 90°")
            bot.turn_precise_angle(-90)

        print("转向完成，等待下一条指令")


# ==================================================
# 程序入口
# ==================================================
if __name__ == "__main__":
    main()
