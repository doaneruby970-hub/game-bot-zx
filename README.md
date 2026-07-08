# Game Bot ZX -- 诛仙手游自动化脚本

基于图像识别（OpenCV）与虚拟键鼠驱动（pydirectinput）的**诛仙手游（ZXSJ / 朱仙世界）**全自动挂机脚本套件。支持主线任务自动跑图、副本循环刷级、多角色切换练级、宏录制回放、智能寻路导航等功能。

## 功能特性

- **CSV 任务引擎** -- 通过 CSV 表格编排任务流水线，每一步由"屏幕截图匹配触发"+"动作执行"组成，支持分支跳转和超时控制
- **多角色自动练级** -- Master 主控模块按等级目标循环刷 12 级 / 30 级副本，完成后自动换号（默认 3 个角色）
- **图像识别点击** -- 在屏幕上查找目标图片并自动点击（左键 / 右键 / 按 F 键），支持限时轮询和循环模式
- **OCR 等级识别** -- 基于 Tesseract 截取角色等级区域进行数字 OCR，用于等级判断和挂机循环终止条件
- **智能自动寻路** -- OpenCV 模板匹配追踪目标菱形标记，扇形区域算法控制前进 / 转向，配合虚拟键盘实现自动跑图
- **万能操作录制器** -- 录制完整的鼠标移动、点击、键盘按键、滚轮事件为 JSON 文件，精确到毫秒级时间戳
- **鼠标坐标录制器** -- 录制屏幕坐标点（眼睛 -> 脸部拖拽 / 单点右键），用于捏脸、拖拽等需要精确坐标的操作
- **JSON 宏回放** -- 精确按时间戳回放录制的操作序列，支持虚拟键盘模式和 Arduino 硬件模式两种驱动
- **虚拟键盘模式** -- 纯软件方案，无需 Arduino 硬件即可运行，兼容原有硬件串口协议接口
- **游戏窗口管理** -- 按进程名查找并置顶 / 移动游戏窗口
- **拟人化鼠标轨迹** -- 三次贝塞尔曲线 + Quintic Ease Out 变速算法模拟真人鼠标甩动
- **可视化调试窗口** -- 寻路模块提供 OpenCV 实时监视窗，显示目标框、扇形导航线、状态文字

## 项目结构

