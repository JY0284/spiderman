# collectors/base_collector.py

from re import sub
from abc import ABC, abstractmethod
from typing import Dict, Any
from db.db import DBHandler
import logging


class Collector(ABC):
    """
    Abstract base class for all collectors.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.db_handler = DBHandler(config["Database"]["db_path"])
        self.name = self.__class__.__name__
        if not hasattr(self, "table_name"):
            self.table_name = sub(r"(?<!^)(?=[A-Z])", "_", self.name).lower()
        self.schedule_interval = self.get_schedule_interval()
        self.schedule_time = self.get_schedule_time()
        self.create_table()
        self.mapping = None

    @abstractmethod
    def collect(self) -> Any:
        """
        Collect data from the source.
        Returns:
            Raw data collected.
        """
        pass

    @abstractmethod
    def process_data(self, raw_data: Any) -> Dict[str, Any]:
        """
        Process raw data into a structured format.
        Args:
            raw_data: The raw data collected from the source.
        Returns:
            A dictionary containing the processed data.
        """
        pass

    @abstractmethod
    def create_table(self):
        """
        Create the necessary database table for the collector.
        """
        pass

    def map_dict_keys(self, original):
        """
        Maps the keys of the original dictionary to new keys based on the provided mapping.

        Args:
            original (dict): The original dictionary with keys to be mapped.

        Returns:
            dict: A new dictionary with keys renamed according to the mapping.
        """
        return (
            {self.mapping.get(k, k): v for k, v in original.items()}
            if self.mapping
            else original
        )

    def insert_data(self, data: Dict[str, Any]):
        """
        Insert data into the database.
        Args:
            data: A dictionary containing the data.
        """
        data = self.map_dict_keys(data)
        keys = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        sql = f"INSERT OR REPLACE INTO {self.table_name} ({keys}) VALUES ({placeholders});"
        print(data)
        values = tuple(data.values())
        try:
            self.db_handler.execute_query(sql, values)
            self.logger.info(f"Data inserted into '{self.table_name}'.")
        except Exception as e:
            self.logger.error(
                f"Failed to insert data info into '{self.table_name}': {e}"
            )

    def get_schedule_interval(self) -> str:
        """
        Retrieve the schedule interval from configuration.
        Returns:
            Schedule interval as a string.
        """
        section = self.__class__.__name__
        return self.config.get(section, {}).get("schedule_interval", "daily")

    def get_schedule_time(self) -> str:
        """
        Retrieve the schedule time from configuration.
        Returns:
            Schedule time as a string (HH:MM).
        """
        section = self.__class__.__name__
        return self.config.get(section, {}).get("schedule_time", "02:00")
