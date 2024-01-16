import slack
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask
from slackeventsapi import SlackEventAdapter

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(os.environ["SIGNING_SECRET"], "/slack/events", app)

client = slack.WebClient(token=os.environ["SLACK_TOKEN"])

#* WHITELISTED USERS (Nour, Noah and Bot)
whitelisted_users = ["U06C38LSP1Q", "U06CCMLG5C2", None]

messages_set = set()
ts_to_delete = set()

@slack_event_adapter.on("message")
def event(payload):
    
    event = payload.get("event", {})
    channel_id = event.get("channel")
    user_id = event.get("user")
    text = event.get("text")
    timestamp = event.get("ts")
    event_type = event.get("type")

    if len(text) <= 1:
        client.chat_delete(channel=channel_id, ts=timestamp)

    #elif not user_id in whitelisted_users and channel_id == "C06C5Q3GF5J":
        #messages_set.add(timestamp)

        #for ts in messages_set:
            
            #ts_to_delete.add(ts)
            #try:
                #client.chat_delete(channel=channel_id, ts=ts)
            #except Exception as e:
                #//print(e)
                #pass
        
        #try:
            #while len(messages_set) != 0:
                #messages_set.difference_update(ts_to_delete)
            
            #ts_to_delete.discard(ts_to_delete[0])

        #except:
            #pass
        

if __name__ == "__main__":
    app.run(debug=True)