```
game-bot-zx/
├── GameBot/
│   ├── Master.py                          # 主控脚本：多角色循环练级
│   ├── core/                              # 核心引擎与工具模块
│   │   ├── Main_Engine.py                 # CSV 任务执行引擎
│   │   ├── bofangqi.py                    # JSON 宏回放器（虚拟键盘版）
│   │   ├── zxsj11zhidongxunlu.py          # 智能自动寻路（虚拟键盘版）
│   │   ├── zxsj22ocr.py                   # 识图 + 左键点击
│   │   ├── zxsj33ocr.py                   # 识图 + 按 F 键
│   │   ├── zxsjFFocr.py                   # 识图 + 循环按 F
│   │   ├── zxsjditu11.py                  # 小地图区域识图 + 右键点击（720p 专用）
│   │   ├── shibiedengji.py                # OCR 等级识别
│   │   ├── shubiaozuobiaobofang.py        # 捏脸拖拽播放器
│   │   ├── shubiaozuobiaobofang11.py      # 右键坐标播放器
│   │   └── ArduinoKeyboard.py             # Arduino 硬件键盘类（已被虚拟键盘替代）
│   └── ZhuXian/                           # 诛仙游戏专属资源
│       ├── tasks.csv                      # 主线任务表
│       ├── tasks_12.csv                   # 12级副本任务表
│       ├── tasks_30.csv                   # 30级副本任务表
│       ├── tasks_ice.csv                  # 冰霜副本任务表
│       ├── tasks_fire.csv                 # 火焰副本任务表
│       ├── tasks_logout.csv               # 退出/换号任务表
│       ├── seqs/                          # 动作序列 .txt 文件
│       ├── scripts/                       # 游戏专属启动脚本
│       │   ├── run_ice.py
│       │   ├── run_fire.py
│       │   └── run_25.py
│       └── imgs/                          # 游戏截图资源（mission_bar, actions, tools 等）
├── wannengluzhiqi.py                      # 万能操作录制器
├── 29luzhi.py                             # 新版录制器（pynput 相对位移式）
├── 29bofang.py                            # 新版回放器
├── shubiaozuobiaoluzhi.py                 # 捏脸坐标录制器（眼 + 脸）
├── zhubiaozuobiaoluzhi11.py               # 右键单点坐标录制器
├── shubiaozuobiaobofang.py                # 捏脸拖拽回放器（旧版 Arduino）
├── shubiaozuobiaobofang11.py              # 右键坐标回放器（旧版 Arduino）
├── zxsjshubiaohengyi.py                   # Arduino 精确角度转向
├── zxsj22lengxingzhuizhong.py             # Arduino 菱形追踪寻路（旧版）
├── zxsj11zhidongxunlu.py                  # 自动寻路（旧版独立脚本）
├── zxsjsditu11.py                         # 小地图识图点击（1080p 自适应缩放版）
├── ZXSJ22ocr.py                           # 识图点击（诊断调试版）
├── ZXSJ22ocr——1.py                        # OCR+识图流水线框架示例
├── ZXSJAAAAManager.py                     # 热键管理器（PageUp 启动 / PageDown 停止）
├── ZCSJ1OCR.py                            # 二值化图片匹配函数
├── ArduinoKeyboard.py                     # 独立虚拟键盘类（完整版）
├── xunijianpan.py                         # 虚拟按键简单示例
├── xunijianpan.py111.py                   # 虚拟按键示例备份
├── HumanMovement.py                       # 拟人化贝塞尔鼠标移动
├── LG.py                                  # 游戏窗口查找与置顶
├── Level_Monitor.py                       # 等级区域调试工具
├── shibiedengji.py                        # 等级识别（顶层级联副本）
├── requirements.txt                       # Python 依赖清单
└── README.md
```

## 环境要求

- Windows 10 / 11（需要管理员权限运行）
- Python 3.10+
- Tesseract OCR（需单独安装，默认路径 `E:\OCR\tesseract.exe`）
- 屏幕分辨率：1280x720（部分模块适配 1920x1080）
- 游戏客户端：诛仙手游 PC 版

## 安装

```bash
git clone https://github.com/doaneruby970-hub/game-bot-zx.git
cd game-bot-zx
pip install -r requirements.txt
```

### 安装 Tesseract OCR

等级识别功能依赖 Tesseract OCR 引擎：

1. 从 https://github.com/UB-Mannheim/tesseract/wiki 下载 Windows 安装包
2. 安装到 `E:\OCR\` 目录，确保 `E:\OCR\tesseract.exe` 存在
3. 或者修改 `shibiedengji.py` 中的 `pytesseract.tesseract_cmd` 路径

## 配置

### 任务表格式（CSV）

任务表位于 `GameBot/ZhuXian/` 目录下，格式如下：

| 列名 | 说明 |
|------|------|
| `id` | 任务编号 |
| `description` | 任务描述 |
| `state_img` | 触发条件：屏幕截图路径，多个用 `\|` 分隔表示分支 |
| `action_type` | 动作类型：`SEQUENCE` / `JSON` / `SCRIPT` / `AUTO_F` / `AUTO_CLICK` / `AUTO_RUN` / `AUTO_RIGHT_CLICK` / `PLAY_JSON` / `PLAY_RIGHT` / `CLICK` / `LOOP_UNTIL_LV` |
| `action_target` | 动作目标：序列文件 / JSON 文件 / 脚本路径 / 图片路径 |
| `timeout` | 超时时间（秒），可选，默认 360 |

### 序列文件格式（TXT）

每行一个动作：`动作类型|参数`

支持类型：`JSON`、`SCRIPT`、`AUTO_F`、`AUTO_CLICK`、`AUTO_RUN`、`AUTO_RIGHT_CLICK`、`PLAY_JSON`、`PLAY_RIGHT`、`SEQUENCE`、`CLICK`

### 游戏截图准备

所有图像识别依赖预先截取的游戏 UI 截图，需放置到 `GameBot/ZhuXian/imgs/` 对应子目录下：
- `imgs/mission_bar/` -- 任务进度图标
- `imgs/actions/` -- 动作触发图标（菱形标记、NPC 名称、按钮等）
- `imgs/tools/` -- 工具类坐标 JSON 文件

## 使用方式

### 1. 全自动多角色练级（推荐入口）

```bash
# 以管理员身份运行
python GameBot/Master.py
```

脚本启动后有 3 秒切换窗口时间。自动流程：
1. 循环 3 个角色
2. 每个角色先跑 12 级副本直到到达目标等级
3. 再跑 30 级副本
4. 完成后自动换号

### 2. 单独跑某个副本

```bash
# 主线任务
python GameBot/core/Main_Engine.py

