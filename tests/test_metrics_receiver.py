# SysMoniTool/tests/test_metrics_receiver.py

import unittest
import socket
import threading
import time
from context import *
from automation import MetricsReceiver
import tempfile
import json
import os

class TestMetricsReceiver(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a temporary directory for test data
        cls.test_dir = tempfile.mkdtemp()
        cls.db_path = os.path.join(cls.test_dir, 'test_logs.db')
        
    def setUp(self):
        self.port = 12346  # Use a different port for testing
        self.receiver = MetricsReceiver(host='localhost', port=self.port, db_path=self.db_path)
        
        # Create a mock metrics sender
        self.mock_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.mock_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.mock_server.bind(('localhost', self.port))
        except OSError as e:
            self.skipTest(f"Port {self.port} is in use: {e}")
            
        self.mock_server.listen(1)
        
        # Start the mock server in a separate thread
        self.server_thread = threading.Thread(target=self._run_mock_server)
        self.server_thread.daemon = True
        self.server_thread.start()
        time.sleep(0.1)  # Small delay to ensure server is ready
        
    def tearDown(self):
        try:
            self.mock_server.close()
            time.sleep(0.1)  # Allow time for socket to close
        except Exception as e:
            print(f"Warning during tearDown: {e}")
            
    @classmethod
    def tearDownClass(cls):
        # Clean up temporary directory
        try:
            import shutil
            shutil.rmtree(cls.test_dir)
        except Exception as e:
            print(f"Warning during tearDownClass: {e}")
            
    def _run_mock_server(self):
        try:
            conn, _ = self.mock_server.accept()
            test_data = "50.0,60.0,70.0,80.0,2024-01-01 12:00:00"
            conn.send(test_data.encode())
            conn.close()
        except Exception as e:
            print(f"Warning in mock server: {e}")
            
    def test_receive_metrics(self):
        # Test connection
        try:
            self.assertTrue(self.receiver.connect())
            
            # Test metrics reception
            metrics = self.receiver.receive_metrics()
            self.assertIsNotNone(metrics)
            self.assertEqual(metrics['cpu_usage'], 50.0)
            self.assertEqual(metrics['memory_usage'], 60.0)
            self.assertEqual(metrics['disk_io'], 70.0)
            self.assertEqual(metrics['network_usage'], 80.0)
            self.assertEqual(metrics['timestamp'], '2024-01-01 12:00:00')
        except Exception as e:
            self.fail(f"Test failed with exception: {e}")
            
    def test_invalid_data_handling(self):
        # Test with invalid data format
        class MockSocket:
            def recv(self, size):
                return b"invalid,data,format"
            def close(self):
                pass
                
        self.receiver.socket = MockSocket()
        metrics = self.receiver.receive_metrics()
        self.assertIsNone(metrics)

if __name__ == '__main__':
    unittest.main()


