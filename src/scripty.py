"""Scripty-Bot is a bot for Discord that allows users to run scripts on the host

    TODO:
        - Add ability to add and remove scripts
        - Allow execution of scripts via command
        - Show a list of all scripts
        - Show a list of currently running scripts
        - Kill specific running scripts via command
"""
import discord
import aioconsole
import logging
from src.JSONDataFile import JSONDataFile
import src.user.permissions as permissions
import src.user.commands as commands
# Support for modification in file path
import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Log discord debug information
logging.basicConfig(level=logging.INFO)

######################### Constants #########################
# JSON files used by the bot to access and write data

PROPERTIES_FILE = JSONDataFile("../data/properties.json", {
    'token': None
})
SCRIPTS_FILE = JSONDataFile("../data/scripts.json")
USERS_FILE = JSONDataFile("../data/users.json", {
    "superusers": [],
    "users": []
})
C_PREFIX = '$' # The prefix for all commands
TOKEN = PROPERTIES_FILE.get_data()['token'] # the token for the bot
HAS_SUPERUSER = len(USERS_FILE.get_data()['superusers']) > 0 # is there any superusers yet?

######################### Variables #########################

is_connected = False # Is the client logged in and connected? pylint: disable=invalid-name
is_running = True # Is the client running. pylint: disable=invalid-name
client = discord.Client()

# Returns the permission level of the user
def get_user_permission_level(user_id):
    user_perms_list = USERS_FILE.get_data()
    for p in user_perms_list:
        if user_id in user_perms_list[p]:
            return permissions.get_permission_of_label(p[:-1])
    return permissions.PermissionLevel.DEFAULT

""" Converts the given id to a user, returning None if that user couldn't be found
:returns user or None
"""
def id_to_user(id):
    for user in client.get_all_members():
        if user.id == id:
            return user
    return None

