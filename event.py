# import sys
# import mouse as mouse
# import keyboard
# import time
# import queue
# import uiautomation as auto
# from agents.extract import extractModel

# # Queue to pass click data from callback thread to main thread
# click_queue = queue.Queue()


# class Event:
#     def __init__(self):
#         self.__listeners = []

#     # Define a getter for the 'on' property which returns the decorator.
#     @property
#     def on(self):
#         # A declorator to run addListener on the input function.
#         def wrapper(func):
#             self.addListener(func)
#             return func
#         return wrapper
    
#     def addListener(self,func):
#         if func in self.__listeners: return
#         self.__listeners.append(func)
    
#     def removeListener(self,func):
#         if func not in self.__listeners: return
#         self.__listeners.remove(func)
    
#     # Trigger events
#     def trigger(self,args = None):
#         # Run all the functions that are saved.
#         if args is None:
#             args = []
#         for func in self.__listeners: func(*args)


# evn = Event()  # For mouse events
# key_evn = Event()  # For keyboard events
# extract = extractModel()

# @evn.on
# def on_mouse_click(x, y):
#     print(f"Click detected at ({x}, {y})")  # Immediate feedback
#     # Just queue the coordinates for processing in main thread (much faster)

# def process_ui_automation(x, y):
#     """Process UI automation in main thread where COM is already initialized"""
#     try:
#         clickable_elements = extract.get_clickable_elements()
#         element_name = None
#         min_area = float('inf')
#         for name, coords in clickable_elements.items():
#             if(coords[0] < x and coords[2] > x and coords[1] < y and coords[3] > y):
#                 if(y>1776 and y<1920):  # check if it is in the taskbar position
#                     area = (coords[2]-coords[0])*(coords[3]-coords[1])
#                     if(area < min_area):
#                         min_area = area
#                         element_name = name

#         active_window_elements = extract.get_active_window_elements()
#         for name, coords in active_window_elements.items():
#             if(coords[0] < x and coords[2] > x and coords[1] < y and coords[3] > y):
#                 area = (coords[2]-coords[0])*(coords[3]-coords[1])
#                 if(area < min_area):
#                     min_area = area
#                     element_name = name
#         print(f"UI Element: {element_name}")
#     except Exception as e:
#         print(f"Error in UI automation: {e}")

# def handle_click():
#     x, y = mouse.get_position()
#     evn.trigger([x, y])  # Immediate click detection
#     click_queue.put((x, y))  # Queue for UI automation

# @key_evn.on
# def on_key_press(key):
#   print("Key pressed: ", key)

#   if hasattr(key, "char") and key.char == "z":
#     print("Z PRESSED!")

# def handle_key_press(event):
#   key = event.name
#   key_evn.trigger([key])  # Use key_evn for keyboard events

# def on_key_release(key):
#   print("Key released: ", key)
#   # if you need to check for a special key like shift you can
#   # do so like this:
#   if key == "shift":
#     print("SHIFT KEY RELEASED!")

# keyboard.on_press(on_key_press)
# keyboard.on_release(on_key_release)

# mouse.on_click(handle_click)

# if __name__ == '__main__':
#     print("tracking .. press ctrl+c to stop")

#     try:
#         while True:
#             # Process any clicks in the queue for UI automation
#             try:
#                 x, y = click_queue.get_nowait()
#                 process_ui_automation(x, y)
#             except queue.Empty:
#                 pass
#             time.sleep(0.1)
#     except KeyboardInterrupt:
#         print("\nstopped")
#         sys.exit(0)


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
    
    # Trigger events
    def trigger(self,args = None):
        # Run all the functions that are saved.
        if args is None:
            args = []
        for func in self.__listeners: func(*args)

evn = Event()
scroll_evn = Event()  # Fixed name
key_evn = Event()     # Fixed name  
extract = extractModel()

@evn.on
def on_mouse_click(x, y):
    print(f"Clicked at ({x}, {y})")

@scroll_evn.on
def on_mouse_scroll(x, y, delta):
    if delta > 0:
        direction = "up"
    else:
        direction = "down"
    print(f"Scrolled at {x}, {y}. Direction is {direction}, Delta: {delta}")

@key_evn.on
def on_key_press(key):
    print("Key pressed: ", key)

def handle_click():
    x, y = mouse.get_position()
    # clickable_elements = extract.get_clickable_elements()
    # element_name = None
    # min_area = float('inf')
    # for name, coords in clickable_elements.items():
    #     if(coords[0] < x and coords[2] > x and coords[1] < y and coords[3] > y):
    #         if(y>1776 and y<1920):  # check if it is in the taskbar position
    #             area = (coords[2]-coords[0])*(coords[3]-coords[1])
    #             if(area < min_area):
    #                 min_area = area
    #                 element_name = name

    # active_window_elements = extract.get_active_window_elements()
    # for name, coords in active_window_elements.items():
    #     if(coords[0] < x and coords[2] > x and coords[1] < y and coords[3] > y):
    #         area = (coords[2]-coords[0])*(coords[3]-coords[1])
    #         if(area < min_area):
    #             min_area = area
    #             element_name = name
    evn.trigger([x, y])

def handle_scroll(x, y, delta):
    """Handle mouse scroll events"""
    scroll_evn.trigger([x, y, delta])

def handle_keypress(key):
    key_evn.trigger([key])

def mouse_event_handler(event):
    """Handle all mouse events including scroll"""
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
        sys.exit(0)
