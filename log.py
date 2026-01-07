from helpers import *
from os import makedirs, stat
from pythoncom import CoInitialize
from pynput import keyboard, mouse
from datetime import datetime, timedelta, timezone
from threading import Thread

held = {'ctrl_l' : False, 'shift_l' : False, '<' : False}
y1, y2 = None, None

try:
    makedirs('logs')
except:
    pass

def save_logs(time, y):
    global tm

    CoInitialize()

    time_str = str(time)[0:-6].replace(':', '-').replace(' ', '_')
    file = f'logs\\{time_str}.sqlite'

    print(f'Startar tråd {time_str}')

    tm.get_system_data()
    tm.sort_data()

    for category in categories:
        data = list(data_point for data_point in getattr(tm, category).values())
        write_to_table(file, 'task_manager', data)

    events = get_events(time)
    write_to_table(file, 'events', events)

    top, bot = y['top'], y['bot']

    file_size = stat(file).st_size

    write_to_table(
        file, 
        'metadata',
        (len(events), top, bot, round((bot - top) / 10.79), file_size, tm.points)
    )

    print(f'Tråd startad {time_str} avslutad')

def on_key_press(key):
    if key == keyboard.Key.ctrl_l:
        held['ctrl_l'] = True
    if key == keyboard.Key.shift_l:
        held['shift_l'] = True
    try:
        if key.vk == 226:
            held['<'] = True
    except:
        pass

def on_key_release(key):
    if key == keyboard.Key.ctrl_l:
        held['ctrl_l'] = False
    if key == keyboard.Key.shift_l:
        held['shift_l'] = False
    try:
        if key.vk == 226:
            held['<'] = False
    except:
        pass

def on_mouse_click(y, pressed):
    global y1, y2

    if pressed and all(key_held for key_held in held.values()):
        if y1 is None:
            y1 = y

        else:
            y2 = y
            Thread(
                target = save_logs,
                args = (
                    datetime.now(timezone(timedelta(hours = 2))),
                    {
                        'top' : min(y1, y2),
                        'bot' : max(y1,y2)
                        }
                ),
                daemon = False
            ).start()
            y1, y2 = None, None

def init_listeners():
    global keyboard_listener, mouse_listener
    
    keyboard_listener = keyboard.Listener(
        on_press = on_key_press,
        on_release = on_key_release
    )

    mouse_listener = mouse.Listener(
        on_click = lambda x, y, button, pressed: on_mouse_click(y, pressed)
    )
    
    keyboard_listener.start()
    mouse_listener.start()

    keyboard_listener.join()
    mouse_listener.join()

init_listeners()