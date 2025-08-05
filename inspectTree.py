import time
from win32gui import GetWindowText, GetForegroundWindow
from pywinauto import Application, Desktop
import json
import win32api
import hashlib
import math
import re

def flatten_tree(element, elements_list):
    info = element.element_info
    name=info.name
    
    #Arbitrary filter on length of string
    maxLen=80
    if len(name) > maxLen:
        name=name[:maxLen-3] + "..."
    
    node = {
        "name": name,
        "type": info.control_type,
        "X": int((info.rectangle.left+info.rectangle.right)/2),
        "Y": int((info.rectangle.top+info.rectangle.bottom)/2)
    }
    
    '''
        An alternative method to track - this is the bounding boxes but not needed right now
        "rect": {
            "left": info.rectangle.left,
            "top": info.rectangle.top,
            "right": info.rectangle.right,
            "bottom": info.rectangle.bottom
        }
    '''

    elements_list.append(node)

    try:
        for child in element.children():
            flatten_tree(child, elements_list)
    except Exception as e:
        pass  # Ignore inaccessible children

def filter_duplicates(elements, tolerance=50):
    filtered = []
    seen = []

    for elem in elements:
        name = elem["name"]
        x = elem["X"]
        y = elem["Y"]

        # Check if there is a similar element already seen
        is_duplicate = False
        for s in seen:
            if s["name"] == name:
                sx = s["X"]
                sy = s["Y"]
                dist = math.hypot(x - sx, y - sy)
                if dist <= tolerance:
                    is_duplicate = True
                    break
        
        if not is_duplicate:
            filtered.append(elem)
            seen.append(elem)

    return filtered

def getTree():
    time.sleep(1)
    
    notSuccess=True
    while notSuccess:
        try:
            windowName = GetWindowText(GetForegroundWindow())
            print("ML-getTree()-Detected Window:", windowName)
            
            escaped_window_name = ".*" + re.escape(windowName) + ".*"

            # Try connecting to the application
            app = Application(backend="uia").connect(title_re=escaped_window_name)

            notSuccess=False

        except Exception as e:
            print("Something got really fricked up so retrying")
            time.sleep(0.2)

    # Get the top window of that app
    dlg = app.top_window()

    all_elements = []
    flatten_tree(dlg, all_elements)
    
    desktop = Desktop(backend="uia")

    #Find the tbar
    try:
        taskbar = desktop.window(title="Taskbar")
    except Exception as e:
        print("ML-getTree()-Taskbar not found!")

    tbar_elements = []
    flatten_tree(taskbar, tbar_elements)
    
    
    #all_elements+={"name": 'THE BELOW ELEMENTS ARE ALL OF THE TASKBAR.'}
    all_elements+=tbar_elements
    
    marker = {
        "name": "=== TASKBAR STARTS HERE ===",
        "control_type": "Marker",
        "X": 0,
        "Y": 0
    }
    for i, el in enumerate(all_elements):
        if el["name"] == "Taskbar":
            all_elements.insert(i, marker)
            break
    
    
    screen_width = win32api.GetSystemMetrics(0)
    screen_height = win32api.GetSystemMetrics(1)

    #Filter non-empty names and centres inside screen bounds
    filt = []
    for el in all_elements:
        if not el["name"].strip():
            continue

        x = el["X"]
        y = el["Y"]

        if (0 <= x <= screen_width) and (0 <= y <= screen_height):
            filt.append(el)
    
    #Straight-up return the json
    return filter_duplicates(filt)

"""Helper to create a hash of the tree to detect changes."""
def hash_tree(tree):
    json_str = json.dumps(tree, sort_keys=True)
    return hashlib.md5(json_str.encode()).hexdigest()

#Waits until webpage loaded
def stable_tree(stable_checks=2, interval=0.5):
    time.sleep(interval)
    
    last_hash = None
    stable_count = 0
    checks=0
    while True:
        checks+=1
        current_tree = getTree()
        current_hash = hash_tree(current_tree)

        if current_hash == last_hash:
            stable_count += 1
        else:
            stable_count = 0

        last_hash = current_hash

        if stable_count >= stable_checks or checks>=10:
            
            print("\n\nML-stable_tree()-Page is stable thus CONTINUING, after", checks, "checks.")
            if True:
                print("ML-stable_tree()-json passed:")
                for i in current_tree:
                    print(i)
            return current_tree


        time.sleep(interval)
if __name__ == "__main__":
    stable_tree()
