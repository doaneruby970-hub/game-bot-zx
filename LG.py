import psutil
import win32gui
import win32process
import win32con

TARGET_PROCESS = "AION2.exe"   # 如果不确定，等下我教你怎么看

def find_pids_by_name(name):
    pids = []
    for p in psutil.process_iter(['pid', 'name']):
        if p.info['name'] and p.info['name'].lower() == name.lower():
            pids.append(p.info['pid'])
    return pids

def find_windows_by_pid(pid):
    hwnds = []

    def callback(hwnd, _):
        try:
            _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
            if found_pid == pid and win32gui.IsWindowVisible(hwnd):
                hwnds.append(hwnd)
        except:
            pass

    win32gui.EnumWindows(callback, None)
    return hwnds

def move_window(hwnd):
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

    rect = win32gui.GetWindowRect(hwnd)
    w = rect[2] - rect[0]
    h = rect[3] - rect[1]

    result = win32gui.SetWindowPos(
        hwnd,
        win32con.HWND_TOP,
        0, 0,
        w, h,
        win32con.SWP_SHOWWINDOW
    )
    return result

# =================== 主流程 ===================

pids = find_pids_by_name(TARGET_PROCESS)

if not pids:
    print("❌ 没找到进程：", TARGET_PROCESS)
    exit()

print("✅ 找到 PID：", pids)

for pid in pids:
    hwnds = find_windows_by_pid(pid)
    print(f"PID {pid} 找到 hwnd 数量：", len(hwnds))

    for hwnd in hwnds:
        title = win32gui.GetWindowText(hwnd)
        cls = win32gui.GetClassName(hwnd)
        print("  hwnd:", hex(hwnd), "title:", repr(title), "class:", cls)

        ok = move_window(hwnd)
        print("  👉 尝试移动结果：", ok)
