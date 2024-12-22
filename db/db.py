# db/db.py

import os
import sqlite3
from sqlite3 import Error
from typing import Dict, Any, List
import logging

class DBHandler:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.logger = logging.getLogger(self.__class__.__name__)
        self._user_table_name = 'user_preferences'
        self.create_user_table()

    def create_connection(self) -> sqlite3.Connection:
        """Create a database connection to the SQLite database."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            self.logger.debug("Database connection established.")
            return conn
        except Error as e:
            self.logger.error(f"Database connection error: {e}")
        return conn

    def execute_query(self, query: str, params: tuple = ()):
        """Execute a single query with optional parameters."""
        conn = self.create_connection()
        if conn:
            try:
                c = conn.cursor()
                c.execute(query, params)
                conn.commit()
                self.logger.debug("Query executed successfully.")
            except Error as e:
                self.logger.error(f"Error executing query: {e}")
            finally:
                conn.close()

    def insert_trade_info(self, table: str, data: Dict[str, Any]):
        """
        Insert trade information into the specified table.
        Args:
            table: Table name.
            data: Dictionary containing data to insert.
        """
        keys = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        sql = f"INSERT OR REPLACE INTO {table} ({keys}) VALUES ({placeholders});"
        values = tuple(data.values())
        try:
            self.execute_query(sql, values)
            self.logger.info(f"Trade information inserted into '{table}'.")
        except Exception as e:
            self.logger.error(f"Failed to insert trade info into '{table}': {e}")

    def create_user_table(self):
        """
        Create the user_preferences table specific to this collector.
        """
        create_user_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {self._user_table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT NOT NULL,
            user_email TEXT NOT NULL UNIQUE
        );
        """
        self.execute_query(create_user_table_sql)
        self.logger.info(
            "Table 'nj_existing_housing_trade_info' ensured in the database."
        )

    def get_user_emails(self) -> List:
        """Retrieve all user emails from user_preferences."""
        sql = "SELECT user_name, user_email FROM user_preferences;"
        conn = self.create_connection()
        emails = []
        if conn:
            try:
                c = conn.cursor()
                c.execute(sql)
                rows = c.fetchall()
                names = [row[0] for row in rows]
                emails = [row[1] for row in rows]
                user_info = list(zip(names, emails))
                self.logger.debug(f"Retrieved user emails: {user_info}")
            except Error as e:
                self.logger.error(f"Failed to retrieve user emails: {e}")
            finally:
                conn.close()
        return user_info

    def add_user_email(self, name:str, email: str):
        """Add a new user email to the user_preferences table."""
        sql = "INSERT OR IGNORE INTO user_preferences (user_name, user_email) VALUES (?, ?);"
        try:
            self.execute_query(sql, (name, email))
            self.logger.info(f"User email '{email}' added to the database.")
        except Exception as e:
            self.logger.error(f"Failed to add user email '{email}': {e}")

    def absolute_db_path(self):
        return os.path.join(os.path.join(os.path.dirname(os.path.dirname(__file__)), self.db_path))

    # Additional methods as needed
