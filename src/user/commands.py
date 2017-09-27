"""This module contains functions and classes with anything to do with user commands

This includes:
    - A command list
    - A command class that when instantiated, can be added to the command list
    - command keywords that help with matching a string with command arguments
This is here to simplify the creation of new commands and checking if the users
message matches the command correctly.
"""
from enum import Enum
from src.user.permissions import PermissionLevel

############################## Keyword Functions ##############################
'''
Every keyword function must match these criteria:
Arguments:
    string (str): the input string to check for the match
Returns:
    None if there were no matches to the keyword function
    Any data (other than None) if there were matches to the keyword function
'''
def keyword_function_user_reference(string):
    """ Checks if the string is a user mention

    Returns None if not a match
    Returns the user id found if a match
    An example matchs would be:
        <@782311255082572245>
        782311255082572245
    """
    if string.startswith('<@') and string.endswith('>'):
        string = string[2:-1]
    if len(string) != 18:
        return None
    try:
        int(string)
        return string
    except ValueError:
        return None

def keyword_function_number(string):
    """Checks if the string is a number

    Returns None if not a match
    Returns the number if a match
    """
    try:
        number = float(string)
        return number
    except ValueError:
        return None

def keyword_function_passthrough(string):
    """Used as a way to simply return the string back
    This is useful if you want to just pass what the user
    typed where that command is and don't want to do any operations on it
    """
    return string

class KeywordCount(Enum):
    """Used to represent if a command keyword will
    include a single or multiple words
    """
    SINGLE_WORD = 0
    MULTIPLE_WORDS = 1

class CommandKeywords(Enum):
    """A keyword in a command that represents a special match in the string

    The keyword is a part in the command string that acts as its own function to check
    If the string given matches the criteria for that keyword.

        For example, if we wanted a command to say hi to any mentioned user,
        we make the command name:
            'say <user>'
        The '<user>' in 'say <user>' is a CommandKeyword that
        tells us we need to mention a user there.
        To do that, a keyword function checks that the string in that index is a user_id.
        Returning True if it is, and False otherwise

    Each CommandKeyword is a list in which holds:
        index[0]: holds the keyword_string
        index[1]: holds the keyword function
        index[2]: tells if this functions will include multiple words,
                  separated by the '|' delimiter or end of string
    """
    USER_REFERENCE = ('<user>', keyword_function_user_reference, KeywordCount.SINGLE_WORD)
    NUMBER = ('<number>', keyword_function_number, KeywordCount.SINGLE_WORD)
    STRING = ('<string>', keyword_function_passthrough, KeywordCount.MULTIPLE_WORDS)

def get_keyword_string_of(keyword):
    """Gets the keyword string of the keyword"""
    return keyword.value[0]

def get_keyword_function_of(keyword):
    """Gets the keyword function of the keyword"""
    return keyword.value[1]

def get_keyword_count_of(keyword):
    """Gets the keyword count of the keyword"""
    return keyword.value[2]

def matches_keyword_function(string, command_keyword):
    """Checks if the given string matches the given CommandKeyword function

    Returns True if so, returns False if not
    """
    keyword_function = get_keyword_function_of(command_keyword)
    return keyword_function(string)


