"""Constants and initialization"""
from src.user.commands import Command, get_keyword_string_of, \
    CommandKeywords, command_list, \
    CommandType, order_commands_by_type
from src.user.permissions import PermissionLevel
import src.command_functions as command_functions
import src.file_functions as file_functions
import src.file.files as files

C_PREFIX = '$'  # The prefix for all commands

################# Default Command Creation #################
# Initializes all default commands and puts them into the commands_list
HELP = Command('help', 'lists the available commands for the user',
               CommandType.STANDARD,
               PermissionLevel.DEFAULT,
               command_functions.help)

PERMISSION_CHECK = Command('permission',
                           'gets the permission level of the user',
                           CommandType.MODERATION,
                           PermissionLevel.DEFAULT,
                           command_functions.permission_check)

LOGOUT_BOT = Command('logout', 'shuts down the bot',
                     CommandType.MODERATION,
                     PermissionLevel.SUPERUSER,
                     command_functions.logout_bot)

SET_PERM_TO_SUPERUSER = Command('superuser {}'.format(
    get_keyword_string_of(CommandKeywords.USER_REFERENCE)),
    'sets the permission level of \'user\' to superuser',
    CommandType.MODERATION,
    PermissionLevel.SUPERUSER,
    command_functions.set_perm_to_superuser)

SET_PERM_TO_USER = Command('user {}'.format(
    get_keyword_string_of(CommandKeywords.USER_REFERENCE)),
    'sets the permission level of \'user\' to user',
    CommandType.MODERATION,
    PermissionLevel.SUPERUSER,
    command_functions.set_perm_to_user)

SET_PERM_TO_DEFAULT = Command('default {}'.format(
    get_keyword_string_of(CommandKeywords.USER_REFERENCE)),
    'sets the permission level of \'user\' to to default',
    CommandType.MODERATION,
    PermissionLevel.SUPERUSER,
    command_functions.set_perm_to_default)

PURGE = Command('purge {}'.format(
    get_keyword_string_of(CommandKeywords.NUMBER)),
    'Removes \'number\' amount of messages from this channel (max 100)',
    CommandType.MODERATION, PermissionLevel.SUPERUSER,
    command_functions.purge)

RANDOM_NUMBER = Command('random {}'.format(
    get_keyword_string_of(CommandKeywords.NUMBER)),
    'Gets a random number between 0 and \'number\'',
    CommandType.STANDARD,
    PermissionLevel.DEFAULT,
    command_functions.random_number)

RANDOM_NUMBER_FACT = Command('fact', 'Gets random number facts',
                             CommandType.STANDARD,
                             PermissionLevel.DEFAULT,
                             command_functions.random_fact)

CHOOSE = Command('choose {}'.format(
    get_keyword_string_of(CommandKeywords.OPTIONS)),
    'Chooses a random option out of the options given',
    CommandType.STANDARD,
    PermissionLevel.DEFAULT,
    command_functions.choose,
    'choose <option 1> | <option 2> | ... ')

EIGHT_BALL = Command('8ball',
                     'Attempts to give you the best advice',
                     CommandType.STANDARD,
                     PermissionLevel.DEFAULT,
                     command_functions.eight_ball)

COMMAND_ADD = Command('command add {} {}'.format(
    get_keyword_string_of(CommandKeywords.WORD),
    get_keyword_string_of(CommandKeywords.STRING)),
    'Creates a custom command',
    CommandType.STANDARD,
    PermissionLevel.DEFAULT,
    command_functions.command_add,
    'command add <command name> | <command>')

# Add these commands to the command list
command_list.extend((
    HELP, PERMISSION_CHECK,
    LOGOUT_BOT, SET_PERM_TO_SUPERUSER,
    SET_PERM_TO_USER, SET_PERM_TO_DEFAULT,
    PURGE, RANDOM_NUMBER, RANDOM_NUMBER_FACT,
    CHOOSE, EIGHT_BALL, COMMAND_ADD,
))

# Custom commands
CUSTOM_COMMANDS = file_functions.load_custom_commands()
for c in CUSTOM_COMMANDS:
    command_list.append(c)

order_commands_by_type()