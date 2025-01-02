import json
import os
from groq import Groq
import webbrowser
import pyautogui
from agent import Agent


if __name__=="__main__":

    text = input("prompt: ")
    text += "Output in JSON form. (Example: {\"action\": \"search_google\", \"parameters\": {\"query\": \"latest news\"}})"
    
    # initialize agent
    client = Agent()
    command = client.call(text, client.action_history)
    print('Press Ctrl-C to quit.')

    while(True):
        # run model
        try:
            client.action_history.append(command)
            command = client.get_intent_image(command, client.action_history)
            print("Executing... \n", command)
            if "STOPSTOPSTOP" in command:
                print("The task is finished.")
                break
            elif "navigate_screen" in command:
                coords = client.get_coordinates(command, client.action_history)
                coords = json.loads(coords)
                x = int(coords["x"])
                y = int(coords["y"])
                print(f"navigating to screen: {x}, {y}")
                pyautogui.click(x, y)
            elif "right click" in command:
                c = json.loads(command)
                x = int(c["x"])
                y = int(c["y"])
                print(f"right clicking at {x},{y}")
                client.right_click(x, y)
            elif "left click" in command:
                c = json.loads(command)
                x = int(c['x'])
                y = int(c['y'])
                print(f"left clicking at {x},{y}")
                client.left_click(x, y)
            elif "vertical scroll" in command:
                c = json.loads(command)
                amount = int(c['amount'])
                print(f"scrolling {amount} times")
                client.vertical_scroll(amount)
            elif "horizontal scroll" in command:
                c = json.loads(command)
                amount = int(c['amount'])
                print(f"scrolling {amount} times")
                client.horizontal_scroll(amount)
            elif "type text" in command:
                c = json.loads(command)
                text = c['text']
                print(f"typing text: {text}")
                client.type_text(text)
            else:
                # execute command
                client.execute_command(command)

        except KeyboardInterrupt:
            exit()
        