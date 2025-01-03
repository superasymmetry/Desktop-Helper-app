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
            else:
                client.execute(command)

        except KeyboardInterrupt:
            exit()
        