import discord
import os
from dotenv import load_dotenv
import requests
import json
import response 
import shutil
# Load environment variables from a .env file
load_dotenv()

# Get the Discord bot token from the .env file
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN not found in environment variables.")

# Target user ID to send the message to
TARGET_USER_ID = 877449570840354856
#787708226916319242

# File to store channel information to avoid repeated DM creation
CHANNEL_STORE = "channels.json"


def saveChannelId(user_id, channel_id):
    """Save the user-channel mapping to a file."""
    if os.path.exists(CHANNEL_STORE):
        with open(CHANNEL_STORE, "r") as file:
            channels = json.load(file)
    else:
        channels = {}

    channels[str(user_id)] = channel_id

    with open(CHANNEL_STORE, "w") as file:
        json.dump(channels, file)


def getSavedChannelId(user_id):
    """Retrieve the channel ID for a user from the file."""
    if os.path.exists(CHANNEL_STORE):
        with open(CHANNEL_STORE, "r") as file:
            channels = json.load(file)
            return channels.get(str(user_id))
    return None


def getMyUsername(token):
    """Fetch and return the bot's username."""
    url = "https://discord.com/api/v9/users/@me"
    headers = {"Authorization": token}

    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        user_data = r.json()
        username = f"{user_data['username']}#{user_data['discriminator']}"
        return username
    else:
        print(f"Failed to fetch your username. Status Code: {r.status_code}")
        return None


def createOrFetchDmChannel(token, user_id):
    """Create or fetch an existing DM channel for the user."""
    # Check if a channel already exists in storage
    channel_id = getSavedChannelId(user_id)
    if channel_id:
        return channel_id

    # Otherwise, create a new DM channel
    data = {"recipient_id": user_id}
    headers = {"Authorization": token}

    r = requests.post('https://discord.com/api/v9/users/@me/channels', json=data, headers=headers)
    print(f"Create DM Channel status code: {r.status_code}")

    if r.status_code == 200:
        channel_id = r.json()['id']
        saveChannelId(user_id, channel_id)
        print(f"Created new DM channel: {channel_id}")
        return channel_id
    else:
        print("Failed to create a DM channel.")
        return None


def getMessageHistory(token, channel_id, limit=50):
    """Fetch and print message history from a channel."""
    url = f'https://discord.com/api/v9/channels/{channel_id}/messages?limit={limit}'
    headers = {"Authorization": token}
    conversation = []
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        messages = r.json()
        for msg in messages:
            convo = ""
            convo += f"{msg['author']['username']}: {msg['content']}\n"
            conversation.append(convo)
        return ''.join(conversation[::-1])
    else:
        print(f"Failed to fetch message history. Status Code: {r.status_code}")


def sendMessage(token, channel_id, message):
    """Send a message to a channel."""
    url = f'https://discord.com/api/v8/channels/{channel_id}/messages'
    data = {"content": message}
    headers = {"Authorization": token}

    r = requests.post(url, data=data, headers=headers)
    print(f"Message send status code: {r.status_code}")


# MAIN SCRIPT EXECUTION
if __name__ == "__main__":
    # Step 1: Fetch your own username
    my_username = getMyUsername(DISCORD_TOKEN)

    # Step 2: Create or fetch a DM channel with the target user
    channel_id = createOrFetchDmChannel(DISCORD_TOKEN, TARGET_USER_ID)

    if channel_id:
        # Step 3: Fetch the last 50 messages in the DM channel
        message = response.generate_text(getMessageHistory(DISCORD_TOKEN, channel_id, limit=20),my_username)
        # Step 4: Send a message after reading the history
        # message = "Hello! Sending this message after analyzing the message history."
        message.replace('"','')
        # sendMessage(DISCORD_TOKEN, channel_id, message)
    else:
        print("Failed to establish a DM channel.")

        # Remove the __pycache__ directory if it exists
    try:
        folder_path = '__pycache__'
        shutil.rmtree(folder_path)
        print(f"Folder {folder_path} and all its contents have been removed.")
    except FileNotFoundError:
        print(f"Folder {folder_path} not found.")
    except Exception as e:
        print(f"Error: {e}")    