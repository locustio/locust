from configurations.build import configs_npn
import sys, os

sys.path.insert(0, os.path.dirname(__file__))


class AppData():

    @staticmethod
    def return_message(parameter):
        return parameter

    @staticmethod
    def return_config_data():
        config_dictionary = configs_npn.configs
        environment_name = config_dictionary['name']
        return environment_name
