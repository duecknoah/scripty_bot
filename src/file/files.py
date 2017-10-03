from .json_data_file import JSONDataFile
# JSON files used by the bot to access and write data
properties_file = JSONDataFile("../data/properties.json", {
    'token': None
})
scripts_file = JSONDataFile("../data/scripts.json")
users_file = JSONDataFile("../data/users.json", {
    "superusers": [],
    "users": []
})
commands_file = JSONDataFile("../data/commands.json")
# Example commands file layout:
# {
#   'cool_command': 'what\'s up ma dudes'
#   'squad': 'http://www.stuff.com/pic_of_squad.png'
# }

def close():
    """Closes all files"""
    properties_file.close()
    scripts_file.close()
    users_file.close()
    commands_file.close()