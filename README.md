# Game Bot ZX -- ZhuXian Mobile Game Automation Script

An **automated botting suite** for the **ZhuXian Mobile Game (ZXSJ)** based on image recognition (OpenCV) and virtual keyboard/mouse drivers (pydirectinput). Supports main quest auto-navigation, dungeon looping for leveling, multi-character switching and leveling, macro recording and playback, intelligent pathfinding, and more.

## Features

- **CSV Task Engine** -- Orchestrates task pipelines via CSV tables. Each step consists of "screenshot match trigger" + "action execution," supporting conditional branching and timeout control.
- **Multi-Character Auto-Leveling** -- The Master controller module cycles through level 12 and level 30 dungeons based on level targets, automatically switching characters once done (default 3 characters).
- **Image-Recognition Clicking** -- Searches for target images on screen and auto-clicks (left-click / right-click / press F key), supporting timed polling and looping modes.
- **OCR Level Recognition** -- Uses Tesseract to capture character level regions for numeric OCR, used as level judgment and loop termination conditions.
- **Intelligent Auto-Pathfinding** -- OpenCV template matching tracks target diamond markers; a fan-zone algorithm controls forward movement / turning, combined with virtual keyboard for auto-navigation.
- **Universal Action Recorder** -- Records complete mouse movement, clicks, keyboard presses, and scroll events into JSON files with millisecond-precision timestamps.
- **Mouse Coordinate Recorder** -- Records screen coordinate points (eye -> face drag / single right-click) for face-customization, dragging, and other precision-coordinate operations.
- **JSON Macro Playback** -- Precisely replays recorded action sequences by timestamp, supporting both virtual keyboard mode and Arduino hardware mode.
- **Virtual Keyboard Mode** -- Pure software solution; runs without Arduino hardware while remaining compatible with the existing hardware serial protocol interface.
- **Game Window Management** -- Finds and brings to front / moves the game window by process name.
- **Human-like Mouse Trajectory** -- Cubic Bezier curves + Quintic Ease Out speed variation to simulate natural human mouse movement.
- **Visual Debug Window** -- Pathfinding module provides a real-time OpenCV monitor window showing target bounding boxes, fan-shaped navigation guides, and status text.

## Project Structure

