from os import getcwd,listdir
import configparser
from pydmarc.common.log import logger

WORKSPACE = getcwd()
config = configparser.ConfigParser()
CONFIG_FILE: str
ATTACHMENTS_FOLDER = getcwd() + '\\attachments\\'

def _check_config_file_present():
    files = listdir(WORKSPACE)
    if any('config.cfg' in listdir(WORKSPACE) for file in files):
        CONFIG_FILE = '{}\\config.cfg'.format(WORKSPACE)
        logger.info("Configuration file set - {}".format(CONFIG_FILE))
        return True
    else:
        return False