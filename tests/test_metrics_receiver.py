# SysMoniTool/tests/test_metrics_receiver.py
import unittest
import socket
import threading
import time
import sys
sys.path.append('../src/python')
from automation import MetricsReceiver

class TestMetricsReceiver(unittest.TestCase):
    def setUp(self):
        self.receiver = MetricsReceiver(host='localhost', port=12346)
        
        # Create a mock metrics sender
        self.mock_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.mock_server.bind(('localhost', 12346))
        self.mock_server.listen(1)
        
        # Start the mock server in a separate thread
        self.server_thread = threading.Thread(target=self._run_mock_server)
        self.server_thread.daemon = True
        self.server_thread.start()
        
    def tearDown(self):
        self.mock_server.close()
        
    def _run_mock_server(self):
        conn, _ = self.mock_server.accept()
        conn.send(b"50.0,60.0,70.0,80.0,2024-01-01 12:00:00")
        conn.close()
        
    def test_receive_metrics(self):
        # Test connection
        self.assertTrue(self.receiver.connect())
        
        # Test metrics reception
        metrics = self.receiver.receive_metrics()
        self.assertIsNotNone(metrics)
        self.assertEqual(metrics['cpu_usage'], 50.0)
        self.assertEqual(metrics['memory_usage'], 60.0)
        self.assertEqual(metrics['disk_io'], 70.0)
        self.assertEqual(metrics['network_usage'], 80.0)

if __name__ == '__main__':
    unittest.main()


