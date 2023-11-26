import logging
import sys
from logging.handlers import RotatingFileHandler
import os


logger = logging.getLogger('logger')
logger.setLevel(logging.INFO)

hdlr = logging.StreamHandler(stream=sys.stdout)
hdlr.setLevel(logging.INFO)

logs_folder = 'logs'
if not os.path.exists(logs_folder):
    os.mkdir(logs_folder)

file_hdlr = RotatingFileHandler(os.path.join(logs_folder, 'main.log'), maxBytes=50000000, backupCount=7)
file_hdlr.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')

hdlr.setFormatter(formatter)
file_hdlr.setFormatter(formatter)

logger.addHandler(hdlr)
logger.addHandler(file_hdlr)
