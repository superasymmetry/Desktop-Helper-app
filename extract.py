import uiautomation as automation
import pyautogui
import os
import json

class ExtractUtil():
    def __init__(self):
        # for UIAutomation
        self.max_depth = 20
        self.root_control = automation.GetRootControl()
        # Use a dictionary comprehension to assign a separate list for each key.
        self.tree = {key: [] for key in [
            'WindowControl', 'PaneControl', 'DocumentControl', 'ButtonControl',
            'EditControl', 'CheckBoxControl', 'RadioButtonControl', 'ComboBoxControl',
            'ListControl', 'ListItemControl', 'MenuControl', 'TreeControl',
            'TabControl', 'SliderControl', 'CustomControl'
        ]}

    def get_control_coordinates(self, control):
        """Return control's bounding rectangle as (left, top, width, height) if available."""
        try:
            rect = control.BoundingRectangle
            if isinstance(rect, tuple) and len(rect) == 4:
                left, top, right, bottom = rect
            else:
                left, top, right, bottom = rect.left, rect.top, rect.right, rect.bottom
            width = right - left
            height = bottom - top
            return (left, top, width, height)
        except Exception as e:
            print(f"Error getting coordinates for {control.ControlTypeName}: {e}")
            return None

    def get_major_controls(self, control, indent=0, max_depth=None):
        if max_depth is None:
            max_depth = self.max_depth
        if indent // 4 >= max_depth:
            return

        try:
            name = control.Name.strip() if control.Name else ''
            if control.IsOffscreen and "Grammarly" in name and control.ControlTypeName not in self.interactive_controls:
                return

            coords = self.get_control_coordinates(control)
            if name and coords:
                controlType = control.ControlTypeName
                # Only add if the controlType is one of the keys in our tree.
                if controlType in self.tree:
                    self.tree[controlType].append({"feature": name, "coordinates": coords})
                    print(f"{indent*' '} Added {controlType}: {name} - Coordinates: {coords}")
        except Exception as e:
            try:
                ctype = control.ControlTypeName
            except Exception:
                ctype = "<unknown>"
            print(' ' * indent + f'{ctype}: <error retrieving info> - {e}')

        try:
            # Recursively process child controls
            for child in control.GetChildren():
                self.get_major_controls(child, indent + 4, max_depth)
        except Exception as e:
            print(' ' * indent + f'<error iterating children> - {e}')

    # get only clickable elements
    def get_clickable_elements(max_depth = 35):
        root_control = automation.GetRootControl()
        screen_width, screen_height = pyautogui.size()
        element_dict = {}

        def tree_traversal(node, depth = 0):
            if depth > 35:
                return
            for child in node.GetChildren():
                if child.ControlTypeName in ["Button", "ListItem", "Hyperlink", "CheckBox", "RadioButton"]:
                    element_name = child.Name.strip() if child.Name else "Unnamed"
                    box = child.BoundingRectangle
                    element_dict[element_name] = ((box.left+box.right)/2, (box.top+box.bottom)/2)
                    print(element_dict[element_name])
                tree_traversal(child, depth + 1)
            
        tree_traversal(root_control)
        return element_dict

if __name__ == "__main__":
    agent = ExtractUtil()
    # agent.get_major_controls(agent.root_control)
    clickable_elements = agent.get_clickable_elements()
