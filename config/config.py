# config/config.py

import configparser
import os
import logging
from logging.handlers import RotatingFileHandler

config = configparser.ConfigParser()

# Path to the config file
CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.ini')

# Read config from file or set default values
if os.path.exists(CONFIG_FILE):
    config.read(CONFIG_FILE)
