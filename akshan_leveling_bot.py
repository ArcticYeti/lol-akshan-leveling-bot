import enum
import pyautogui
import time
import keyboard
import win32gui
import win32api
import win32con
import logging
import os


# ONLY WORKS ON WINDOWS
#
# setup guide:
#   go to practice tool
#   disable spell upgrade recommendations
#   disable UI animations
#   set hud scale to 0
#   set shop scale to 100
#   enable colorblind mode
#   set graphics resolution to 1280x720
#   set game to borderless mode
#   put shop in the top right corner (will auto-adjust itself later)

APP_NAME = 'Akshan Leveling Bot'
GAME_WINDOW_TITLE = 'League of Legends (TM) Client'
CLIENT_WINDOW_TITLE = 'League of Legends'
CLIENT_EXPECTED_SIZE = [1024, 576]
app_running = True
app_paused = False
current_state = None


class State(enum.Enum):
    CLIENT_FIND_WINDOW = enum.auto()
    CLIENT_CHECK_WINDOW_SIZE = enum.auto()
    CLIENT_ROUTER_HUB = enum.auto()
    CLIENT_PRESS_PLAY = enum.auto()
    CLIENT_PRESS_COOP = enum.auto()
    CLIENT_READY_UP = enum.auto()
    CLIENT_ACCEPT_QUEUE = enum.auto()
    CLIENT_SELECT_CHAMPION = enum.auto()
    CLIENT_LOCK_IN = enum.auto()
    LOADING_SCREEN = enum.auto()
    GAME_ROUTER_HUB = enum.auto()
    GAME_BUY_ITEMS = enum.auto()
    GAME_LOCK_CAMERA = enum.auto()
    GAME_WALK_TO_WOLF_CAMP = enum.auto()
    GAME_DISMISS_AFK_WARNING = enum.auto()
    CLIENT_HONOR_TEAMMATE = enum.auto()
    CLIENT_PLAY_AGAIN = enum.auto()

logging.basicConfig(level = logging.DEBUG,
                    format = '[%(asctime)s] %(levelname)s: %(message)s', datefmt='%H:%M:%S')

def window_relative_coords(hwnd: int, x: int, y: int):
    offset_x, offset_y, _, _ = get_window_coords(hwnd)

    return (x+offset_x, y+offset_y)

def get_window_titles():
    ret = []
    def winEnumHandler(hwnd, ctx):
        if win32gui.IsWindowVisible(hwnd):
            txt = win32gui.GetWindowText(hwnd)
            if txt:
                ret.append((hwnd,txt))

    win32gui.EnumWindows(winEnumHandler, None)
    return ret

def window_exists(target_hwnd: int) -> bool:
    all_windows = get_window_titles()
    is_found = False
    for hwnd, full_title in all_windows:
        if hwnd == target_hwnd:
            is_found = True
    return is_found

def set_terminal_title(text: str):
    os.system(f"title {text}")

def mouse_move(hwnd: int, x: int, y: int):
    relative_x, relative_y = window_relative_coords(hwnd, x, y)
    win32api.SetCursorPos((relative_x, relative_y))

def right_click(hwnd: int, x: int, y: int):
    relative_x, relative_y = window_relative_coords(hwnd, x, y)
    win32api.SetCursorPos((relative_x, relative_y))
    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0)
    time.sleep(0.01)
    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0)

