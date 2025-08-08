import pyautogui, sys
import mouse as mouse
import keyboard
import time
from extract import ExtractUtil

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
    e = ExtractUtil()
    e.get_major_controls(e.root_control)
    clickable_elements = e.tree
    print(clickable_elements)
    time.sleep(1)
    for( name, coords ) in clickable_elements.items():
        if coords[0] < x < coords[1] and coords[2] < y < coords[3]:
            element_name = name
            print(f"Clicked on clickable element: {element_name}")
            break
    evn.trigger([x, y])

mouse.on_click(handle_click)

if __name__ == '__main__':
    
    print("tracking .. press ctrl+c to stop")
    
    try:
        # Keep the program running to listen for events
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