# 冰霜副本
python GameBot/ZhuXian/scripts/run_ice.py

# 火焰副本
python GameBot/ZhuXian/scripts/run_fire.py

# 25级副本
python GameBot/ZhuXian/scripts/run_25.py
```

### 3. 录制操作宏

```bash
# 新版录制器（pynput，记录相对位移）
python 29luzhi.py
# PageUp 开始 / PageDown 结束 -> 输入文件名保存到 quests/

# 旧版录制器（pyautogui，记录绝对坐标）
python wannengluzhiqi.py
# PageUp 开始 / PageDown 结束 -> 输入文件名保存到 quests/
```

### 4. 回放操作宏

```bash
python 29bofang.py
# 从 quests/ 目录列表中选择文件回放
```

### 5. 录制屏幕坐标点

```bash
# 捏脸拖拽（记录眼睛 + 脸部两点）
python shubiaozuobiaoluzhi.py

# 单点右键（记录一个点击位置）
python zhubiaozuobiaoluzhi11.py
```

## 任务引擎工作流程

```
CSV 任务表加载
  -> 对每一行任务：
     1. 等待 state_img 在屏幕上出现（超时则终止）
     2. 支持多图片分支（| 分隔）：哪个先出现就执行哪个分支
     3. 根据 action_type 执行对应动作：
        - SEQUENCE: 递归解析 .txt 序列文件
        - JSON: 调用 bofangqi.py 播放 JSON 宏
        - SCRIPT: subprocess 启动独立 Python 脚本
        - AUTO_F/AUTO_CLICK/AUTO_RUN: 带参数调用对应子模块
        - LOOP_UNTIL_LV: 循环刷副本直到 OCR 检测等级达标
     4. 在执行过程中持续监控 next_stop_img（下一关的触发图）
        -> 如果出现则立即中断当前动作，进入下一关
     5. 完成当前任务，继续下一个
```

## 自动寻路算法

使用 OpenCV 模板匹配在屏幕上追踪目标（菱形标记），计算目标位置与屏幕中心的偏移：

- **扇形前方区域** -- 目标在人物前方且偏角在扇形范围内：按住 W 前进 + 微调转向
- **扇形外侧** -- 目标在视野内但偏角过大：松开 W，仅转向对准
- **身后区域** -- 目标在人物身后（屏幕下方）：松开 W，大角度转向
- **到达判断** -- 目标距离进入停止半径范围或检测到 finish.png

## 注意事项

1. **必须管理员权限** -- pydirectinput 在部分游戏中需要管理员权限才能发送输入
2. **屏幕分辨率** -- 部分模块硬编码 1280x720 参数，请确认游戏窗口分辨率匹配
3. **Tesseract 路径** -- 默认 OCR 引擎路径为 `E:\OCR\tesseract.exe`，需按实际安装路径修改
4. **截图依赖** -- 所有图像识别功能依赖预先截取的 UI 截图，更换分辨率或游戏版本后需重新截图
5. **串口号** -- 如果使用 Arduino 硬件模式，默认串口为 `COM5`
6. **切勿遮挡游戏窗口** -- 图像识别依赖实时截屏，游戏窗口不能被其他窗口遮挡
7. **停止热键** -- 大部分脚本支持 PageDown / Q / PageUp 作为启动 / 停止控制
8. **多开风险** -- 自动脚本行为可能违反游戏用户协议，请自行评估使用风险
