""" Allows simple loading, getting, and setting of an individual json data file.

For All further explanation see the class docstring

"""
import json
import threading  # used to attempt to write to disk every 5 seconds if data was changed
import copy  # allows for deep copying of dictionary data used in json


class JSONDataFile:
    """Allows simple loading, getting, and setting of an individual json data file.

    The JSONDataFile is always kept in sync with the file it represents on disk.
    Example:
        properties = JSONDataFile('properties.json')
    """

    def __init__(self, file, default_data={}):
        """Initialize by loading the file data and storing it within data

            :param file: The relative path to the json file
            :param default_data: the default json data to be set into the file if theres an error
        """
        self.__file = file
        self.__data = None  # The current json data
        # A copy of the json (__data) that was last saved to disk
        self.__data_last = None
        self.__data_was_changed = False  # was the data changed since last save to disk?
        try:
            json_data_file = open(file)
            self.__data = json.load(json_data_file)
        except (FileNotFoundError, json.JSONDecodeError) as ex:
            if isinstance(ex, json.JSONDecodeError):
                print("Error decoding {}, reseting file ... ".format(file), end='')
            if isinstance(ex, FileNotFoundError):
                print("File {} doesn't exist! Creating ... ".format(file), end='')
            # Create a new file and write default_data
            json_data_file = open(file, "w+")
            json_data_file.close()
            self.set_data(default_data)
            self.__write_data_to_disk()
        print("{} loaded ...".format(file), end='')
        self.__start_auto_save_timer()
        print()  # print new line

    def __start_auto_save_timer(self):
        """ Automatically attempt to write the data (__data) to disk (__file) in 5 seconds """
        threading.Timer(5.0, self.__write_data_to_disk).start()

    def __write_data_to_disk(self):
        """ writes the data stored in (__data) to the file (__file) if data was changed """
        self.__data_change_check()

        if self.__data_was_changed:
            # Update file on disk
            with open(self.__file, "w") as json_data_file:
                json.dump(self.__data, json_data_file)
            json_data_file.close()
            # Set data was changed to false as the data in memory
            # is the same as in the file now
            self.__data_was_changed = False
            self.__data_last = copy.deepcopy(self.__data)  # copy
        self.__start_auto_save_timer()

    def set_data(self, data):
        """ Forcefully sets the entire json data, use carefully
        Args:
            data (dict): JSON data string for the file
        """
        self.__data = data

    def __data_change_check(self):
        """ Checks if data was changed, if so, mark it in self.__dataWasChanged """
        if str(self.__data) != str(self.__data_last):
            self.__data_was_changed = True

    def get_data(self):
        """ Gets the string data of the json file
        Note:
            this is a direct reference and not a copy of the data
        Returns:
            dict: the data for the JSON file
        """
        return self.__data

    def close(self):
        """ Saves and closes the JSON file while removing any threads on a timer """
        self.__write_data_to_disk()
