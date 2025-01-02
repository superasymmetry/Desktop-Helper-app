import winreg
import pyautogui
import os
import webbrowser
import pytesseract
import base64
import json
from PIL import Image
from groq import Groq

class agent():
    def __init__(self):
        self.action_history = []
        self.task = ""
        basedir = os.path.dirname(os.path.abspath(__file__))
        folder_path = os.path.join(basedir,'config.json')
        with open((folder_path), "rb") as config_file:
            config = json.load(config_file)
        self.api_key = config["api_key"]
        self.client = Groq(
            api_key = self.api_key,
        )

        self.task_library = {
            "open_app": self.open_app,
            "close_app": self.close_app,
            "search_google": self.search_google,
            "move_files": self.move_files,
            "delete_files": self.delete_files,
            "open_website": self.open_website,
            "navigate_screen": self.navigate_screen,
        }

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

    def find_element_on_screen(self, element_text, screen_image):
        text_data = pytesseract.image_to_string(screen_image)
        if element_text in text_data:
            return True
        return False

    def open_app(self, app_name):
        app = app_name.split(" ")
        name = ""
        for i, word in enumerate(app):
            name += "\\" + word 

        # Construct the path to the executable
        path = rf"C:\Program Files{name}\Application\{app[-1]}.exe"

        # Check if the executable exists
        if os.path.exists(path):
            os.system(f'start "" "{path}"')
            return f"Opened {app_name}"
        else:
            return f"Error: {path} not found"


    def close_app(self, app_name):
        os.system(f'taskkill /im {app_name}.exe')
        return f"Closed {app_name}"

    def move_files(self, source, destination):
        os.system(f'copy {source} {destination}')
        return f"Moved {source} to {destination}"

    def delete_files(self, file_path):
        os.remove(file_path)
        return f"Deleted {file_path}"

    def open_website(self, website_url):
        webbrowser.open(website_url)
        return f"Opened {website_url}"

    def search_google(self, query):
        webbrowser.open(f"https://www.google.com/search?q={query}")
        return f"Searching Google for {query}"

    def execute_command(self, task):
        try:
            print("Executing...... ", task)
            task = json.loads(task)
            action = task['action']
            print("action", action)
            parameters = task['parameters']
            if "open_app" in action:
                print("here")
                self.open_app(parameters['app_name'])
                return f"Opened {parameters['app_name']}"
            elif "close_app" in action:
                self.close_app(parameters['app_name'])
                return f"Closed {parameters['app_name']}"
            elif "move_files" in action:
                self.move_files(parameters['source'], parameters['destination'])
                return f"Moved {parameters['source']} to {parameters['destination']}"
            elif "delete_files" in action:
                self.delete_files(parameters['file_path'])
                return f"Deleted {parameters['file_path']}"
            elif "open_website" in action:
                self.open_website(parameters['url'])
                return f"Opened {parameters['url']}"
            else:
                return f"Error: Action {action} not found"
        except Exception as e:
            return f"Error: {e}"
    
    def navigate_screen(self, x, y):
        pyautogui.click(x, y)

    # extract software list
    def get_installed_apps():
        apps = []
        registry_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
        try:
            registry_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,registry_path)
            for i in range(0,winreg.QueryInfoKey(registry_key)[0]):
                app_name = winreg.EnumKey(registry_key,i)
                app_path = f"{registry_path}\\{app_name}"
                app_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,app_path)
                try:
                    display_name,_=winreg.QueryValueEx(app_key,"DisplayName")
                    apps.append(display_name)
                except FileNotFoundError:
                    pass
        except Exception as e:
            print(f"Error: {e}")
        
        return apps

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
                    "content": f"What is the next step in performing this task {text} given the message history of {action_history}?",
                }
            ],
            model="llama3-8b-8192",
            temperature=0,
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
                            "text": f"What is the immediate next step in performing this task {task} given the action history of {action_history}? You can use the following steps or create your own: {self.task_library}. Write the next step in JSON format. If the task is finished, simply output STOPSTOPSTOP",
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
    
