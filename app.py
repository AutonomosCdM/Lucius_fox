import os
import asyncio
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from agents import LuciusFox

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Initialize Slack client
SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
slack_client = WebClient(token=SLACK_BOT_TOKEN)

# Initialize Lucius Fox
lucius = LuciusFox()

def get_bot_user_id():
    try:
        response = slack_client.auth_test()
        return response["user_id"]
    except SlackApiError as e:
        print(f"Error getting bot user ID: {e}")
        return None

BOT_USER_ID = get_bot_user_id()

async def handle_message(text: str, channel_id: str, thread_ts: str = None, user: str = None):
    try:
        # Create context for the message
        context = {
            'channel': channel_id,
            'thread_ts': thread_ts,
            'user': user,
            'ts': thread_ts
        }

        # Get response from Lucius
        response = await lucius.process(text, context)

        # Send the response back to Slack
        slack_client.chat_postMessage(
            channel=channel_id,
            thread_ts=thread_ts,
            text=response
        )
    except Exception as e:
        print(f"Error handling message: {e}")
        slack_client.chat_postMessage(
            channel=channel_id,
            thread_ts=thread_ts,
            text="I encountered an error while processing your request."
        )

@app.route('/slack/events', methods=['POST'])
def slack_events():
    data = request.json
    
    # Handle URL verification challenge
    if data.get('type') == 'url_verification':
        return jsonify({'challenge': data.get('challenge')})
    
    # Handle events
    if data.get('type') == 'event_callback':
        event = data.get('event', {})
        
        # Handle message events
        if event.get('type') == 'app_mention':
            channel_id = event.get('channel')
            thread_ts = event.get('thread_ts', event.get('ts'))
            text = event.get('text')
            user = event.get('user')
            
            # Remove the bot mention from the text
            if BOT_USER_ID:
                text = text.replace(f'<@{BOT_USER_ID}>', '').strip()
            
            # Handle the message asynchronously
            asyncio.run(handle_message(text, channel_id, thread_ts, user))
            
        return jsonify({'status': 'ok'})
    
    return jsonify({'status': 'error', 'message': 'Unhandled event type'})

if __name__ == '__main__':
    app.run(port=3000, debug=True)
