import slack 
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request, Response
from slackeventsapi import SlackEventAdapter
import string

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(os.environ["SIGNING_SECRET"], "/slack/events", app)

client = slack.WebClient(token=os.environ['SLACK_BOT_TOKEN'])   
BOT_ID = client.api_call("auth.test")['user_id']

#* WHITELISTED USERS (Bot)
whitelisted_users = [None]

WelcomeMessages = {}
message_counts = {}

messages_set = set()
ts_to_delete = set()

#! test bad words
BAD_WORDS = ['bad', 'stop', 'dumb', 'stupid']

class WelcomeMessage:
    
    
    START_TEXT = {
        'type': 'section',
        'text': {
        'type': 'mrkdwn',
        'text': (
            'Welcome to this awesome channel! \n\n'
            '*Get started my completing some tasks*'
        )}
    }
    DIVIDER = {'type': 'divider'}    
    def __init__(self, channel, user):
        self.channel = channel
        self.user = user
        self.icon_emoji = ':robot_face:'
        self.timestamp = ''
        self.completed = False
        
    def get_message(self):
        return {
            'ts': self.timestamp,
            'channel': self.channel,
            'username': 'Welcome Robot!',
            'icon_emoji': self.icon_emoji,
            'blocks': [
                self.START_TEXT,
                self.DIVIDER,
                self._get_reaction_task()
            ]
        }
        
    def _get_reaction_task(self):
        checkmark = ':white_check_mark:'
        if not self.completed:
            checkmark = ':white_large_square:'

        text = f'{checkmark} *React to this message!*'

        return {'type': 'section', 'text': {'type': 'mrkdwn', 'text': text}}

def send_welcome_message(channel, user):
    if channel not in WelcomeMessages:
        WelcomeMessages[channel] = {}

    if user in WelcomeMessages[channel]:
        return

    welcome = WelcomeMessage(channel, user)
    message = welcome.get_message()
    response = client.chat_postMessage(**message)
    welcome.timestamp = response['ts']
    
    WelcomeMessages[channel][user] = welcome

def check_if_bad_words(message):
    msg = message.lower()
    msg = msg.translate(str.maketrans('', '', string.punctuation))
    
    return any(word in msg for word in BAD_WORDS)

    

@slack_event_adapter.on('message')
def message(payload):
    event = payload.get("event", {})
    channel_id = event.get("channel")
    user_id = event.get("user")
    text = event.get("text")
    timestamp = event.get("ts")
    event_type = event.get("type")
    
    if user_id != None and BOT_ID != user_id:
        if user_id in message_counts:
            message_counts[user_id] += 1
        else:
            message_counts[user_id] = 1
        
        if text.lower() == 'welcome_message.test':
            send_welcome_message(f'@{user_id}', user_id)
            
        elif check_if_bad_words(text):
            ts = event.get('ts')
            client.chat_postMessage(
                channel=channel_id, thread_ts=ts, text = "That is a bad word!(TESTING)")