def click(hwnd: int, x: int, y: int):
    relative_x, relative_y = window_relative_coords(hwnd, x, y)
    win32api.SetCursorPos((relative_x, relative_y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
    time.sleep(0.01)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)

def get_window_coords(hwnd: int) -> tuple:
    try:
        x0, y0, x1, y1 = win32gui.GetWindowRect(hwnd)
    except:
        x0, y0, x1, y1 = 0, 0, 0, 0
    return (x0, y0, x1, y1)

def is_window_active(hwnd: int):
    active_window = win32gui.GetForegroundWindow()
    return active_window == hwnd

def activate_window(hwnd: int):
    try:
        win32gui.SetForegroundWindow(hwnd)
        return True
    except:
        return False

def get_window(window_title: str):
    return win32gui.FindWindow(None, window_title)

def set_state(state: State):
    global current_state
    set_terminal_title(f"{APP_NAME}  /  {state.name}")
    logging.info(f"State set to '{state.name}'.")
    win32api.SetCursorPos((0, 0))
    time.sleep(0.1)
    current_state = state

def pause_app():
    global app_paused
    app_paused = not app_paused

def stop_app():
    global app_running
    app_running = False

def pixel_matches(x: int, y: int, color: tuple):
    im = pyautogui.screenshot(region=(x, y, 1, 1))
    return im.getpixel((0, 0)) == color

def get_pixel(hwnd: int, x: int, y: int):
    relative_x, relative_y = window_relative_coords(hwnd, x, y)
    im = pyautogui.screenshot(region=(relative_x, relative_y, 1, 1))
    return im.getpixel((0, 0))

if __name__ == '__main__':
    keyboard.add_hotkey('ctrl+p', pause_app)
    keyboard.add_hotkey('ctrl+end', stop_app)
    set_terminal_title('Akshan Leveling Bot')
    set_state(State.CLIENT_FIND_WINDOW)
    win32api.SetCursorPos((0, 0))

    while app_running:
        if app_paused:
            time.sleep(0.25)
            continue

        match current_state:
            case State.CLIENT_FIND_WINDOW:
                client_hwnd = get_window(CLIENT_WINDOW_TITLE)

                if client_hwnd == 0:
                    logging.error('League Client is not running.')
                    # extra sleep until client is opened
                    time.sleep(2)
                else:
                    set_state(State.CLIENT_CHECK_WINDOW_SIZE)
            case State.CLIENT_CHECK_WINDOW_SIZE:
                client_x0, client_y0, client_x1, client_y1 = get_window_coords(client_hwnd)
                client_window_size = [client_x1-client_x0, client_y1-client_y0]
                game_hwnd = get_window(GAME_WINDOW_TITLE)

                if window_exists(game_hwnd):
                    set_state(State.LOADING_SCREEN)
                elif not window_exists(client_hwnd):
                    set_state(State.CLIENT_FIND_WINDOW)
                elif not is_window_active(client_hwnd):
                    activate_window(client_hwnd)
                    time.sleep(0.25)
                elif client_window_size != CLIENT_EXPECTED_SIZE:
                    logging.info('Adjusting client size...')
                    keyboard.press_and_release('ctrl+-')
                else:
                    set_state(State.CLIENT_ROUTER_HUB)

            case State.CLIENT_ROUTER_HUB:
                game_hwnd = get_window(GAME_WINDOW_TITLE)

                if window_exists(game_hwnd):
                    set_state(State.LOADING_SCREEN) 
                elif get_pixel(client_hwnd, 84, 33) == (235, 226, 206):     # white letter P on play button
                    set_state(State.CLIENT_PRESS_PLAY)
                elif get_pixel(client_hwnd, 800, 83) == (211, 198, 156):    # right top corner tournament icon
                    set_state(State.CLIENT_PRESS_COOP)
                elif get_pixel(client_hwnd, 1013, 124) == (41, 90, 35):     # green queue timer
                    set_state(State.CLIENT_READY_UP)
                elif get_pixel(client_hwnd, 523, 263) == (1, 79, 119):      # accept queue graphic
                    set_state(State.CLIENT_ACCEPT_QUEUE)
                elif get_pixel(client_hwnd, 530, 484) == (72, 73, 72):      # grayed out lock in button
                    set_state(State.CLIENT_SELECT_CHAMPION)
                elif get_pixel(client_hwnd, 506, 495) == (30, 37, 41):      # lit up lock in button
                    set_state(State.CLIENT_LOCK_IN)
                # end of game
                elif get_pixel(client_hwnd, 511, 522) == (115, 113, 93):
                    set_state(State.CLIENT_HONOR_TEAMMATE)
                elif get_pixel(client_hwnd, 658, 32) == (190, 177, 135):    # advanced stats text
                    set_state(State.CLIENT_PLAY_AGAIN)
                elif get_pixel(client_hwnd, 658, 33) == (205, 190, 145):
                    set_state(State.CLIENT_PLAY_AGAIN)

            case State.CLIENT_PRESS_PLAY:
                click(client_hwnd, 73, 32)
                set_state(State.CLIENT_ROUTER_HUB)

            case State.CLIENT_PRESS_COOP:
                click(client_hwnd, 115, 80)      # select coop at the top
                time.sleep(0.5)
                click(client_hwnd, 332, 421)     # select beginner difficulty
                time.sleep(0.5)
                click(client_hwnd, 427, 550)     # confirm button
                set_state(State.CLIENT_ROUTER_HUB)

            case State.CLIENT_READY_UP:
                click(client_hwnd, 417, 560)
                set_state(State.CLIENT_ROUTER_HUB)

            case State.CLIENT_ACCEPT_QUEUE:
                click(client_hwnd, 493, 448)
                set_state(State.CLIENT_ROUTER_HUB)

            case State.CLIENT_SELECT_CHAMPION:
                time.sleep(1.0)
                click(client_hwnd, 619, 86)
                time.sleep(0.5)
                keyboard.write('Akshan')
                time.sleep(0.5)
                click(client_hwnd, 309, 129)
                set_state(State.CLIENT_ROUTER_HUB)

            case State.CLIENT_LOCK_IN:
                click(client_hwnd, 506, 495)
                set_state(State.CLIENT_ROUTER_HUB)

            case State.LOADING_SCREEN:
                game_hwnd = get_window(GAME_WINDOW_TITLE)

                if not window_exists(game_hwnd):
                    set_state(State.CLIENT_ROUTER_HUB)
                elif not is_window_active(game_hwnd):
                    activate_window(game_hwnd)
                    time.sleep(0.25)
                elif get_pixel(game_hwnd, 1233, 672) == (52, 55, 40):       # botlane fog of war
                    set_state(State.GAME_BUY_ITEMS)

            case State.GAME_ROUTER_HUB:
                game_hwnd = get_window(GAME_WINDOW_TITLE)

                if not window_exists(game_hwnd):
                    set_state(State.CLIENT_ROUTER_HUB)
                elif not is_window_active(game_hwnd):
                    activate_window(game_hwnd)
                    time.sleep(0.25)
                elif get_pixel(game_hwnd, 959, 705) == (170, 146, 101):                 # unlocked camera button
                    set_state(State.GAME_LOCK_CAMERA)
                elif get_pixel(game_hwnd, 1206, 587) == (146, 147, 146):                 # enemy blue buff grey
                    set_state(State.GAME_WALK_TO_WOLF_CAMP)
                elif get_pixel(game_hwnd, 664, 327) == (66, 48, 25):                    # afk warning button
                    set_state(State.GAME_DISMISS_AFK_WARNING)

            case State.GAME_BUY_ITEMS:
                keyboard.send('p')                  # open shop
                time.sleep(0.25)
                click(game_hwnd, 601, 54)           # all items
                time.sleep(0.25)
                click(game_hwnd, 338, 142)          # all classes
                time.sleep(0.25)
                click(game_hwnd, 800, 223)          # select cull
                time.sleep(0.25)
                click(game_hwnd, 1085, 679)         # click purchase
                time.sleep(0.25)
                keyboard.send('p')                  # close shop
                time.sleep(0.25)
                # this levels up E, its here cause Im lazy to rewrire lol
                keyboard.send('ctrl+e')
                set_state(State.GAME_ROUTER_HUB)

            case State.GAME_LOCK_CAMERA:
                keyboard.send('y')                  # locks camera
                set_state(State.GAME_ROUTER_HUB)

            case State.GAME_WALK_TO_WOLF_CAMP:
                right_click(game_hwnd, 1069, 599)
                time.sleep(50.0)
                mouse_move(game_hwnd, 903, 255)
                time.sleep(0.25)
                keyboard.send('e')      # cast on wall
                time.sleep(1.0)
                keyboard.send('e')      # recast to activate
                set_state(State.GAME_ROUTER_HUB)

            case State.GAME_DISMISS_AFK_WARNING:
                click(game_hwnd, 664, 327)
                set_state(State.GAME_ROUTER_HUB)

            case State.CLIENT_HONOR_TEAMMATE:
                click(client_hwnd, 417, 353)
                set_state(State.CLIENT_ROUTER_HUB)
            case State.CLIENT_PLAY_AGAIN:
                click(client_hwnd, 417, 553)
                set_state(State.CLIENT_ROUTER_HUB)

        time.sleep(0.25)
