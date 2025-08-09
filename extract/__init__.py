# get_ui_elements.py
import uiautomation as automation
import pyautogui
import pygetwindow as gw
import json

class BoundingBox:
    def __init__(self, left, top, right, bottom):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom

    def is_valid(self):
        """Check if the bounding box is valid."""
        return self.right > self.left and self.bottom > self.top


class CenterCord:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class TreeElementNode:
    def __init__(self, name, control_type, shortcut, bounding_box, center, handle):
        self.name = name
        self.control_type = control_type
        self.shortcut = shortcut
        self.bounding_box = bounding_box
        self.center = center
        self.handle = handle

    def __repr__(self):
        return f"{self.name} ({self.control_type}) - Coordinates: {self.bounding_box.left}, {self.bounding_box.top}, {self.bounding_box.right}, {self.bounding_box.bottom}"

class extractModel():
    def __init__(self):
        pass

    def get_clickable_elements(self, max_depth=35):
        """Retrieve all clickable UI elements and return a dictionary with positions."""
        root_control = automation.GetRootControl()
        screen_width, screen_height = pyautogui.size()
        element_dict = {}

        def tree_traversal(node, depth=0):
            """Recursive function to traverse the UI tree and extract clickable elements."""
            if depth > max_depth:
                return

            for child in node.GetChildren():
                box = child.BoundingRectangle
                bounding_box = BoundingBox(
                    left=box.left,
                    top=box.top,
                    right=box.right,
                    bottom=box.bottom
                )

                # Skip invalid, out-of-bounds, or invisible elements
                if not bounding_box.is_valid() or box.left < 0 or box.top < 0 or box.right > screen_width or box.bottom > screen_height:
                    continue

                # Check if the element is clickable (Button, ListItem, etc.)
                if child.ControlTypeName in ["ButtonControl", "ListItemControl", "HyperlinkControl", "MenuItemControl"]:
                    element_name = child.Name.strip() if child.Name else "Unnamed"

                    # Ensure the name is unique to prevent overwriting
                    counter = 1
                    original_name = element_name
                    while element_name in element_dict:
                        element_name = f"{original_name}_{counter}"
                        counter += 1

                    # Add the element to the dictionary with bounding rectangle coordinates
                    element_dict[element_name] = (box.left, box.top, box.right, box.bottom)

                # Recursive call to check deeper levels
                tree_traversal(child, depth + 1)

        # Start tree traversal from the root control
        tree_traversal(root_control)
        return element_dict


    def get_active_window_elements(self, max_depth=35):
        """Get clickable elements from the active window."""
        active_window = automation.GetForegroundControl()
        if not active_window:
            print("No active window found.")
            return {}

        screen_width, screen_height = pyautogui.size()
        window_elements = {}

        def tree_traversal(node, depth=0):
            """Recursive function to traverse the UI tree and extract clickable elements."""
            if depth > max_depth:
                return

            for child in node.GetChildren():
                box = child.BoundingRectangle
                bounding_box = BoundingBox(
                    left=box.left,
                    top=box.top,
                    right=box.right,
                    bottom=box.bottom
                )

                # Skip invalid, out-of-bounds, or invisible elements
                if not bounding_box.is_valid() or box.left < 0 or box.top < 0 or box.right > screen_width or box.bottom > screen_height:
                    continue

                # Check if the element is clickable (Button, ListItem, etc.)
                if child.ControlTypeName in ["ButtonControl", "ListItemControl", "HyperlinkControl", "MenuItemControl"]:
                    element_name = child.Name.strip() if child.Name else "Unnamed"

                    # Ensure the name is unique to prevent overwriting
                    counter = 1
                    original_name = element_name
                    while element_name in window_elements:
                        element_name = f"{original_name}_{counter}"
                        counter += 1

                    # Add the element to the dictionary with bounding rectangle coordinates
                    window_elements[element_name] = (bounding_box.left, bounding_box.top, bounding_box.right, bounding_box.bottom)

                # Recursive call to check deeper levels
                tree_traversal(child, depth + 1)

        # Start tree traversal from the active window control
        tree_traversal(active_window)

        return window_elements


if __name__ == "__main__":
    # Get desktop elements
    j = {"desktop": {}, "taskbar": {}}
    extract = extractModel()
    clickable_elements = extract.get_clickable_elements()
    for name, coords in clickable_elements.items():
        if(coords[1]>1776 and coords[1]<1920):  # check if it is in the taskbar position
            j["taskbar"][name] = coords
        else:
            j["desktop"][name] = coords
        # print(name, j["desktop"][name])
    active_window_elements = extract.get_active_window_elements()
    print("Active window elements", active_window_elements)

    active_window = gw.getActiveWindow().title
    j[f"{active_window}"] = {}
    # active window elements
    for name, coords in active_window_elements.items():
        j[f"{active_window}"][name] = coords
        print(name, j[f"{active_window}"][name])

    with open("ui_elements.json", "w") as file:
        json.dump(j, file, indent=4)
    print("taskbar elements", j["taskbar"])
