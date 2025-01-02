query = "Find the file named report.xlsx, open it, and extract all data into a new CSV file"

            # response = client.chat.completions.create(
            #     messages=[{"role": "user", "content": command}],
            #     parameters={
            #         "intent_types": ["open_app", "close_app", "move_files", "delete_files", "open_website", "search_google", "perform_task", "write"],
            #         "return_format": "json",
            #     }
            # )

task = {
   "action": "open_app",
   "parameters": {
      "app_name": "Google Chrome"
   }
}

action = task['action']
print(action)

from algs import agent
client = agent()
# print(client.get_coordinates(task, client.action_history))
client.navigate_screen(100, 200)