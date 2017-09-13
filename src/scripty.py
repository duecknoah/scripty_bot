import asyncio
import discord
import logging
import webbrowser
from src.JSONDataFile import JSONDataFile

# Log discord debug information
logging.basicConfig(level=logging.INFO)
# JSON files used by the bot to access and write data
PROPERTIES_FILE = JSONDataFile("properties.json", {'token': None})
SCRIPTS_FILE = JSONDataFile("scripts.json")
USERS_FILE = JSONDataFile("users.json")
"""
On startup first check if there is a server token that has been established.
if not, allow the user to set it via command-line
"""
isConnected = False # Is the client logged in and connected?
client = discord.Client()

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    print("To add the bot to your server, open the link below:\n"
          "https://discordapp.com/oauth2/authorize?client_id={}&scope=bot&permissions=0".format(client.user.id))
    pJSON = PROPERTIES_FILE.get_data()
    pJSON['token'] = TOKEN
    PROPERTIES_FILE.set_data(pJSON)
    isConnected = True

@client.event
async def on_message(message):
    if message.content.startswith('!test'):
        await client.send_message(message.server, "Yo")

# Setup and starting of client
TOKEN = PROPERTIES_FILE.get_data()['token'] # the token for the bot
if (TOKEN == None):
    isValid = False
    TOKEN = input("Enter the app bot user token: ")
try:
    client.run(TOKEN)
except discord.LoginFailure:
    print("Invalid token. Setup your bot and get its token at: https://discordapp.com/developers")

# Close the client and free it of resources
client.logout()
print("Client logged out")
exit(0)