# SysMoniTool/tests/test_database.py

import unittest
import sqlite3
import os
from datetime import datetime
import sys
sys.path.append('../src/python')
from database import Database

class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.test_db_file = 'test_logs.db'
        self.db = Database(self.test_db_file)

    def tearDown(self):
        self.db.__del__()
        if os.path.exists(self.test_db_file):
            os.remove(self.test_db_file)

    def test_insert_and_get_metrics(self):
        test_metrics = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'cpu_usage': 50.0,
            'memory_usage': 60.0,
            'disk_io': 70.0,
            'network_usage': 80.0
        }
        
        # Test insertion
        self.db.insert_data(test_metrics)
        
        # Test retrieval
        latest = self.db.get_latest_metrics()
        self.assertIsNotNone(latest)
        self.assertEqual(latest[2], test_metrics['cpu_usage'])
        self.assertEqual(latest[3], test_metrics['memory_usage'])
        self.assertEqual(latest[4], test_metrics['disk_io'])
        self.assertEqual(latest[5], test_metrics['network_usage'])

    def test_update_and_get_thresholds(self):
        # Test threshold update
        self.db.update_threshold('cpu_usage', 85.0)
        self.db.update_threshold('memory_usage', 90.0)
        
        # Test threshold retrieval
        thresholds = self.db.get_thresholds()
        self.assertEqual(thresholds['cpu_usage'], 85.0)
        self.assertEqual(thresholds['memory_usage'], 90.0)


