import json
import threading # used to attempt to write to disk every 5 seconds if data was changed
"""Allows simple loading, getting, and setting of an individual json data file.

The JSONDataFile is always kept in sync with the file it represents on disk.
Example:
    properties = JSONDataFile("properties.json)
"""
class JSONDataFile:
    __file = ""
    __data = None # The current json data
    __dataLast = None # A copy of the json (__data) that was last saved to disk
    __dataWasChanged = False # was the data changed since last save to disk?

    """Initialize by loading the file data and storing it within data

    :param file: The relative path to the json file
    :param default_data: the default json data to be set into the file if theres an error
    """
    def __init__(self, file, default_data={}):
        json_data_file = None
        self.__file = file
        try:
            json_data_file = open(file)
            self.__data = json.load(json_data_file)
        except (FileNotFoundError, json.JSONDecodeError) as ex:
            if (type(ex) == json.JSONDecodeError):
                print("Error decoding {}, reseting file ... ".format(file), end='')
            if (type(ex) == FileNotFoundError):
                print("File {} doesn't exist! Creating ... ".format(file), end='')
            # Create a new file and write default_data
            json_data_file = open(file, "w+")
            json_data_file.close()
            self.set_data(default_data)
            self.__write_data_to_disk()
        print("{} loaded ...".format(file), end='')
        self.__start_auto_save_timer()
        print() # print new line

    # Automatically attempt to write the data (__data) to disk (__file) in 5 seconds
    def __start_auto_save_timer(self):
        threading.Timer(5.0, self.__write_data_to_disk).start()

    # writes the data stored in (__data) to the file (__file) if data was changed
    def __write_data_to_disk(self):
        if self.__dataWasChanged:
            # Update file on disk
            with open(self.__file, "w") as json_data_file:
                json.dump(self.__data, json_data_file)
            json_data_file.close()
            # Set data was changed to false as the data in memory
            # is the same as in the file now
            self.__dataWasChanged = False
            self.__dataLast = dict(self.__data) # copy
        self.__start_auto_save_timer()

    # Set the json data if data was changed
    def set_data(self, data):
        self.__data = data
        # Mark if data was actually changed since last write
        if (str(self.__data) != str(self.__dataLast)):
            self.__dataWasChanged = True

    # Gets the data of the json file
    def get_data(self):
        return self.__data
