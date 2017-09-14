import logging
import webbrowser
import threading
import discord
import aioconsole
from src.JSONDataFile import JSONDataFile
from enum import Enum

''' The Rankings of user permissions ranging from lowest to highest.
DEFAULT - Default permissions, no interaction allowed with this bot unless specified
USER - Permission to execute any command
SUPERUSER - Full permissions to use any command.
'''
class Permission(Enum):
    DEFAULT = 0 # The lowest default permission for any user in a server
    USER = 1 # The middle permission, allows a user to use general commands like running a script
    SUPERUSER = 2 # The highest permission, allows a user to use any command

# Log discord debug information
logging.basicConfig(level=logging.INFO)

######################### Constants #########################
# JSON files used by the bot to access and write data
PROPERTIES_FILE = JSONDataFile("properties.json", {
    'token': None
})
SCRIPTS_FILE = JSONDataFile("scripts.json")
USERS_FILE = JSONDataFile("users.json", {
    "superusers": [],
    "users": []
})
C_PREFIX = '$' # The prefix for all commands
TOKEN = PROPERTIES_FILE.get_data()['token'] # the token for the bot

######################### Variables #########################
isConnected = False # Is the client logged in and connected?
isRunning = True # Is the client running
hasSuperuser = len(USERS_FILE.get_data()['superusers']) > 0 # is there any superusers yet?
client = discord.Client()

# Returns the permission level of the user
def getPermissionLevel(user_id):
    users = USERS_FILE.get_data()
    if (user_id in users['superusers']):
        return Permission.SUPERUSER
    if (user_id in users['users']):
        return Permission.USER
    return Permission.DEFAULT

async def run_command(message, fromConsole=False):
    '''If run from console, then make message string simply the message sent in
       However, if its not (ex. message sent through the client), then the
       message string is stored in message.content. This is done to simplify message
       checks
    '''
    # Ignore messages written by the bot (itself) to prevent spamming
    if not fromConsole:
        if message.author.id == client.user.id:
            return

    # Get permission level and string of message
    permissionLevel = Permission.DEFAULT
    messageString = ''
    if fromConsole:
        permissionLevel = Permission.SUPERUSER
        messageString = message
    else:
        permissionLevel = getPermissionLevel(message.author)
        messageString = message.content

    # Commands that can be executed by anyone or anyone with higher permission
    if (permissionLevel.value >= Permission.DEFAULT.value):
        if (messageString.startswith(C_PREFIX + "test")):
            if fromConsole:
                print("It works!")
            else:
                await client.send_message(message.channel, "It works!")
            return
    # Commands that can be executed by anyone with the permission of USER or any higher permission
    if (permissionLevel.value >= Permission.USER.value):
        pass
    # Commands that can be executed by any superuser
    if (permissionLevel.value == Permission.SUPERUSER.value):
        # Logs the bot out, and saves any other data
        if (messageString.startswith(C_PREFIX + "logout")):
            if not fromConsole:
                await client.send_message(message.channel, "Logging out ...")
            print("Logging out.")
            client.logout()
            # write any data and close
            PROPERTIES_FILE.close()
            SCRIPTS_FILE.close()
            USERS_FILE.close()
            exit(0)
    if (fromConsole):
        print("Unknown command")
    else:
        await client.send_message(message.channel, "Unknown command or you do not have permission to use that command")

'''This is the console that allows the owner who is running the server to always have permission
as a superuser.
'''
async def console():
    while True:
        text = await aioconsole.ainput('$ ')
        command = '$' + text.strip()
        await run_command(command, fromConsole=True)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    print("To add the bot to your server, open the link below:\n"
          "https://discordapp.com/oauth2/authorize?client_id={}&scope=bot&permissions=0"
          .format(client.user.id))
    # Update token
    p_json = PROPERTIES_FILE.get_data()
    p_json['token'] = TOKEN
    PROPERTIES_FILE.set_data(p_json)
    # Make user add self as a superuser
    if (not hasSuperuser):
        first_superuser = input("Add yourself as a superuser (input user id): ")
        users = USERS_FILE.get_data()
        users['superusers'].append(first_superuser)
    isConnected = True
    # Enable console to run for host to type commands through while bot is running
    await console()

@client.event
async def on_message(message):
    await run_command(message)

"""
On startup first check if there is a server token that has been established.
if not, allow the user to set it via command-line
"""
if (not TOKEN):
    isValid = False
    TOKEN = input("Enter the app bot user token: ")
try:
    client.run(TOKEN)
    #client.run(TOKEN)
except discord.LoginFailure:
    print("Invalid token. Setup your bot and get its token at: https://discordapp.com/developers under MyApps->YourApp")

# Close the client and free it of resources
client.logout()
print("Client logged out")
exit(0)
