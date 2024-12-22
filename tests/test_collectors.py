# tests/test_collectors.py

import unittest
from collectors.nj_existing_housing_trade_info import NJExistingHousingTradeInfoCollector
from collectors.collector3 import Collector3
from config.config import config
from unittest.mock import patch, MagicMock

class TestNJExistingHousingTradeInfoCollector(unittest.TestCase):
    def setUp(self):
        self.collector = NJExistingHousingTradeInfoCollector(config)

    def test_collect(self):
        raw_data = self.collector.collect()
        self.assertIsInstance(raw_data, str)
        self.assertGreater(len(raw_data), 0)

    def test_process_data(self):
        # Mock raw_data
        raw_data = "<div class='busniess_banner_num'><span>Key1：Value1</span><span>Key2：Value2</span></div>"
        processed_data = self.collector.process_data(raw_data)
        self.assertIsInstance(processed_data, dict)
        self.assertIn('date', processed_data)
        self.assertIn('timestamp', processed_data)
        self.assertIn('Key1', processed_data)
        self.assertIn('Key2', processed_data)

class TestCollector3(unittest.TestCase):
    def setUp(self):
        self.collector = Collector3(config)

    @patch('requests.get')
    def test_collect(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'timestamp': '2024-12-08T00:00:00Z',
            'value1': '100',
            'value2': '200'
        }
        raw_data = self.collector.collect()
        self.assertIsInstance(raw_data, dict)
        self.assertEqual(raw_data['value1'], '100')
        self.assertEqual(raw_data['value2'], '200')

    def test_process_data(self):
        # Mock raw_data
        raw_data = {
            'timestamp': '2024-12-08T00:00:00Z',
            'value1': '100',
            'value2': '200'
        }
        processed_data = self.collector.process_data(raw_data)
        self.assertIsInstance(processed_data, dict)
        self.assertIn('date', processed_data)
        self.assertIn('timestamp', processed_data)
        self.assertIn('value1', processed_data)
        self.assertIn('value2', processed_data)

if __name__ == '__main__':
    unittest.main()
