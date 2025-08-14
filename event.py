
import uiautomation as auto
import pyautogui, sys
import mouse as mouse
import keyboard
import time
from agents.extract import extractModel


class Event:
    def __init__(self):
        self.__listeners = []

    # Define a getter for the 'on' property which returns the decorator.
    @property
    def on(self):
        # A decorator to run addListener on the input function.
        def wrapper(func):
            self.addListener(func)
            return func
        return wrapper
    
    def addListener(self,func):
        if func in self.__listeners: return
        self.__listeners.append(func)
    
    def removeListener(self,func):
        if func not in self.__listeners: return
        self.__listeners.remove(func)
    
    def trigger(self,args = None):
        if args is None:
            args = []
        for func in self.__listeners: func(*args)

class UIAutomationEventHandler:
    def __init__(self):
        self.listeners = []
        
    def add_listener(self, func):
        self.listeners.append(func)
    
    def trigger_event(self, element_info):
        for listener in self.listeners:
            listener(element_info)

# global event handler
click_handler = UIAutomationEventHandler()

evn = Event()
scroll_evn = Event()
key_evn = Event()
extract = extractModel()
sequence = []

@scroll_evn.on
def on_mouse_scroll(x, y, delta):
    sequence.append(f"Scrolled at {x}, {y} with delta: {delta}")

@key_evn.on
def on_key_press(key):
    sequence.append(f"Key pressed: {key}")

def handle_click():
    x, y = mouse.get_position()
    try:
        with auto.UIAutomationInitializerInThread():
            element = auto.ControlFromPoint(x, y)
            if element:
                element_info = {
                    'name': element.Name,
                    'type': element.ControlTypeName,
                    'coordinates': (x, y),
                    'bounds': element.BoundingRectangle
                }
                click_handler.trigger_event(element_info)
    except Exception as e:
        return ""

    evn.trigger([x, y])

@click_handler.add_listener
def on_uia_clicked(element_info):
    sequence.append(f"Clicked {element_info['name']} ({element_info['type']})")


def handle_scroll(x, y, delta):
    scroll_evn.trigger([x, y, delta])

def handle_keypress(key):
    key_str = str(key)
    if key_str.endswith(' down)'):
        key_str = key_str[:-6]
    # check for starts with
    if key_str.startswith('KeyboardEvent('):
        key_str = key_str[14:]
    key_evn.trigger([key_str])

def mouse_event_handler(event):
    # handle all mouse events including scroll
    if isinstance(event, mouse.ButtonEvent):
        if event.event_type == mouse.DOWN:
            handle_click()
    elif isinstance(event, mouse.WheelEvent):
        # note: for scroll to properly detect you need to use a real mouse not just trackpad
        x, y = mouse.get_position()
        delta = event.delta
        handle_scroll(x, y, delta)

mouse.hook(mouse_event_handler)
keyboard.on_press(handle_keypress)

if __name__ == '__main__':

    print("tracking .. press ctrl+c to stop")
    
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nstopped")
        print(sequence)
        seq = []
        i = 0
        while i < len(sequence):
            if "Key pressed:" in sequence[i]:
                temp = ""
                while i < len(sequence) and "Key pressed:" in sequence[i]:
                    # parse the key pressed
                    key = sequence[i].split(": ")[1]
                    temp += key
                    temp += " "
                    i += 1
                seq.append(f"Keys pressed: {temp.strip()}")
                if i < len(sequence):
                    seq.append(sequence[i])
                    i += 1
            else:
                seq.append(sequence[i])
                i += 1
        print(seq)
        sys.exit(0)
