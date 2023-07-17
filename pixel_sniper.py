import pyautogui
import keyboard
import os
import win32gui
import pyperclip

# script for retrieving window-relative pixel data
# 
# how to use
#   [CTRL + SHIFT + ALT + A]: save mouse position on the active window
#   [CTRL + SHIFT + ALT + S]: retrieves the pixel x, y and rgb color (copies to clipboard and prints it)

saved_mouse_pos = [0, 0]
active_window = 0

def set_terminal_title(text: str):
    os.system(f"title {text}")

def get_window_coords(hwnd: int) -> tuple:
    try:
        x0, y0, x1, y1 = win32gui.GetWindowRect(hwnd)
    except:
        x0, y0, x1, y1 = 0, 0, 0, 0
    return (x0, y0, x1, y1)

def save_mouse_pos():
    global saved_mouse_pos, active_window

    saved_mouse_pos = pyautogui.position()
    active_window = win32gui.GetForegroundWindow()
    set_terminal_title(f"pixel_sniper  /  {win32gui.GetWindowText(active_window)}  /  {saved_mouse_pos}")

def get_pixel():
    global saved_mouse_pos
    x, y = saved_mouse_pos
    im = pyautogui.screenshot(region=(x, y, 1, 1))
    active_window = win32gui.GetForegroundWindow()
    win_x0, win_y0, win_x1, win_y1 = get_window_coords(active_window)
    relative_x, relative_y = (x-win_x0, y-win_y0)

    output = f"{relative_x}, {relative_y}, {im.getpixel((0, 0))}"
    pyperclip.copy(output)
    print(output)

if __name__ == '__main__':
    set_terminal_title('pixel_sniper')

    keyboard.add_hotkey('ctrl+alt+shift+a', save_mouse_pos)
    keyboard.add_hotkey('ctrl+alt+shift+s', get_pixel)
    keyboard.wait('F1') 
        
        