```
game-bot-zx/
├── GameBot/
│   ├── Master.py                          # Master script: multi-character cycling leveling
│   ├── core/                              # Core engine and utility modules
│   │   ├── Main_Engine.py                 # CSV task execution engine
│   │   ├── bofangqi.py                    # JSON macro player (virtual keyboard edition)
│   │   ├── zxsj11zhidongxunlu.py          # Intelligent auto-pathfinding (virtual keyboard edition)
│   │   ├── zxsj22ocr.py                   # Image recognition + left-click
│   │   ├── zxsj33ocr.py                   # Image recognition + press F key
│   │   ├── zxsjFFocr.py                   # Image recognition + loop press F
│   │   ├── zxsjditu11.py                  # Minimap region image recognition + right-click (720p specific)
│   │   ├── shibiedengji.py                # OCR level recognition
│   │   ├── shubiaozuobiaobofang.py        # Face-customization drag player
│   │   ├── shubiaozuobiaobofang11.py      # Right-click coordinate player
│   │   └── ArduinoKeyboard.py             # Arduino hardware keyboard class (replaced by virtual keyboard)
│   └── ZhuXian/                           # ZhuXian game-specific resources
│       ├── tasks.csv                      # Main quest task table
│       ├── tasks_12.csv                   # Level 12 dungeon task table
│       ├── tasks_30.csv                   # Level 30 dungeon task table
│       ├── tasks_ice.csv                  # Ice dungeon task table
│       ├── tasks_fire.csv                 # Fire dungeon task table
│       ├── tasks_logout.csv               # Logout / character switch task table
│       ├── seqs/                          # Action sequence .txt files
│       ├── scripts/                       # Game-specific launcher scripts
│       │   ├── run_ice.py
│       │   ├── run_fire.py
│       │   └── run_25.py
│       └── imgs/                          # Game screenshot assets (mission_bar, actions, tools, etc.)
├── wannengluzhiqi.py                      # Universal action recorder
├── 29luzhi.py                             # New recorder (pynput relative-motion edition)
├── 29bofang.py                            # New player
├── shubiaozuobiaoluzhi.py                 # Face-customization coordinate recorder (eye + face)
├── zhubiaozuobiaoluzhi11.py               # Right-click single-point coordinate recorder
├── shubiaozuobiaobofang.py                # Face-customization drag player (legacy Arduino edition)
├── shubiaozuobiaobofang11.py              # Right-click coordinate player (legacy Arduino edition)
├── zxsjshubiaohengyi.py                   # Arduino precision angle turning
├── zxsj22lengxingzhuizhong.py             # Arduino diamond-tracking pathfinding (legacy)
├── zxsj11zhidongxunlu.py                  # Auto-pathfinding (legacy standalone script)
├── zxsjsditu11.py                         # Minimap image recognition click (1080p adaptive scaling edition)
├── ZXSJ22ocr.py                           # Image recognition click (diagnostic debug edition)
├── ZXSJ22ocr——1.py                        # OCR + image recognition pipeline framework example
├── ZXSJAAAAManager.py                     # Hotkey manager (PageUp start / PageDown stop)
├── ZCSJ1OCR.py                            # Binary image matching functions
├── ArduinoKeyboard.py                     # Standalone virtual keyboard class (full edition)
├── xunijianpan.py                         # Virtual key simple example
├── xunijianpan.py111.py                   # Virtual key example backup
├── HumanMovement.py                       # Human-like Bezier mouse movement
├── LG.py                                  # Game window find & bring to front
├── Level_Monitor.py                       # Level region debug tool
├── shibiedengji.py                        # Level recognition (top-level cascaded copy)
├── requirements.txt                       # Python dependency list
└── README.md
```

## Requirements

- Windows 10 / 11 (requires administrator privileges)
- Python 3.10+
- Tesseract OCR (must be installed separately; default path `E:\OCR\tesseract.exe`)
- Screen resolution: 1280x720 (some modules adapted for 1920x1080)
- Game client: ZhuXian Mobile Game PC edition

## Installation

```bash
git clone https://github.com/doaneruby970-hub/game-bot-zx.git
cd game-bot-zx
pip install -r requirements.txt
```

### Installing Tesseract OCR

Level recognition depends on the Tesseract OCR engine:

1. Download the Windows installer from https://github.com/UB-Mannheim/tesseract/wiki
2. Install to `E:\OCR\` directory; ensure `E:\OCR\tesseract.exe` exists
3. Or modify the `pytesseract.tesseract_cmd` path in `shibiedengji.py`

## Configuration

### Task Table Format (CSV)

Task tables are located under `GameBot/ZhuXian/` with the following format:

| Column | Description |
|------|------|
| `id` | Task number |
| `description` | Task description |
| `state_img` | Trigger condition: screenshot path; multiple paths separated by `\|` indicate branches |
| `action_type` | Action type: `SEQUENCE` / `JSON` / `SCRIPT` / `AUTO_F` / `AUTO_CLICK` / `AUTO_RUN` / `AUTO_RIGHT_CLICK` / `PLAY_JSON` / `PLAY_RIGHT` / `CLICK` / `LOOP_UNTIL_LV` |
| `action_target` | Action target: sequence file / JSON file / script path / image path |
| `timeout` | Timeout in seconds, optional, default 360 |

### Sequence File Format (TXT)

One action per line: `action_type|parameter`

Supported types: `JSON`, `SCRIPT`, `AUTO_F`, `AUTO_CLICK`, `AUTO_RUN`, `AUTO_RIGHT_CLICK`, `PLAY_JSON`, `PLAY_RIGHT`, `SEQUENCE`, `CLICK`

### Game Screenshot Preparation

All image recognition relies on pre-captured game UI screenshots. Place them under the corresponding subdirectories in `GameBot/ZhuXian/imgs/`:
- `imgs/mission_bar/` -- Quest progress icons
- `imgs/actions/` -- Action trigger icons (diamond markers, NPC names, buttons, etc.)
- `imgs/tools/` -- Utility coordinate JSON files

## Usage

### 1. Fully-Automated Multi-Character Leveling (Recommended Entry Point)

```bash
# Run as Administrator
python GameBot/Master.py
```

The script starts with a 3-second window for you to switch to the game. Automated flow:
1. Cycles through 3 characters
2. Each character runs the level 12 dungeon until reaching the target level
3. Then runs the level 30 dungeon
4. Auto-switches character upon completion

### 2. Run a Single Dungeon

```bash
# Main quest
python GameBot/core/Main_Engine.py

