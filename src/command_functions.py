""" This module contains all of the functions for the default commands
Each function must be asynchronous and have the following Args:
    client (object) -- the client of the discord bot
    message (object or string) -- the message object (when message
                                  was sent through discord) or string
    match_result (tuple) -- the results of the match for the command. Contains useful
                            information when using command keywords as arguments in a command.
                            See commands.py Commands class for more info
    as_permission (object) -- the permission level of the user executing the function
    FROM_CONSOLE (bool) -- was this message sent through the console?
"""
import src.user.permissions as permissions
import src.file_functions as file_functions
import random

async def help(client, message, match_result, as_permission, FROM_CONSOLE=False):
    """The help command, returns the list of commands
    available to the user who sent the message
    """
    import src.user.commands as commands
    commands_list = None
    commands_str_tidy = ''
    note = '*NOTE that all commands begin with \'$\'*'
    if FROM_CONSOLE:
        commands_list = commands.get_permitted_commands_for(
            permissions.PermissionLevel.SUPERUSER)
        for i in commands_list:
            commands_str_tidy += i.get_help() + '\n'
        print(commands_str_tidy)
    else:
        commands_list = commands.get_permitted_commands_for(as_permission)
        for i in commands_list:
            commands_str_tidy += i.get_help_decorated() + '\n'
        await client.send_message(message.channel, "**Available commands for {}:**\n{}\n{}"
                            .format(message.author.name, commands_str_tidy, note))

async def test(client, message, match_result, as_permission, FROM_CONSOLE=False):
    """A debug command"""
    if FROM_CONSOLE:
        print("It works!")
    else:
        await client.send_message(message.channel, "It works!")

async def permission_check(client, message, match_result, as_permission, FROM_CONSOLE=False):
    """Tells the user their permission level"""
    if FROM_CONSOLE:
        print(permissions.PermissionLevel.SUPERUSER)
    else:
        await client.send_message(message.channel, "{}'s permission level is {}"
                                  .format(message.author.name,
                                          permissions.get_label_of_permission(
                                              as_permission)))

async def logout_bot(client, message, match_result, as_permission, FROM_CONSOLE=False):
    """Logs the bot out, and saves any other data"""
    import os
    from src.file import files

    if not FROM_CONSOLE:
        await client.send_message(message.channel, "Logging out ...")
    print("Logging out.")
    await client.logout()
    # Saves all json files and any other data to file and makes bot logout
    files.close()
    os._exit(0)

async def set_perm_to_superuser(client, message, match_result, as_permission, FROM_CONSOLE=False):
    """Sets the permission level of 'user' to superuser"""
    await __set_perm_to(permissions.PermissionLevel.SUPERUSER, client, message, match_result, as_permission, FROM_CONSOLE)

async def set_perm_to_user(client, message, match_result, as_permission, FROM_CONSOLE=False):
    """Sets the permissions for the specified user to a superuser"""
    await __set_perm_to(permissions.PermissionLevel.USER, client, message, match_result, as_permission, FROM_CONSOLE)

async def set_perm_to_default(client, message, match_result, as_permission, FROM_CONSOLE=False):
    """Sets the permissions for the specified user to a default"""
    await __set_perm_to(permissions.PermissionLevel.DEFAULT, client, message, match_result, as_permission, FROM_CONSOLE)

async def __set_perm_to(permission, client, message, match_result, as_permission, FROM_CONSOLE=False):
    """Sets the permissions for the specified user to 'permission'
         Examples via Discord:
            superuser @cooldude
         Through the console, you must put the user id in instead of @username
            superuser 229628971736654096
        """
    # Get the id part of the string
    user_to_add_id = match_result[0]

    # Set the users permission
    reply_message = file_functions.set_user_permission(user_to_add_id, client, permission)
    if FROM_CONSOLE:
        print(reply_message)
    else:
        await client.send_message(message.channel, reply_message)

async def purge(client, message, match_result, as_permission, FROM_CONSOLE=False):
    """ removes n amount of messages from the messages channel
        Note that this doesn't actually do anything from the console
    """
    import discord.errors

    if FROM_CONSOLE:
        print("This command cannot be used from the console.")
        return
    # Limit amount to 100 for safety reasons
    amt = int(match_result[0])
    MAX_AMT = 100
    amt = MAX_AMT if amt > MAX_AMT else amt

    try:
        await client.purge_from(message.channel, limit=amt + 1) # we add one to remove this message that was typed
        await client.send_message(message.channel, "Removed {} messages".format(amt))
    except discord.errors.Forbidden:
        await client.send_message(message.channel, "I do not have the privileges to do that on this server or channel")

async def random_number(client, message, match_result, as_permission, FROM_CONSOLE=False):
    """Generates a random number between 1 and 'number'"""
    NUM_MIN = 0
    NUM_MAX = int(match_result[0])
    reply = ''
    try:
        rand_number = random.randint(NUM_MIN, NUM_MAX)
        reply = "The random number is {}".format(rand_number)
    except ValueError:
        reply = "Invalid range, must be at least 0"

    if FROM_CONSOLE:
        print(reply)
    else:
        await client.send_message(message.channel, reply)