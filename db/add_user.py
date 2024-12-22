# db/add_user.py

import sys
import logging
from config.config import config
from db import DBHandler

def add_user(name: str, email: str, config):
    db_handler = DBHandler(config['Database']['db_path'])
    db_handler.add_user_email(name, email)

if __name__ == "__main__":
    logger = logging.getLogger('add_user')

    if len(sys.argv) != 3:
        logger.error("Usage: python add_user.py user_name user_email@example.com")
    else:
        name, email = sys.argv[1:3]
        add_user(name, email, config)
        logger.info(f"Added user: {name}: {email}")
