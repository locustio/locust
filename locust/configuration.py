import os, json, logging

logger = logging.getLogger(__name__)

def read_file():
    try:
        with open((os.environ['PYTHONPATH'].split(os.pathsep))[-1] + '/tests/settings/config.json', "r") as data_file:
            datas = data_file.read()
            data_file.close()
            return datas
    except Exception as err:
        logger.info(err)
        return "{}"

def write_file(stringJSON):
    try:
        with open((os.environ['PYTHONPATH'].split(os.pathsep))[-1] + '/tests/settings/config.json', "w") as data_file:
            datas = data_file.write(stringJSON)
            return True, 'JSON saved'
    except Exception as err:
        logger.info(err)
        return False, err

def read_JSON():
    try:
        with open((os.environ['PYTHONPATH'].split(os.pathsep))[-1] + '/tests/settings/config.json', "r") as data_file:
            datas = json.load(data_file)
            data_file.close()
            return datas
    except Exception as err:
        logger.info(err)
        return "{}"
