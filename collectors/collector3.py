# collectors/collector3.py

import requests
from typing import Dict, Any
from collectors.base_collector import Collector

class Collector3(Collector):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_endpoint = config[self.__class__.__name__]['api_endpoint']

    def collect(self) -> Any:
        """
        Fetch data from the API endpoint.
        Returns:
            Raw JSON data as a dictionary.
        """
        try:
            response = requests.get(self.api_endpoint)
            response.raise_for_status()
            self.logger.info("API data fetched successfully.")
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching data from API: {e}")
            return {}

    def process_data(self, raw_data: Any) -> Dict[str, Any]:
        """
        Process the raw JSON data.
        Args:
            raw_data: JSON data as a dictionary.
        Returns:
            A dictionary containing the processed data.
        """
        try:
            # Example processing: extract specific fields
            data = {
                'timestamp': raw_data.get('timestamp', ''),
                'value1': raw_data.get('value1', ''),
                'value2': raw_data.get('value2', ''),
                # Add more fields as necessary
            }

            # Add metadata
            data['date'] = data['timestamp'].split('T')[0] if 'T' in data['timestamp'] else 'unknown'

            # Validate required fields
            required_fields = ['date', 'timestamp', 'value1', 'value2']
            for field in required_fields:
                if field not in data or not data[field]:
                    self.logger.warning(f"Missing required field: {field}")
                    return {}

            self.logger.info("Data processed successfully.")
            return data

        except Exception as ex:
            self.logger.error(f"An unexpected error occurred during data processing: {ex}")
            return {}

    def create_table(self):
        """
        Create the collector3 table in the database.
        """
        create_collector3_table = f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL UNIQUE,
            timestamp TEXT NOT NULL,
            value1 TEXT,
            value2 TEXT
            -- Add other keys as necessary
        );
        """
        self.db_handler.execute_query(create_collector3_table)
        self.logger.info("Table 'collector3' ensured in the database.")
