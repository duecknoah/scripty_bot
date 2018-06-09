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


class CommandArgs:
    """ An object for passing into command functions as a single argument. It
    holds data most used for each command function below
    """
    def __init__(self,
                 client=None,
                 message=None,
                 match_result=(),
                 as_permission=permissions.PermissionLevel.DEFAULT,
                 is_from_console=False
                 ):
        self.client = client
        self.message = message
        self.match_result = match_result
        self.as_permission = as_permission
        self.is_from_console = is_from_console


async def help(cmd_args: CommandArgs):
    """The help command, returns the list of commands
    available to the user who sent the message
    """
    import src.user.commands as commands
    commands_str_tidy = ''
    commands_list = commands.get_permitted_commands_for(cmd_args.as_permission)

    if cmd_args.is_from_console:
        for command_type in commands_list.keys():
            commands_str_tidy += '\n ******** {} ********\n'.format(
                command_type.value)
            for i in commands_list[command_type]:
                commands_str_tidy += i.get_help() + '\n'
        print(commands_str_tidy)
    else:
        for command_type in commands_list.keys():
            commands_str_tidy += '\n**{}**\n'.format(command_type.value)
            for i in commands_list[command_type]:
                commands_str_tidy += i.get_help_decorated() + '\n'
        await cmd_args.client.send_message(cmd_args.message.channel, "**Available commands for {}:**\n{}\n{}"
                                  .format(cmd_args.message.author.name,
                                          commands_str_tidy,
                                          '*NOTE that all commands begin with \'$\'*'))


async def permission_check(cmd_args: CommandArgs):
    """Tells the user their permission level"""
    if cmd_args.is_from_console:
        print(permissions.PermissionLevel.SUPERUSER)
    else:
        await cmd_args.client.send_message(cmd_args.message.channel, "{}'s permission level is {}"
                                  .format(cmd_args.message.author.name,
                                          permissions.get_label_of_permission(
                                              cmd_args.as_permission)))


async def logout_bot(cmd_args: CommandArgs):
    """Logs the bot out, and saves any other data"""
    import os
    from src.file import files

    if not cmd_args.is_from_console:
        await cmd_args.client.send_message(cmd_args.message.channel, "This command can only be run via console.")
        return
    print("Logging out.")
    await cmd_args.client.logout()
    # Saves all json files and any other data to file and makes bot logout
    files.close()
    os._exit(0)


async def set_perm_to_superuser(cmd_args: CommandArgs):
    """Sets the permission level of 'user' to superuser"""
    await __set_perm_to(permissions.PermissionLevel.SUPERUSER, cmd_args)


async def set_perm_to_user(cmd_args: CommandArgs):
    """Sets the permissions for the specified user to a superuser"""
    await __set_perm_to(permissions.PermissionLevel.USER, cmd_args)


async def set_perm_to_default(cmd_args: CommandArgs):
    """Sets the permissions for the specified user to a default"""
    await __set_perm_to(permissions.PermissionLevel.DEFAULT, cmd_args)


async def __set_perm_to(permission, cmd_args: CommandArgs):
    """Sets the permissions for the specified user to 'permission'
         Examples via Discord:
            superuser @cooldude
         Through the console, you must put the user id in instead of @username
            superuser 229628971736654096
        """
    # Get the id part of the string
    user_to_add_id = cmd_args.match_result[0]

    # Set the users permission
    reply_message = file_functions.set_user_permission(
        user_to_add_id, cmd_args.client, permission)
    await reply_simple(cmd_args.client, reply_message, None if cmd_args.is_from_console else cmd_args.message.channel)


async def purge(cmd_args: CommandArgs):
    """ removes n amount of messages from the messages channel
        Note that this doesn't actually do anything from the console
    """
    import discord.errors

    if cmd_args.is_from_console:
        print("This command cannot be used from the console.")
        return
    # Limit amount to 100 for safety reasons
    amt = int(cmd_args.match_result[0])
    MAX_AMT = 100
    amt = MAX_AMT if amt > MAX_AMT else amt
    amt = 0 if amt < 0 else amt

    try:
        # we add one to remove this message that was typed
        await cmd_args.client.purge_from(cmd_args.message.channel, limit=amt + 1)
        await cmd_args.client.send_message(cmd_args.message.channel, "Removed {} messages".format(amt))
    except discord.errors.Forbidden:
        await cmd_args.client.send_message(cmd_args.message.channel,
                                           "I do not have the privileges to do that on this server or channel")


