import pyperclip
from pywinauto.application import Application
from pywinauto.keyboard import send_keys
import time

cmd = 'load("<ADS_WORKSPACE>/probe_pins", "SimCmd")'
pyperclip.copy(cmd)
print(f"Clipboard: {cmd}")

app = Application(backend="uia").connect(title_re="Advanced Design System.*")
main = app.window(title_re="Advanced Design System.*")
main.click_input()
time.sleep(0.3)

send_keys("%T", with_spaces=False)
time.sleep(0.3)
send_keys("C", with_spaces=False)
time.sleep(0.5)
send_keys("^V", with_spaces=False)
time.sleep(0.2)
send_keys("{ENTER}", with_spaces=False)
time.sleep(1)
print("Done")
