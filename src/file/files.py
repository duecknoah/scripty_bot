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

def close():
    """Closes all files"""
    properties_file.close()
    scripts_file.close()
    users_file.close()