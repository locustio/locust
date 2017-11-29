import os, json, logging

logger = logging.getLogger(__name__)
config_path = '/tests/settings/config.json'

def read_file():
    """
    Will read the file and return it as a string with tree view.
    """
    try:
        with open((os.environ['PYTHONPATH'].split(os.pathsep))[-1] + config_path, "r") as data_file:
            data = data_file.read()
            data_file.close()
    except Exception as err:
        logger.info(err)
        data = "{}"
    return data

def write_file(string_json):
    """
    The `string_json` will overwrite existing configuration. 
    If the previous configuration doesn't exist, then it will create the file.
    """
    status, message = None, None
    try:
        with open((os.environ['PYTHONPATH'].split(os.pathsep))[-1] + config_path, "w") as data_file:
            data_file.write(string_json)
            status = True
            message = 'Configuration has been saved'
    except Exception as err:
        logger.info(err)
        status = False
        message = "Can't save the configuration :" + err
    return status, message

class ClientConfiguration:
    """
    This class is a handler for data configuration with JSON data structure.
    """

    config_data = None

    def read_json(self):
        """
        Will get the data of configuration as JSON. 
        It reads configuration file once.
        """
        if self.config_data is None:
            try:
                with open((os.environ['PYTHONPATH'].split(os.pathsep))[-1] + config_path, "r") as data_file:
                    self.config_data = json.load(data_file)
                    data_file.close()
            except Exception as err:
                logger.info(err)
                self.config_data = json.load({})
        return self.config_data

