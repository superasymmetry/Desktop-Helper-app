import pyautogui
from openai import OpenAI
import base64
from AppOpener import open as open_app
import time
import io
import subprocess
from groq import Groq
import json
from io import BytesIO
import sys
import os
import urllib.request
from PIL import Image


#Mars - This is my file - too lazy to put it into one
import inspectTree
print("ALL IMPORTS COMPLETE")

omniParser_setUp=False

#Sets up OmniParser
def opSetUp():
        # === OMNIPARSER CODE ===
    omni_parser_path = r"C:\Users\2026029\OmniParser"
    sys.path.append(r"C:\Users\2026029\OmniParser")

    from util.utils import get_som_labeled_img, check_ocr_box, get_caption_model_processor, get_yolo_model
    import torch
    from ultralytics import YOLO
    from PIL import Image
    device = 'cpu'
    model_path = r"C:\Users\2026029\OmniParser\weights\icon_detect\model.pt"

    som_model = get_yolo_model(model_path)

    som_model.to(device)
    print('model to {}'.format(device))

    import importlib
    # import util.utils
    # importlib.reload(utils)
    from util.utils import get_som_labeled_img, check_ocr_box, get_caption_model_processor, get_yolo_model
    caption_model_processor = get_caption_model_processor(model_name="florence2", model_name_or_path=r"C:\Users\2026029\OmniParser\weights\icon_caption_florence", device=device)
    print("This step completed")

    som_model.device, type(som_model)
    print("That step completed")
    #==END OF OMNIPARSER SETUP==


client = Groq(api_key = API_KEY)

#Old call function
'''
def call(client, query, img_base64, chat_history, feature_list):
    completion = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
        {
            "role": "user",
            "content": [
            {
                "type": "text",
                "text": (
                    f"You are an agent that controls a computer to complete tasks. "
                    f"Your task is: {query}. \n\n"
                    f"The actions you have taken so far are: {chat_history}. The list of elements on this laptop is here: {feature_list}.\n"
                    "Interpret the screenshot given. If the last action you tried did not succeed, try again with a different method.\n"
                    "Assuming all your actions are completed correctly, respond ONLY with {{ \"tool\": \"Done\", \"args\": {{}} }} if the exact task specified is complete (this is to STOP). When in doubt, assume the task is completed."
                    "If not done, choose **one** tool below and output **only** the JSON object specified.\n"
                    "Prioritize tools that don't require you to use coordinates (e.g. pressing hotkeys like delete/Ctrl-C) over tools that do (e.g. moving/clicking):\n"
                    "- Click-Tool: Click at coordinates. Output in this format {{ \"tool\": \"Click-Tool\", \"args\": {{ \"element\": \"value\" }} }}\n\n"
                    "- Type-Tool: Type text on an element (can clear first). {{ \"tool\": \"Type-Tool\", \"args\": {{ \"text\": \"value\" }} }}\n\n"
                    #"- Clipboard-Tool: Copy/paste using clipboard. {{ \"tool\": \"Clipboard-Tool\", \"args\": {{ \"action\": \"value (copy or paste)\" }} }}\n\n"
                    "- Scroll-Tool: Scroll on the screen. {{ \"tool\": \"Scroll-Tool\", \"args\": {{ \"axis\": \"horizontal/vertical\", Hello, World!\"direction\": \"up/down\" }} }}\n\n"
                    "- Drag-Tool: Drag from one point to another. {{ \"tool\": \"Drag-Tool\", \"args\": {{ \"initial_element\": \"value\", \"final_position\": \"value\" }} }}\n\n"
                    #"- Move-Tool: Move the mouse pointer. {{ \"tool\": \"Move-Tool\", \"args\": {{ \"destination\": \"value\" }} }}\n\n"
                    "- Shortcut-Tool: Press keyboard shortcuts (e.g., Ctrl+C to copy, Ctrl+V to paste). {{ \"tool\": \"Shortcut-Tool\", \"args\": {{ \"keys\": [\"a list of keys\"] }} }}\n\n"
                    "- Key-Tool: Press a single key. {{ \"tool\": \"Key-Tool\", \"args\": {{ \"key\": \"value\" }} }}\n\n"
                    #"- Wait-Tool: Wait for a short time. {{ \"tool\": \"Wait-Tool\", \"args\": {{ \"time\": \"value\" }} }}\n\n"
                    "- Launch-Tool: Open an app via start menu. {{ \"tool\": \"Launch-Tool\", \"args\": {{ \"app\": \"value\" }} }}\n\n"
                    #"- Shell-Tool: Run a PowerShell command. {{ \"tool\": \"Shell-Tool\", \"args\": {{ \"command\": \"value\" }} }}\n\n"
                    #"- Scrape-Tool: Extract full webpage content. {{ \"tool\": \"Scrape-Tool\", \"args\": {{ None }} }}\n\n"
                    #"- Script-Tool: Write and execute a script to control the computer. {{ \"tool\": \"Script-Tool\", \"args\": {{ \"script\": \"value\" }} }}\n\n"
                    "Only respond with one tool call. If unsure, ask for clarification. \n\n"
                )
            },
            {
                "type": "image_url",
                "image_url": {
                "url": img_base64
                }
            }
            ]
        }
        ],
        temperature=0,
        max_completion_tokens=1024,
        top_p=1,
        stream=False,
        response_format={"type": "json_object"},
        stop=None,
    )

    res = completion.choices[0].message
    action = json.loads(res.content)
    return action
'''