async def random_number(cmd_args: CommandArgs):
    """Generates a random number between 1 and 'number'"""
    NUM_MIN = 0
    NUM_MAX = int(cmd_args.match_result[0])
    reply = ''
    try:
        rand_number = random.randint(NUM_MIN, NUM_MAX)
        reply = "The random number is {}".format(rand_number)
    except ValueError:
        reply = "Invalid range, must be at least 0"

    await reply_simple(cmd_args.client, reply, None if cmd_args.is_from_console else cmd_args.message.channel)


async def random_fact(cmd_args: CommandArgs):
    """Gets a random fact about a number

    To get the random facts, I used numbersapi.com which makes it easy
    to request a random fact, as it responds in plain text the random fact.
    """
    import urllib.request
    import html

    response = urllib.request.urlopen('http://numbersapi.com/random')
    response_as_text = str(response.read())
    response_as_text = response_as_text[2:-1]  # Remove extra characters
    fact = html.unescape(response_as_text)

    await reply_simple(cmd_args.client, fact, None if cmd_args.is_from_console else cmd_args.message.channel)


async def choose(cmd_args: CommandArgs):
    """Chooses one of the options out of the options given"""
    options = cmd_args.match_result[0]
    option_chosen = options[random.randint(0, len(options) - 1)]
    possible_sentences = (
        'The option chosen is {}',
        'Obviously I\'d choose {}',
        'Definitely {}',
        'Of course {}'
    )
    sentence_chosen = possible_sentences[random.randint(
        0, len(possible_sentences) - 1)]
    reply = sentence_chosen.format(option_chosen)

    await reply_simple(cmd_args.client, reply, None if cmd_args.is_from_console else cmd_args.message.channel)


async def eight_ball(cmd_args: CommandArgs):
    """Returns a decision to any question"""
    possible_sentences = (
        'It is certain',
        'It is decidedly so',
        'Without a doubt',
        'Yes definitely',
        'You may rely on it',
        'As I see it, yes',
        'Most likely',
        'Outlook good',
        'Yes',
        'Signs point to yes',
        'Reply hazy try again',
        'Ask again later',
        'Better not tell you now',
        'Cannot predict now',
        'Concentrate and ask again',
        'Don\'t count on it',
        'My reply is no',
        'My sources say no',
        'Outlook not so good',
        'Very doubtful'
    )
    sentence_chosen = possible_sentences[random.randint(
        0, len(possible_sentences) - 1)]

    await reply_simple(cmd_args.client, sentence_chosen, None if cmd_args.is_from_console else cmd_args.message.channel)


async def command_add(cmd_args: CommandArgs):
    """Creates a custom command"""
    import src.user.commands as commands
    reply = ''

    try:
        success = commands.add_command(
            commands.CustomCommand(
                cmd_args.match_result[0],
                cmd_args.match_result[1],
                custom_command))
        if success:
            reply = 'Added \'{}\' to the list of commands'.format(
                cmd_args.match_result[0])
            file_functions.save_custom_commands()
        else:
            reply = 'A command with that name already exists!'

    except commands.ImproperNameError:
        reply = 'The command name can\'t contain any spaces! Ex. command add Hello Why hello there'

        await reply_simple(cmd_args.client, reply, None if cmd_args.is_from_console else cmd_args.message.channel)


async def command_remove(cmd_args: CommandArgs):
    import src.user.commands as commands
    reply = ''

    if commands.remove_command_by_name(cmd_args.match_result[0]):
        reply = 'Removed the command \'{}\' from the commands list'.format(
            cmd_args.match_result[0])
        file_functions.save_custom_commands()
    else:
        reply = 'That command doesn\'t exist'

    await reply_simple(cmd_args.client, reply, None if cmd_args.is_from_console else cmd_args.message.channel)


async def custom_command(cmd_args: CommandArgs):
    """The command run for all custom commands,
    simply just passing a message through to the user
    """
    await reply_simple(cmd_args.client, cmd_args.match_result, None if cmd_args.is_from_console else cmd_args.message.channel)


async def reply_simple(client, message, channel=None):
    if channel is None:
        print(message)
    else:
        await client.send_message(channel, message)
