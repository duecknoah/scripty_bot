"""Scripty-Bot is a simple bot for Discord that does what you need it to
"""
import os.path
# Support for modification in file path
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import discord
import aioconsole
import logging
from src.file import files
import src.user.permissions as permissions
import src.user.commands as commands
import src.file_functions as file_functions
import src.command_functions as command_func
from src import C_PREFIX

# Initialization stuff
client = discord.Client()
TOKEN = files.properties_file.get_data()['token']  # the token for the bot


def extract_message_data(message, FROM_CONSOLE=False):
    """Extracts data from the message string and returns the following tuple:
       (message_string, permission_level, is_command)

       message_string (str) - text of the message sent
       permission_level (permissions.PermissionLevel.*) - the permitted level of the user who sent the message
       is_command (bool) - is the message a command?
    """
    if FROM_CONSOLE:
        permission_level = permissions.PermissionLevel.SUPERUSER
        message_string = message
    else:
        permission_level = file_functions.get_user_permission_level(
            message.author.id)
        message_string = message.content

    # It is considered a command if the message string begins with the prefix
    #   ex. $example command
    #   Where the '$' is the prefix in this case
    is_command = message_string.startswith(C_PREFIX)

    # Remove the prefix as we don't want it in our way now
    message_string = message_string[1:]
    return message_string, permission_level, is_command


async def run_command(message, FROM_CONSOLE=False):
    '''If run from console, then make message string simply the message sent in
       However, if its not (ex. message sent through the client), then the
       message string is stored in message.content. This is done to simplify message
       checks
    '''

    # Ignore messages written by the bot (itself) to prevent spamming
    if not FROM_CONSOLE:
        if message.author.id == client.user.id:
            return

    # Extract message data
    message_string, permission_level, is_command = extract_message_data(message, FROM_CONSOLE)

    if not is_command:
        return

    ############################## Default Commands ##########################
    # Loop through all of the commands in the commands list
    for command in commands.get_commands_as_list():
        # Check if the message typed matches a commands arguments and
        # the users minimum permissions required to use it
        try:
            match_result = command.matches(message_string, permission_level)
            if match_result is not None and command.function is not None:
                cmd_args = command_func.CommandArgs(
                    client, message, match_result, permission_level, FROM_CONSOLE
                )
                await command.function(cmd_args)
                return
        except permissions.PermissionDeniedError as e:
            await command_func.reply_simple(client, e.strerror,
                                            None if FROM_CONSOLE else message.channel)

'''This is the console that allows the owner who is running the server to always have permission
as a superuser.
'''
async def console():
    while True:
        text = await aioconsole.ainput('$ ')
        command = '$' + text.strip()
        if command == '$':
            continue
        await run_command(command, FROM_CONSOLE=True)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    print("To add the bot to your server, open the link below:\n"
          "https://discordapp.com/oauth2/authorize?client_id={}&scope=bot&permissions=43008"
          .format(client.user.id))
    # Update token
    p_json = files.properties_file.get_data()
    p_json['token'] = TOKEN
    files.properties_file.set_data(p_json)
    # Make user add self as a superuser
    if len(files.users_file.get_data()['superusers']) == 0:
        first_superuser = input(
            "Add yourself as a superuser (input user id): "
        )
        users = files.users_file.get_data()
        users['superusers'].append(first_superuser)
    # Enable console to run for host to type commands through while bot is
    # running
    await console()


@client.event
async def on_message(message):
    await run_command(message)

"""
On startup first check if there is a server token that has been established.
if not, allow the user to set it via command-line
"""
if not TOKEN:
    isValid = False
    TOKEN = input("Enter the app bot user token: ")
try:
    logging.basicConfig(level=logging.INFO)  # Log discord debug information
    client.run(TOKEN)
except discord.LoginFailure:
    print("Invalid token. "
          "Setup your bot and get its token at: "
          "https://discordapp.com/developers under MyApps->YourApp")

    # Close the client and free it of resources
    client.logout()
    print("Client logged out")
    exit(0)
