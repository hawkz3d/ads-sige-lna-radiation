"""ADS 命令行发送 — 用 Win32 SendInput API"""
import sys, time, ctypes, pyperclip
from ctypes import wintypes

# 构建命令
if len(sys.argv) > 1:
    if sys.argv[1] == "--raw":
        cmd = sys.argv[2]
    else:
        name = sys.argv[1]
        cmd = 'load("<ADS_WORKSPACE>/' + name + '", "SimCmd")'
else:
    cmd = 'load("<ADS_WORKSPACE>/create_bandgap", "SimCmd")'

pyperclip.copy(cmd)
print(f"Clipboard: {cmd}")

# Win32 API
user32 = ctypes.windll.user32

# 找 Command Line 窗口
cmd_hwnd = None
hwnd = None
while True:
    hwnd = user32.FindWindowExW(None, hwnd, None, None)
    if not hwnd:
        break
    buf = ctypes.create_unicode_buffer(300)
    user32.GetWindowTextW(hwnd, buf, 300)
    title = buf.value
    if title and 'Command Line' in title:
        cmd_hwnd = hwnd
        print(f"Found: {title}")
        break

if not cmd_hwnd:
    print("ADS Command Line window not found!")
    sys.exit(1)

# 聚焦并发送
user32.SetForegroundWindow(cmd_hwnd)
time.sleep(0.4)

VK_CONTROL = 0x11
VK_V = 0x56
VK_RETURN = 0x0D
KEYEVENTF_KEYUP = 0x0002

def ctrl_v():
    user32.keybd_event(VK_CONTROL, 0, 0, 0)
    time.sleep(0.05)
    user32.keybd_event(VK_V, 0, 0, 0)
    time.sleep(0.05)
    user32.keybd_event(VK_V, 0, KEYEVENTF_KEYUP, 0)
    time.sleep(0.05)
    user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)
    time.sleep(0.1)

ctrl_v()
time.sleep(0.1)
user32.keybd_event(VK_RETURN, 0, 0, 0)
user32.keybd_event(VK_RETURN, 0, KEYEVENTF_KEYUP, 0)

print("Done")
