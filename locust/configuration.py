import os, json, logging, jsonpath_rw_ext, jsonpath_rw
from jsonpath_rw import jsonpath, parse

logger = logging.getLogger(__name__)
config_path = '/tests/settings/config.json'

def read_file():
    """
    Will read the file and return it as a string with tree view.
    """
    try:
        with open((os.environ['PYTHONPATH'].split(os.pathsep))[-1] + config_path, "r") as data_file:
            data = data_file.read()
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
            except Exception as err:
                logger.info(err)
                self.config_data = json.load({})
        return self.config_data

    def update_json_config(self, json_added, json_path, options):
        """
        Write JSON file configuration
        """
        data = ClientConfiguration.read_json(self)
        if(options != "replace"):
            json_target = jsonpath_rw_ext.match(json_path, data)
            print("target : "+ str(json_target))
            for json_target_value in json_target[0]:
                json_added.append(json_target_value)
            print("added final : "+ str(json_target))

        jsonpath_expr = parse(json_path)
        matches = jsonpath_expr.find(data)
        
        for match in matches:
            data = ClientConfiguration.update_json(data, ClientConfiguration.get_path(match), json_added)

        print("data final : "+str(data))
        
        return json.dumps(data, indent=4)
        
    @classmethod    
    def get_path(self, match):
        """
        Return an iterator based upon MATCH.PATH. Each item is a path component,
        start from outer most item.
        """
        if match.context is not None:
            for path_element in ClientConfiguration.get_path(match.context):
                yield path_element
            yield str(match.path)

    @classmethod
    def update_json(self, json, path, value):
        """
        Update JSON dictionary PATH with VALUE. Return updated JSON
        """
        try:
            first = next(path)

            # check if item is an array
            if first.startswith('[') and first.endswith(']'):
                try:
                    first = int(first[1:-1])
                except ValueError:
                    pass
            json[first] = ClientConfiguration.update_json(json[first], path, value)
            return json
        except StopIteration:
            return value

