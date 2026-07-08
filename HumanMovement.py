import time
import random
import math


class HumanMouse:
    def __init__(self, arduino_kb):
        self.kb = arduino_kb

    def get_point_on_bezier(self, t, p0, p1, p2, p3):
        """计算三次贝塞尔曲线上的点"""
        u = 1 - t
        tt = t * t
        uu = u * u
        uuu = uu * u
        ttt = tt * t

        p = uuu * p0
        p += 3 * uu * t * p1
        p += 3 * u * tt * p2
        p += ttt * p3
        return p

    def move_human_like(self, total_dx, total_dy, duration=0.3):
        """
        拟人化移动 V3.0 (丝滑版)
        解决“卡顿”问题，提高采样率，去除强制阈值
        """
        # 1. 设置起点和终点
        start_x, start_y = 0, 0
        target_x, target_y = total_dx, total_dy

        # 2. 生成随机控制点
        # 减小偏移量，让线条更直一点，减少画圈感，提高响应速度
        offset = abs(total_dx) * 0.2 + abs(total_dy) * 0.2 + 20

        c1_x = start_x + (target_x - start_x) * 0.2 + random.uniform(-offset, offset)
        c1_y = start_y + (target_y - start_y) * 0.2 + random.uniform(-offset, offset)

        c2_x = start_x + (target_x - start_x) * 0.8 + random.uniform(-offset, offset)
        c2_y = start_y + (target_y - start_y) * 0.8 + random.uniform(-offset, offset)

        # 3. 提高采样率 (关键修改！)
        # 之前的 50 太低了，会导致卡顿。现在用 100~150，让动作更细腻
        # 如果 duration 是 0.5秒，steps=100 意味着每 5毫秒发一次指令，非常丝滑
        steps = int(duration * 120)
        if steps < 20: steps = 20

        current_x, current_y = 0, 0

        # 小数累积池（用于保存小于1像素的微动）
        remainder_x = 0.0
        remainder_y = 0.0

        for i in range(steps + 1):
            t = i / steps

            # 变速算法：使用更自然的 Quintic Ease Out (快速启动，极慢结束)
            # 这种曲线在 FPS 游戏里最像真人甩鼠标
            t_eased = 1 - pow(1 - t, 5)

            # 计算目标点
            px = self.get_point_on_bezier(t_eased, start_x, c1_x, c2_x, target_x)
            py = self.get_point_on_bezier(t_eased, start_y, c1_y, c2_y, target_y)

            # 计算这一帧的理论增量
            delta_x = px - current_x
            delta_y = py - current_y

            # 加入累积池
            remainder_x += delta_x
            remainder_y += delta_y

            # === V3.0 核心：只要满 1 像素就发，不再等待 3 像素 ===
            to_send_x = int(remainder_x)
            to_send_y = int(remainder_y)

            # 如果有整数移动，就发送
            if to_send_x != 0 or to_send_y != 0:
                self.kb.move_relative(to_send_x, to_send_y)

                # 更新当前物理位置
                current_x += to_send_x
                current_y += to_send_y

                # 从累积池里减去已发送的整数部分，保留小数
                remainder_x -= to_send_x
                remainder_y -= to_send_y

            # === 核心：极短的休眠 ===
            # 不要让 Arduino 缓冲区溢出，但也要足够快
            frame_time = duration / steps

            # 如果这一帧没有移动（to_send == 0），我们可以 skip sleep 或者 sleep 更短
            # 这里为了保持节奏稳定，还是 sleep，但加入极微小的随机
            time.sleep(frame_time + random.uniform(0, 0.001))

        # 4. 补齐误差 (必须执行)
        final_x = int(target_x - current_x + remainder_x)
        final_y = int(target_y - current_y + remainder_y)

        if final_x != 0 or final_y != 0:
            self.kb.move_relative(final_x, final_y)

class HumanMovement:
            @staticmethod
            def move_to(board, x, y, duration=0.3):
                mouse = HumanMouse(board)
                mouse.move_human_like(x, y, duration)