#New call function
def call(client, query, img_base64, chat_history, feature_list):
    completion = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an agent that controls a computer to complete tasks.\n"
                    "Your task is {query}. If you have already done the task, stop immediately.\n"
                    "Stop as soon as possible after the minimum number of steps.\n"
                    "To stop when the task is done, respond ONLY with {\"tool\": \"Done\", \"args\": {}}.\n"
                    "When not done, pick **one** tool for the next step and output ONLY the JSON object specified.\n"
                    "Important: If you want to type something, into a search bar for example, assume that the input for the search is not yet selected. This means you must click on it before typing. If you type and it doesn't work, it means you didn't select the input properly.\n"
                    "Tools are as follows:\n"
                    "- Click-Tool: Click at coordinates. Output in this format {{ \"tool\": \"Click-Tool\", \"args\": {{ \"element\": \"value\" }} }}\n\n"
                    "- Type-Tool: Type text on an element. Output: {{ \"tool\": \"Type-Tool\", \"args\": {{ \"text\": \"value\" }} }}\n\n"
                    "- Scroll-Tool: Scroll on the screen. {{ \"tool\": \"Scroll-Tool\", \"args\": {{ \"axis\": \"horizontal/vertical\", \"direction\": \"up/down\" }} }}\n\n"
                    "- Drag-Tool: Drag from one point to another. {{ \"tool\": \"Drag-Tool\", \"args\": {{ \"initial_element\": \"value\", \"final_position\": \"value\" }} }}\n\n"
                    "- Shortcut-Tool: Press keyboard shortcuts (e.g., Ctrl+C to copy, Ctrl+V to paste). {{ \"tool\": \"Shortcut-Tool\", \"args\": {{ \"keys\": [\"list of keys\"] }} }}\n\n"
                    "- Key-Tool: Press a single key. {{ \"tool\": \"Key-Tool\", \"args\": {{ \"key\": \"value\" }} }}\n\n"
                    "- Launch-Tool: Open an app. {{ \"tool\": \"Launch-Tool\", \"args\": {{ \"app\": \"value\" }} }}\n\n"
                    "Only respond with one tool call, strictly in JSON format as specified.\n"
                )
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            f"Your task is {query}. The actions you have taken so far are: {chat_history}.\n\n"
                            f"The list of elements on this laptop is here: {feature_list}.\n\n"
                            "Interpret the screenshot and features given. Try not to perform your last action again."
                            "Output the JSON object corresponding to the next step."
                        )
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": img_base64}
                    }
                ]
            }
        ],
        temperature=0,
        max_completion_tokens=1024,
        top_p=1,
        stream=False,
        response_format={"type": "json_object"},
        stop=None,
    )

    res = completion.choices[0].message
    action = json.loads(res.content)

    return action

