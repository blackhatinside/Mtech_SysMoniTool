# SysMoniTool/tests/test_database.py

import unittest
import sqlite3
import os
from datetime import datetime
from context import *
from database import Database
import tempfile

class TestDatabase(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for test database
        self.test_dir = tempfile.mkdtemp()
        self.test_db_file = os.path.join(self.test_dir, 'test_logs.db')
        self.db = Database(self.test_db_file)

    def tearDown(self):
        self.db.__del__()
        try:
            import shutil
            shutil.rmtree(self.test_dir)
        except Exception as e:
            print(f"Warning during tearDown: {e}")

    def test_insert_and_get_metrics(self):
        test_metrics = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'cpu_usage': 50.0,
            'memory_usage': 60.0,
            'disk_io': 70.0,
            'network_usage': 80.0
        }
        
        # Test insertion
        try:
            self.db.insert_data(test_metrics)
            
            # Test retrieval
            latest = self.db.get_latest_metrics()
            self.assertIsNotNone(latest)
            self.assertEqual(latest[2], test_metrics['cpu_usage'])
            self.assertEqual(latest[3], test_metrics['memory_usage'])
            self.assertEqual(latest[4], test_metrics['disk_io'])
            self.assertEqual(latest[5], test_metrics['network_usage'])
        except Exception as e:
            self.fail(f"Test failed with exception: {e}")

    def test_update_and_get_thresholds(self):
        try:
            # Test threshold update
            self.db.update_threshold('cpu_usage', 85.0)
            self.db.update_threshold('memory_usage', 90.0)
            
            # Test threshold retrieval
            thresholds = self.db.get_thresholds()
            self.assertEqual(thresholds['cpu_usage'], 85.0)
            self.assertEqual(thresholds['memory_usage'], 90.0)
        except Exception as e:
            self.fail(f"Test failed with exception: {e}")
            
    def test_invalid_data_handling(self):
        # Test with invalid metrics data
        invalid_metrics = {
            'timestamp': 'invalid_date',
            'cpu_usage': 'not_a_number',
            'memory_usage': None,
            'disk_io': '',
            'network_usage': 'error'
        }
        
        with self.assertRaises(sqlite3.Error):
            self.db.insert_data(invalid_metrics)

if __name__ == '__main__':
    unittest.main()


