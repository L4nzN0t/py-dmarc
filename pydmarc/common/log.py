import logging
from datetime import datetime
from os import getcwd

LOG_FILE = getcwd() + '\\logs\\' + datetime.now().strftime('log_%d%m%Y.txt')

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

