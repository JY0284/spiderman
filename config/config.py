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
else:
    config['Email'] = {
        'server_address': 'smtp.qq.com',
        'server_port': '465',
        'sender_email': 'your_email@qq.com',
        'sender_password': 'your_password'
    }
    config['NJExistingHousingTradeInfo'] = {
        'url': 'http://njzl.njhouse.com.cn/',
        'timezone': 'Asia/Shanghai',
        'schedule_interval': 'daily',
        'schedule_time': '02:00'
    }
    config['Collector3'] = {
        'api_endpoint': 'https://api.example.com/data',
        'schedule_interval': 'hourly',
        'schedule_time': '00:30'
    }
    config['Database'] = {
        'db_path': os.path.join(os.path.dirname(__file__), '../db/data.db')
    }
    config['Notifier'] = {
        'default_recipient': 'jiangyu9272@outlook.com'
    }
    config['Logging'] = {
        'log_file': 'logs/system.log',
        'log_level': 'INFO'
    }
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)
    print(f"Default configuration created at {CONFIG_FILE}. Please update it with actual values.")
    raise Exception(f"Default configuration created at {CONFIG_FILE}. Please update it with actual values.")

def configparser_to_dict(config):
    return {section: dict(config.items(section)) for section in config.sections()}

config = configparser_to_dict(config)

# Setup logging
log_file = config['Logging'].get('log_file', 'logs/system.log')
log_level_str = config['Logging'].get('log_level', 'INFO').upper()
log_level = getattr(logging, log_level_str, logging.INFO)

# Ensure the log directory exists
log_dir = os.path.dirname(log_file)
if log_dir and not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Configure the root logger
logger = logging.getLogger()
logger.setLevel(log_level)

formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')

# File handler with rotation
file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=2)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
