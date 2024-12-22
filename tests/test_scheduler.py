# tests/test_scheduler.py

import unittest
from scheduler.scheduler import run_collector
from collectors.nj_existing_housing_trade_info import NJExistingHousingTradeInfoCollector
from config.config import config
from unittest.mock import MagicMock, patch
from notifier.email_notifier import EmailNotifier

class TestScheduler(unittest.TestCase):
    def setUp(self):
        self.collector = NJExistingHousingTradeInfoCollector(config)
        # Mock methods to prevent actual API calls and email sending
        self.collector.collect = MagicMock(return_value="<div class='busniess_banner_num'><span>Key1：Value1</span></div>")
        self.collector.process_data = MagicMock(return_value={
            'date': '2024-12-07',
            'timestamp': '2024-12-07 02:00:00',
            'Key1': 'Value1',
            'Key2': 'Value2'
        })
        self.collector.db_handler.insert_trade_info = MagicMock()
        self.collector.db_handler.get_user_emails = MagicMock(return_value=['test@example.com'])

    @patch.object(EmailNotifier, 'send_email')
    def test_run_collector(self, mock_send_email):
        # Run the collector
        run_collector(self.collector)

        # Assertions
        self.collector.collect.assert_called_once()
        self.collector.process_data.assert_called_once_with("<div class='busniess_banner_num'><span>Key1：Value1</span></div>")
        self.collector.db_handler.insert_trade_info.assert_called_once_with(
            'njexistinghousingtradeinfo',
            {
                'date': '2024-12-07',
                'timestamp': '2024-12-07 02:00:00',
                'Key1': 'Value1',
                'Key2': 'Value2'
            }
        )
        mock_send_email.assert_called_once_with(
            "Data Notification: NJExistingHousingTradeInfoCollector",
            "Here is the latest data:\n\n"
            "date: 2024-12-07\n"
            "timestamp: 2024-12-07 02:00:00\n"
            "Key1: Value1\n"
            "Key2: Value2\n",
            'test@example.com'
        )

if __name__ == '__main__':
    unittest.main()