def click_agent(client, feature, feature_list):
    completion = client.chat.completions.create(
        model="meta-llama/Llama-4-Maverick-17B-128E-Instruct",
        messages=[
        {
            "role": "user",
            "content": [
            {
                "type": "text",
                "text": f"You need to click on the element on this computer: {feature}. The list of elements on this laptop are {feature_list} What are the coordinates for this element?"
                +" Output in only this json format {{ \"x\": \"value\", \"y\": \"value\" }}. If the feature_list does not contain the element you are looking for, output the exact json {{ \"x\": \"-1024\", \"y\": \"-1024\" }}\n\n"
            },
            ]
        }
        ],
        temperature=0,
        max_completion_tokens=128,
        top_p=1,
        stream=False,
        response_format={"type": "json_object"},
        stop=None,
    )

    res = completion.choices[0].message
    action = json.loads(res.content)
    print(action)
    return action

def capture_screen_OLD():
    screenshot = pyautogui.screenshot()
    buffered = io.BytesIO()
    screenshot.save(buffered, format="JPEG")
    img_bytes = buffered.getvalue()
    img_base64 = base64.b64encode(img_bytes).decode("utf-8")
    return f"data:image/jpeg;base64,{img_base64}"

#New - compression is probably better
def capture_screen(max_size=(800, 800), quality=40):
    screenshot = pyautogui.screenshot()
    screenshot = screenshot.convert("RGB")
    #screenshot.thumbnail(max_size)
    buffered = io.BytesIO()
    screenshot.save(buffered, format="JPEG", quality=quality)
    img_bytes = buffered.getvalue()
    img_base64 = base64.b64encode(img_bytes).decode("utf-8")
    return f"data:image/jpeg;base64,{img_base64}"

def launch_tool(app):
    open_app(app, match_closest=True)

#Mars' suggestion: Move Omniparser into a different method. 
def vision_fallback():
    global omniParser_setUp
    if omniParser_setUp==False:
        opSetUp()
        omniParser_setUp=True
    # reload utils
    import importlib
    import utils
    importlib.reload(utils)
    
    screenshot = pyautogui.screenshot()
    screenshot.save(r"C:\Users\2026029\OneDrive - Appleby College\Grade 11\z_MISC\Certain Documents\for the AI Marketplace\screenshot.png")
    
    importlib.reload(utils)
    
    image_path = r"C:\Users\2026029\OneDrive - Appleby College\Grade 11\z_MISC\Certain Documents\for the AI Marketplace\screenshot.png"

    image = Image.open(image_path)
    image_rgb = image.convert('RGB')
    print('image size:', image.size)

    box_overlay_ratio = max(image.size) / 3200
    draw_bbox_config = {
        'text_scale': 0.8 * box_overlay_ratio,
        'text_thickness': max(int(2 * box_overlay_ratio), 1),
        'text_padding': max(int(3 * box_overlay_ratio), 1),
        'thickness': max(int(3 * box_overlay_ratio), 1),
    }
    BOX_TRESHOLD = 0.05

    ocr_bbox_rslt, is_goal_filtered = check_ocr_box(image_path, display_img = False, output_bb_format='xyxy', goal_filtering=None, easyocr_args={'paragraph': False, 'text_threshold':0.9}, use_paddleocr=True)
    text, ocr_bbox = ocr_bbox_rslt

    labeled_img, label_coordinates, parsed_content_list = get_som_labeled_img(image_path, som_model, BOX_TRESHOLD = BOX_TRESHOLD, output_coord_in_ratio=True, ocr_bbox=ocr_bbox,draw_bbox_config=draw_bbox_config, caption_model_processor=caption_model_processor, ocr_text=text,use_local_semantics=True, iou_threshold=0.7, scale_img=False, batch_size=128)
    image_data = base64.b64decode(labeled_img)


    subset = [
        {
            'content': item['content'],
            'bbox': [round(coord, 3) for coord in item['bbox']]
        }
        for item in parsed_content_list
    ]
    
    return subset

