import os, json, logging, jsonpath_rw_ext, jsonpath_rw
from jsonpath_rw import jsonpath, parse
from . import events
from ast import literal_eval
from flask import make_response

logger = logging.getLogger(__name__)
CONFIG_PATH = '/tests/settings/config.json'

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
                with open((os.environ['PYTHONPATH'].split(os.pathsep))[-1] + CONFIG_PATH, "r") as data_file:
                    self.config_data = json.load(data_file)
            except Exception as err:
                logger.info(err)
                self.config_data = json.load({})
        return self.config_data

    def update_json_config(self, data_json, json_added, json_path, options, list_column):
        """
        Write JSON file configuration
        """
        if(options != "replace"):
            json_target = jsonpath_rw_ext.match(json_path, data_json)
            if isinstance(json_target[0], dict):
                if list_column==1:
                    json_target[0][list_column[0]] = json_added
                    json_final = json_target[0]
                else:
                    return make_response(json.dumps({'success':False, 'error_type':'type not match', 'message':'last variable JSONPath type not match with data.'}))
            else:
                for json_target_value in json_target[0]:
                    json_added.append(json_target_value)
                json_final = json_added
        else:
            json_final = json_added

        jsonpath_expr = parse(json_path)
        matches = jsonpath_expr.find(data_json)
        
        for match in matches:
            data_json = ClientConfiguration.update_json(data_json, ClientConfiguration.get_path(match), json_final)
        
        return make_response(json.dumps({'success':True, 'data':json.dumps(data_json, indent=4)}))

    def add_new_key(self, temppath, new_key_type, config_text):
        """
        Split the jsonpath and trigger create_path
        """
        data = literal_eval(config_text)
        splitpath = filter(None, temppath.split('.'))

        return self.create_path(data, splitpath, new_key_type, 1)

    def check_key(self, input_json, json_path):
        """
        Split path and trigger check_exist_path
        """
        splitpath = filter(None, json_path.split('.'))
        status, message = self.check_exist_path(input_json, splitpath, 1)
        return status, message

    def create_path(self, input_json, splitpath, type_new_key, index):
        """
        Recursively search for jsonpath in json and create not found jsonpath
            **there are several to do for checking json, such as :
                - check dictionary or list type and trigger next iteration
                - create path on json when jsonpath not found until last index
                - for the last index, the object will created depend on type_new_key 
        """
        initial_json = input_json
        if type(input_json) is dict and input_json:
            if splitpath[index] in input_json:
                input_json = input_json[splitpath[index]]
                self.create_path(input_json, splitpath, type_new_key, index+1)
            elif index == len(splitpath)-1:
                if type_new_key == "number":
                    input_json[splitpath[index]] = 0
                elif type_new_key == "object":
                    input_json[splitpath[index]] = {}
                elif type_new_key == "array":
                    input_json[splitpath[index]] = []
                else:
                    input_json[splitpath[index]] = ""
                return
            else:
                input_json[splitpath[index]] = {}
                self.create_path(input_json[splitpath[index]], splitpath, type_new_key, index+1)
        
        elif type(input_json) is list and input_json:
            for entity in input_json:
                self.create_path(entity, splitpath, type_new_key, index)

        elif index < len(splitpath)-1:
            input_json[splitpath[index]] = {}
            self.create_path(input_json[splitpath[index]], splitpath, type_new_key, index+1)
        
        elif index == len(splitpath)-1:
            if type_new_key == "number":
                input_json[splitpath[index]] = 0
            elif type_new_key == "object":
                input_json[splitpath[index]] = {}
            elif type_new_key == "array":
                input_json[splitpath[index]] = []
            else:
                input_json[splitpath[index]] = ""
            return

        if index == 1:
            if splitpath[index] in input_json:
                return input_json
            else:
                initial_json[splitpath[index]] = input_json
                return initial_json
    
    def check_exist_path(self, input_json, splitpath, index):
        """
        Recursively check jsonpath
        """ 
        if index > len(splitpath)-1:
            return True, "Path exist"
        elif type(input_json) is dict and input_json:
            if splitpath[index] in input_json:
                input_json = input_json[splitpath[index]]
                status, message = self.check_exist_path(input_json, splitpath, index+1)
            else:
                return False, splitpath[index]
        elif type(input_json) is list and input_json:
            for entity in input_json:
                status, message = self.check_exist_path(entity, splitpath, index)
                if not status:
                    break
        return status, message

    def convert_to_json(self, csv_stream, multiple_data_headers):
        """
        Convert csv data to json
        """
        if(multiple_data_headers and len(multiple_data_headers) > 0):
            tempStr = csv_stream.convert(multiple_data_headers)
            json_added = tempStr
        else:
            tempStr = csv_stream.convert([])
            if len(csv_stream.get_columns_name()) > 1:
                json_added = tempStr
            else:
                json_added = tempStr.get(csv_stream.get_columns_name()[0])
        
        return json_added

    def get_last_variable(self, jsonpath):
        """
        Get last variable from jsonpath
        """
        splitpath = filter(None, jsonpath.split('.'))
        return splitpath[-1]

        
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
            if (first.startswith('[') and first.endswith(']')) or (first.startswith('{') and first.endswith('}')):
                try:
                    first = int(first[1:-1])
                except ValueError:
                    pass
            json[first] = ClientConfiguration.update_json(json[first], path, value)
            return json
        except StopIteration:
            return value

