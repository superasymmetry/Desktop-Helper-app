import pyautogui, sys
import mouse as mouse
import keyboard
import time
from extract import ExtractUtil
import pygetwindow as gw
from agents.extract import extractModel


class Event:
    def __init__(self):
        self.__listeners = []
        self.agent = ExtractUtil()
        self.clickables = self.agent.get_clickable_elements()

    # Define a getter for the 'on' property which returns the decorator.
    @property
    def on(self):
        # A declorator to run addListener on the input function.
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

@evn.on
def on_mouse_click(x, y):
    print(f"Mouse clicked at ({x}, {y})")

def handle_click():
    x, y = mouse.get_position()
    extract = extractModel()
    clickable_elements = extract.get_clickable_elements()
    element_name = None
    min_area = float('inf')
    for name, coords in clickable_elements.items():
        if(coords[0] < x and coords[2] > x and coords[1] < y and coords[3] > y):
            if(y>1776 and y<1920):  # check if it is in the taskbar position
                area = (coords[2]-coords[0])*(coords[3]-coords[1])
                if(area < min_area):
                    min_area = area
                    element_name = name

    active_window_elements = extract.get_active_window_elements()
    for name, coords in active_window_elements.items():
        if(coords[0] < x and coords[2] > x and coords[1] < y and coords[3] > y):
            area = (coords[2]-coords[0])*(coords[3]-coords[1])
            if(area < min_area):
                min_area = area
                element_name = name
    print(f"Clicked element: {element_name} at ({x}, {y})")
    evn.trigger([x, y])

mouse.on_click(handle_click)

if __name__ == '__main__':
    
    print("tracking .. press ctrl+c to stop")
    
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nstopped")

    # from some import some

    # @some.event
    # async def on_ready(some_info):
    #     print(some_info)

    # @some.event
    # async def on_error(err):
    #     print(err)

    
    # print('Press Ctrl-C to quit.') 
    # try: 
    #     while True: 
    #         x, y = pyautogui.position() 
    #         positionStr = 'X: ' + str(x).rjust(4) + ' Y: ' + str(y).rjust(4) 
    #         print(positionStr, end='') 
    #         print('\b' * len(positionStr), end='', flush=True) 
    # except KeyboardInterrupt: 
    #     print('\n')