def click_tool(client, feature, subset):
    
    label = click_agent(client, feature, subset)
    
    if isinstance(label['x'],str):
        label['x']=int(label['x'])
    if isinstance(label['y'],str):
        label['y']=int(label['y'])
  
    x, y = label['x'],label['y']
    
    triedAgain=False
    
    if label['x']==-1024 and label['y']==-1024 and triedAgain==False:
        triedAgain=True
        subset=inspectTree.stable_tree()
        label = click_agent(client, feature, subset)
        
        if isinstance(label['x'],str):
            label['x']=int(label['x']) 
        if isinstance(label['y'],str):
            label['y']=int(label['y'])
        x, y = label['x'],label['y']
    
    #If the agent declares itself confused twice then resort to OmniParser
    elif label['x']==-1024 and label['y']==-1024:
        subset=vision_fallback()
        label = click_agent(client, feature, subset)
        x, y = 3200*(label['x'])+1, 2000*(label['y'])+1
        
    pyautogui.click(x, y)
    return

def type_tool(text):
    pyautogui.typewrite(text, interval=0.05)

def clipboard_tool(action):
    if action == "copy":
        pyautogui.hotkey('ctrl', 'c')
    elif action == "paste":
        pyautogui.hotkey('ctrl', 'v')

def scroll_tool(axis, direction):
    if axis == "vertical":
        if direction == "up":
            pyautogui.scroll(40)
        elif direction == "down":
            pyautogui.scroll(-40)
    elif axis == "horizontal":
        if direction == "left":
            pyautogui.hscroll(-40)
        elif direction == "right":
            pyautogui.hscroll(40)

def drag_tool(start_x, start_y, end_x, end_y):
    pyautogui.moveTo(start_x, start_y)
    pyautogui.dragTo(end_x, end_y, duration=0.5)

def move_tool(x, y):
    pyautogui.moveTo(x, y)

def shortcut_tool(keys):
    pyautogui.hotkey(keys)

def key_tool(key):
    pyautogui.press(key)

def wait_tool(seconds):
    time.sleep(seconds)

def shell_tool(command):
    result = subprocess.run(["powershell", "-Command", command], capture_output=True, text=True)
    return result.stdout

def script_tool(language, script_str):
    result = subprocess.run(
        [language, '-c', script_str],
        capture_output=True, text=True
    )
    return result.stdout

def cua(client, query):
    chat_history = []
    while True:
        screenshot_base64 = capture_screen()
        
        #Added by Mars here- seems to improve accuracy?
        all_elements=inspectTree.stable_tree()
        response = call(client, query, screenshot_base64, chat_history, all_elements)
        chat_history.append(response)
        print(response)
        if(response['tool'] == "Launch-Tool"):
            launch_tool(response['args']['app'])
        elif(response['tool'] == "Click-Tool"):
            click_tool(client, response['args']['element'], all_elements)
        elif(response['tool'] == "Type-Tool"):
            type_tool(response['args']['text'])
        elif(response['tool'] == "Clipboard-Tool"):
            clipboard_tool(response['args']['action'])
        elif(response['tool'] == "Scroll-Tool"):
            scroll_tool(response['args']['axis'], response['args']['direction'])
        elif(response['tool'] == "Drag-Tool"):
            drag_tool(response['args']['start_x'], response['args']['start_y'], response['args']['end_x'], response['args']['end_y'])
        elif(response['tool'] == "Move-Tool"):
            move_tool(response['args']['x'], response['args']['y'])
        elif(response['tool'] == "Shortcut-Tool"):
            shortcut_tool(response['args']['keys'])
        elif(response['tool'] == "Key-Tool"):
            key_tool(response['args']['key'])
        elif(response['tool'] == "Wait-Tool"):
            wait_tool(response['args']['time'])
        elif(response['tool'] == "Shell-Tool"):
            shell_output = shell_tool(response['args']['command'])
            print("Shell Output:", shell_output)
        elif(response['tool'] == "Script-Tool"):
            script_output = script_tool(response['args']['language'], response['args']['script'])
            print("Script Output:", script_output)
        elif(response['tool'] == "Done"):
            print("Task completed.")
            break

        time.sleep(1)

cua(client, "Open Google Chrome, navigate to Youtube, find videos from MrBeast and click the top result.") 