# Ice dungeon
python GameBot/ZhuXian/scripts/run_ice.py

# Fire dungeon
python GameBot/ZhuXian/scripts/run_fire.py

# Level 25 dungeon
python GameBot/ZhuXian/scripts/run_25.py
```

### 3. Record Action Macros

```bash
# New recorder (pynput, records relative motion)
python 29luzhi.py
# PageUp to start / PageDown to end -> enter filename to save to quests/

# Legacy recorder (pyautogui, records absolute coordinates)
python wannengluzhiqi.py
# PageUp to start / PageDown to end -> enter filename to save to quests/
```

### 4. Play Back Action Macros

```bash
python 29bofang.py
# Select a file from the quests/ directory list for playback
```

### 5. Record Screen Coordinate Points

```bash
# Face-customization drag (records eye + face two-point)
python shubiaozuobiaoluzhi.py

# Single right-click (records one click position)
python zhubiaozuobiaoluzhi11.py
```

## Task Engine Workflow

```
CSV task table loaded
  -> For each task row:
     1. Wait for state_img to appear on screen (timeout triggers termination)
     2. Support multi-image branching (| separated): whichever appears first executes
     3. Execute the corresponding action based on action_type:
        - SEQUENCE: recursively parse .txt sequence file
        - JSON: call bofangqi.py to play JSON macro
        - SCRIPT: subprocess launch independent Python script
        - AUTO_F/AUTO_CLICK/AUTO_RUN: call corresponding submodules with parameters
        - LOOP_UNTIL_LV: loop dungeon until OCR detects level threshold reached
     4. During execution, continuously monitor next_stop_img (trigger image for next stage)
        -> If it appears, immediately interrupt current action and advance to next stage
     5. Complete current task, continue to next
```

## Auto-Pathfinding Algorithm

Uses OpenCV template matching to track targets (diamond markers) on screen, computing the offset between the target position and screen center:

- **Forward fan zone** -- Target is in front of the character and within the fan angle range: hold W to move forward + fine-tune steering
- **Outside fan zone** -- Target is visible but angular offset is too large: release W, turn only to align
- **Behind zone** -- Target is behind the character (lower portion of screen): release W, large-angle turn
- **Arrival check** -- Target distance falls within stopping radius or finish.png is detected

## Notes

1. **Administrator privileges required** -- pydirectinput needs admin rights to send input in some games
2. **Screen resolution** -- Some modules hardcode 1280x720 parameters; verify game window resolution matches
3. **Tesseract path** -- Default OCR engine path is `E:\OCR\tesseract.exe`; modify to match your actual installation path
4. **Screenshot dependency** -- All image recognition relies on pre-captured UI screenshots; re-capture is required after resolution or game version changes
5. **Serial port** -- If using Arduino hardware mode, default serial port is `COM5`
6. **Do not occlude the game window** -- Image recognition depends on real-time screen capture; the game window must not be covered by other windows
7. **Stop hotkeys** -- Most scripts support PageDown / Q / PageUp as start / stop controls
8. **Multi-instance risk** -- Automated script behavior may violate the game's terms of service; evaluate the risks yourself