def set_user_permission(user_id, permission):
    """ Sets the user (id) to the desired permission level (permission).
    It will return a string that can be used as a
    reply message for either the console or server
    :returns str
    """
    user_to_add = id_to_user(user_id)  # set when id is validated
    user_is_valid = False # default

    # Validate that the user exists
    if user_to_add != None:
        user_is_valid = True

    if not user_is_valid:
        return "Invalid or non-existant user. ex. {} @exampleuser"\
            .format(permissions.get_label_of_permission(permission))

    # Check if the users permission level already is what we are trying to set it to
    current_permission = get_user_permission_level(user_id)

    if current_permission == permission:
        return "{} is already a {}".format(user_to_add.name,
                                           permissions.get_label_of_permission(permission))

    # Remove current permission if we are not currently just the default permission,
    # (the default permission users are not stored in the users file)
    # we don't want the user to have multiple permission levels
    # in the users file.
    if current_permission != permissions.PermissionLevel.DEFAULT:
        keyInFile = permissions.get_label_of_permission(current_permission) + 's'
        if user_id in USERS_FILE.get_data()[keyInFile]:
            USERS_FILE.get_data()[keyInFile].remove(user_id)

    # Set the permission of the user
    # Note that we do not add users with the default permission to the users file.
    # As the default permission means at least same permission as everyone on the server
    if permission != permissions.PermissionLevel.DEFAULT:
        permission_save_name = permissions.get_label_of_permission(permission) + 's'
        USERS_FILE.get_data()[permission_save_name].append(user_id)
    return "{} is now a {}".format(
        user_to_add.name,
        permissions.get_label_of_permission(permission))

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

    # Get permission level and string of message
    permission_level = permissions.PermissionLevel.DEFAULT
    message_string = ''
    message_starting_index = len(C_PREFIX)

    if FROM_CONSOLE:
        permission_level = permissions.PermissionLevel.SUPERUSER
        message_string = message
    else:
        permission_level = get_user_permission_level(message.author.id)
        message_string = message.content

    # If the message doesn't start with the prefix, return
    if not message_string.startswith(C_PREFIX):
        return

    # Remove the prefix as we don't want it in our way now
    message_string = message_string[1:]
    default_commands = commands.DefaultCommands

    ############################## Default Command checks and running ##############################
    # Help command
    help_command_match = default_commands.HELP.matches(message_string, permission_level)
    if help_command_match is not None:
        commands_list = None
        commands_str_tidy = ''
        note = '*NOTE that all commands begin with \'$\'*'
        if FROM_CONSOLE:
            commands_list = commands.get_permitted_commands_for(
                permissions.PermissionLevel.SUPERUSER)
        else:
            commands_list = commands.get_permitted_commands_for(permission_level)
        for i in commands_list:
            commands_str_tidy += i.get_help_decorated() + '\n'
        if FROM_CONSOLE:
            print(commands_str_tidy)
        else:
            await client.send_message(message.channel, "**Available commands for {}:**\n{}\n{}"
                                      .format(message.author.name, commands_str_tidy, note))
        return

    # Test command, for uhh ... testing purposes
    test_command_match = default_commands.TEST.matches(message_string, permission_level)
    if test_command_match is not None:
        if FROM_CONSOLE:
            print("It works!")
        else:
            await client.send_message(message.channel, "It works!")
        return

    # Permissions command
    permission_check_command_match = default_commands.PERMISSION_CHECK.matches(
        message_string, permission_level)
    if permission_check_command_match is not None:
        if FROM_CONSOLE:
            print(permissions.PermissionLevel.SUPERUSER)
        else:
            await client.send_message(message.channel, "{}'s permission level is {}"
                                      .format(message.author.name,
                                              permissions.get_label_of_permission(
                                                  permission_level)))
        return

    # Logout command
    # Logs the bot out, and saves any other data
    logout_bot_command_match = default_commands.LOGOUT_BOT.matches(message_string, permission_level)
    if logout_bot_command_match is not None:
        if not FROM_CONSOLE:
            await client.send_message(message.channel, "Logging out ...")
        print("Logging out.")
        client.logout()
        # write any data and close
        PROPERTIES_FILE.close()
        SCRIPTS_FILE.close()
        USERS_FILE.close()
        os._exit(0)

    # sets the permission level to 'superuser' for the specified user
    set_perm_to_superuser_command_match = default_commands.SET_PERM_TO_SUPERUSER.matches(
        message_string, permission_level)
    if set_perm_to_superuser_command_match is not None:
        """Sets the permissions for the specified user to a superuser
         Examples via Discord:
            $superuser @cooldude
         Through the console, you must put the user id in instead of @username
            $superuser 229628971736654096
        """
        # Get the id part of the string
        user_to_add_id = set_perm_to_superuser_command_match[0]

        # Set the users permission
        reply_message = set_user_permission(user_to_add_id, permissions.PermissionLevel.SUPERUSER)
        if FROM_CONSOLE:
            print(reply_message)
        else:
            await client.send_message(message.channel, reply_message)
        return

    # sets the permission level to 'user' for the specified user
    set_perm_to_user_command_match = default_commands.SET_PERM_TO_USER.matches(
        message_string, permission_level)
    if set_perm_to_user_command_match is not None:
        """Sets the permissions for the specified user to a superuser
         Examples via Discord:
            user @cooldude
         Through the console, you must put the user id in instead of @username
            user 229628971736654096
        """
        # Get the id part of the string
        user_to_add_id = set_perm_to_user_command_match[0]

        # Set the users permission
        reply_message = set_user_permission(user_to_add_id, permissions.PermissionLevel.USER)
        if FROM_CONSOLE:
            print(reply_message)
        else:
            await client.send_message(message.channel, reply_message)
        return

    # sets the permission level to 'default' for the specified user
    set_perm_to_default_command_match = default_commands.SET_PERM_TO_DEFAULT.matches(
        message_string, permission_level)
    if set_perm_to_default_command_match is not None:
        """Sets the permissions for the specified user to a default
         Examples via Discord:
            default @cooldude
         Through the console, you must put the user id in instead of @username
            default 229628971736654096
        """
        # Get the id part of the string
        user_to_add_id = set_perm_to_default_command_match[0]

        # Set the users permission
        reply_message = set_user_permission(user_to_add_id, permissions.PermissionLevel.DEFAULT)
        if FROM_CONSOLE:
            print(reply_message)
        else:
            await client.send_message(message.channel, reply_message)
        return

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
          "https://discordapp.com/oauth2/authorize?client_id={}&scope=bot&permissions=0"
          .format(client.user.id))
    # Update token
    p_json = PROPERTIES_FILE.get_data()
    p_json['token'] = TOKEN
    PROPERTIES_FILE.set_data(p_json)
    # Make user add self as a superuser
    if not HAS_SUPERUSER:
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
if not TOKEN:
    isValid = False
    TOKEN = input("Enter the app bot user token: ")
try:
    client.run(TOKEN)
    #client.run(TOKEN)
except discord.LoginFailure:
    print("Invalid token. "
          "Setup your bot and get its token at: "
          "https://discordapp.com/developers under MyApps->YourApp")

# Close the client and free it of resources
client.logout()
print("Client logged out")
exit(0)
