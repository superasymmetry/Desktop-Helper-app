import winreg
import pyautogui
import os
import webbrowser
import pytesseract
import base64
import json
from PIL import Image
from groq import Groq
import time

class Agent():
    def __init__(self):
        self.action_history = []
        self.task = ""

        # get api key
        basedir = os.path.dirname(os.path.abspath(__file__))
        folder_path = os.path.join(basedir,'config.json')
        with open((folder_path), "rb") as config_file:
            config = json.load(config_file)
        self.api_key = config["api_key"]
        # create groq client
        self.client = Groq(
            api_key = self.api_key,
        )

        self.task_library = {
            "type_text": self.type,
            "right_click": self.right_click,
            "left_click": self.left_click,
            "vertical_scroll": self.vertical_scroll,
            "horizontal_scroll": self.horizontal_scroll,
        }

        self.options = [
            {
                "action": "type text",
                "text": "some_text"  # Replace "some_text" with your desired text
            },
            {
                "action": "left click",
                "x": "replace with NUMBER FROM 1-2879",  
                "y": "replace with NUMBER FROM 1-1919" 
            },
            {
                "action": "left click",
                "x": "replace with NUMBER FROM 1-2879",  
                "y": "replace with NUMBER FROM 1-1919" 
            },
            {
                "action": "drag cursor",
                "x": "replace with NUMBER FROM 1-2879",
                "y": "replace with NUMBER FROM 1-1919"
            },
            {
                "action": "vertical scroll",
                "amount": "scroll_n_clicks"  # Replace "scroll_n_clicks" with the amount to scroll
            },
            {
                "action": "horizontal scroll",
                "amount": "scroll_n_clicks"  # Replace "scroll_n_clicks" with the amount to scroll
            }
        ]

    def capture_screen(self):
        screenshot = pyautogui.screenshot()
        basedir = os.path.dirname(os.path.abspath(__file__))
        file_dir = os.path.join(basedir, "files")
        screenshot.save(os.path.join(file_dir,"screenshot.png"))
        return file_dir+"/screenshot.png"
    
    def delete_capture(self, image_path):
        os.remove(image_path)

    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def type(self, text):
        pyautogui.write(text)
        time.sleep(0.3)

    def left_click(self, x, y):
        pyautogui.click(x, y)
        time.sleep(0.2)

    def right_click(self, x, y):
        pyautogui.rightClick(x, y)
        time.sleep(0.2)

    def drag_cursor(self, x, y):
        pyautogui.dragTo(x, y, 0.5, button='left')
        time.sleep(0.2)

    def horizontal_scroll(self, amount):
        pyautogui.hscroll(amount)
        time.sleep(0.2)

    def vertical_scroll(self, amount):
        pyautogui.scroll(amount)
        time.sleep(0.2)

    def execute(self, command):
        if "right click" in command:
            c = json.loads(command)
            x = int(c["x"])
            y = int(c["y"])
            print(f"right clicking at {x},{y}")
            self.right_click(x, y)
        elif "left click" in command:
            c = json.loads(command)
            x = int(c['x'])
            y = int(c['y'])
            print(f"left clicking at {x},{y}")
            self.left_click(x, y)
        elif "drag cursor" in command:
            c = json.loads(command)
            x = int(c['x'])
            y = int(c['y'])
            print(f"dragging cursor to {x},{y}")
            self.drag_cursor(x, y)
        elif "vertical scroll" in command:
            c = json.loads(command)
            amount = int(c['amount'])
            print(f"scrolling {amount} times")
            self.vertical_scroll(amount)
        elif "horizontal scroll" in command:
            c = json.loads(command)
            amount = int(c['amount'])
            print(f"scrolling {amount} times")
            self.horizontal_scroll(amount)
        elif "type text" in command:
            c = json.loads(command)
            text = c['text']
            print(f"typing text: {text}")
            self.type_text(text)

    def call(self,text,action_history):
        chat_completion = self.client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are the user of this laptop."
                },
                # Set a user message for the assistant to respond to.
                {
                    "role": "user",
                    "content": f"What is the next step in performing this task {text} given the message history of {action_history}? Output your response in JSON format. You have these options to output: {self.options}",
                }
            ],
            model="llama3-8b-8192",
            temperature=0,
            max_tokens=800,
            # Controls diversity via nucleus sampling: 0.5 means half of all
            # likelihood-weighted options are considered.
            top_p=1,

            # A stop sequence is a predefined or user-specified text string that
            # signals an AI to stop generating content, ensuring its responses
            # remain focused and concise. Examples include punctuation marks and
            # markers like "[end]".
            stop=None,

            # If set, partial message deltas will be sent.
            stream=False,
        )

        return chat_completion.choices[0].message.content
    
    def get_intent_image(self, task,action_history):
        path = self.capture_screen()
        encode_image = self.encode_image(path)

        completion = self.client.chat.completions.create(
            model="llama-3.2-90b-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"What is the immediate next step in performing this task {task} given the action history of {action_history}? You have these options to output: {self.options}. Output your response in JSON format with \"action\" and \"parameters\". If the task is finished, simply output STOPSTOPSTOP",
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                 "url": f"data:image/jpeg;base64,{encode_image}",
                            }
                        }
                    ]
                }
            ],
            temperature=0,
            max_tokens=800,
            top_p=1,
            stream=False,
            response_format={"type": "json_object"},
            stop=None,
        )

        # delete image
        self.delete_capture(path)

        return completion.choices[0].message.content


    def get_coordinates(self, task,action_history):
        path = self.capture_screen()
        encode_image = self.encode_image(path)

        completion = self.client.chat.completions.create(
            model="llama-3.2-90b-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"What are the coordinates on the screen the mouse should move to in order to execute the next step in the command {task} given the action history of {action_history}? Don't use JSON; just format the output as 2 numbers as the X and Y coordinates, separated by a comma. Do not move the cursor to the corner of the screen.",
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                 "url": f"data:image/jpeg;base64,{encode_image}",
                            }
                        }
                    ]
                }
            ],
            temperature=0,
            max_tokens=800,
            top_p=1,
            stream=False,
            response_format={"type": "json_object"},
            stop=None,
        )

        # delete image
        self.delete_capture(path)

        return completion.choices[0].message.content
    
    def tool_use(self, query):
        messages = [
            {
                "role": "system",
                "content": "You are a calculator assistant. Use the calculate function to perform mathematical operations and provide the results.",
            },
            {
                "role": "user",
                "content": query,
            }
        ]
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "calculate",
                    "description": "Evaluate a mathematical expression",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "expression": {
                                "type": "string",
                                "description": "The mathematical expression to evaluate",
                            }
                        },
                        "required": ["expression"],
                    },
                },
            }
        ]
        response = self.client.chat.completions.create(
            model="llama3-groq-70b-8192-tool-use-preview",
            messages=messages,
            tools=tools,
            tool_choice="auto",
            max_tokens=4096
        )
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls
        if tool_calls:
            messages.append(response_message)
            for tool_call in tool_calls:
                function_args = json.loads(tool_call.function.arguments)
                function_response = self.execute_command(function_args.get("expression"))
                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": "calculate",
                        "content": function_response,
                    }
                )
            second_response = self.client.chat.completions.create(
                model="llama3-groq-70b-8192-tool-use-preview",
                messages=messages
            )
            return second_response.choices[0].message.content
        return response_message.content
    