class Command(object):
    """The object for creating user commands
    Args:
        name (str) -- the name of the command, typing this and giving the
                        correct arguments executes this command.
                        The name can also contain CommandKeywords to identify
                        what type of arguments need to be provided to execute the
                        command
        desc (str) -- the description of the command
        minimum_permission -- the minimum permission needed to execute this command
        function (function) -- a reference to the function
                                to run when the command is called, None by default
    """

    def __init__(self, name, desc='No description provided',
                 minimum_permission=PermissionLevel.DEFAULT,
                 function=None):
        self.name = name.strip()
        self.desc = desc.strip()
        self.minimum_permission = minimum_permission
        self.function = function

    def get_help(self):
        """ Returns the name and description of the command """
        return "{}: {}".format(self.name, self.desc)

    def get_help_decorated(self):
        """ Same as get_help(), but adds text decoration to be used in discord """
        return "`{}`: {}".format(self.name, self.desc)

    @staticmethod
    def get_words_until_delimiter(string):
        """Gets the string of words until the delimiter or end of string
        Where:
            <string> is a bunch of words going until the delimiter '|'
            | - the delimiter
            The delimiter is also the end of the function
        """

        DELIMITER = '|'
        STRING_CUT = string.partition(DELIMITER)[0]
        return STRING_CUT.strip()

    def matches(self, string, permission_level):
        """ Checks if the given string matches this commands requirements

        Args:
            string (str) -- the string to compare if it matches
                up with the command string and keyword arguments
            permission_level (PermissionLevel) -- after checking if the string matches,
                a final check compares if this permission level is allowed to execute this command,
                if not, this function will return None

        If the command fully matches each command_keyword and the command itself, it
        Returns results of each keyword function in a tuple in order
        of the command_keywords

            Example:
                A command with the name of 'say_hi_to <user> <user>'.
                This command would be executed like so:

                    say_hi_to <@782311255082572245> <@282311255082572241>
                    NOTE: in Discord, the <@numbers> represents a user mention

                this matches function would return the result based on the
                keyword_function for the USER_REFERENCE command:
                    (782311255082572245, 282311255082572241)

        However if this command does not fully match each command_keyword,
        it will Returns None
        """
        string = string.strip() # the string we want to test
        command_name_as_tuple = tuple(self.name.split()) # the command's name we want to match to
        string_as_tuple = tuple(string.split())
        results = []
        string_word_offset = 0 # Used if string command is used

        # Go through word by word comparing the string to the command name
        for i in range(len(command_name_as_tuple)): # pylint: disable=consider-using-enumerate
            # If we got to a point where the index in the string is out of
            # bounds, count this as a mismatch, return None
            if len(string_as_tuple) - 1 < i + string_word_offset:
                return None

            string_word = string_as_tuple[i + string_word_offset]
            command_word = command_name_as_tuple[i]
            keyword_match = False

            # Check if this word typed matches our keyword for this command (if there is one)
            for keyword in CommandKeywords:
                # if the command word matches a CommandKeyword, run the match function
                # specific to that command keyword
                if command_word == get_keyword_string_of(keyword):
                    match_function = get_keyword_function_of(keyword)

                    # Do operations on multiple words if the command keyword wants it
                    if get_keyword_count_of(keyword) == KeywordCount.MULTIPLE_WORDS:
                        # Get the entire string after this point until the end or delimiter '|'
                        string_as_tuple_after = string_as_tuple[i + string_word_offset:]
                        string_words = Command.get_words_until_delimiter(' '.join(string_as_tuple_after))
                        match_result = match_function(string_words)

                        # Then since we operated on multiple words, skip ahead to the point
                        # Where the string_word lines up with the command arguments/keywords
                        total_words_to_skip = match_result.count(' ') + 1
                        string_word_offset += total_words_to_skip
                    else:
                        match_result = match_function(string_word)
                    """ If this word does not match the command keyword's criteria,
                    then this whole command doesn't match the criteria
                    """
                    if match_result is None:
                        return None
                    # else append this to the results as it matched!
                    results.append(match_result)
                    keyword_match = True
                    break

            # If there was a keyword match, then move onto the next words
            if keyword_match:
                continue
            # Since there was no CommandKeyword at this part of the command,
            # just check if the string word here matches the command's word here
            if command_word != string_word:
                return None

        # Lastly, verify that the permission_level is allowed to execute this command
        if permission_level.value >= self.minimum_permission.value:
            # The string and permission fully matches the command criteria, return the results!
            return tuple(results)
        # Denied permission level, so it does not match the command requirements
        return None

command_list = []

def get_permitted_commands_for(permission_level):
    """ Returns a list of permitted commands for the specified
    user based off their permissions
    """
    commands_permitted = []
    for i in command_list:
        # Only show commands available to this permission level
        if i.minimum_permission.value > permission_level.value:
            continue
        commands_permitted.append(i)
    return commands_permitted
