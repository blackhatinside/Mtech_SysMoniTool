# SysMoniTool/src/python/automation.py
import socket
import time
import subprocess
import logging
from datetime import datetime
from database import Database

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/system_monitor.log'),
        logging.StreamHandler()
    ]
)

class MetricsReceiver:
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.db = Database('data/logs.db')
        self.thresholds = {
            'cpu_usage': 80.0,
            'memory_usage': 90.0,
            'disk_io': 100.0,  # MB/s
            'network_usage': 50.0  # MB/s
        }
    
    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            return True
        except Exception as e:
            logging.error(f"Failed to connect: {e}")
            return False

    def receive_metrics(self):
        try:
            data = self.socket.recv(1024).decode()
            if not data:
                return None
            
            # Parse CSV formatted metrics
            values = data.strip().split(',')
            if len(values) != 5:
                return None
            
            metrics = {
                'cpu_usage': float(values[0]),
                'memory_usage': float(values[1]),
                'disk_io': float(values[2]),
                'network_usage': float(values[3]),
                'timestamp': values[4]
            }
            return metrics
        except Exception as e:
            logging.error(f"Error receiving metrics: {e}")
            return None

    def trigger_automated_actions(self, metrics):
        if metrics['cpu_usage'] > self.thresholds['cpu_usage']:
            logging.warning(f"High CPU usage detected: {metrics['cpu_usage']}%")
            subprocess.call(['./scripts/cleanup.sh'])
        
        if metrics['memory_usage'] > self.thresholds['memory_usage']:
            logging.warning(f"High memory usage detected: {metrics['memory_usage']}%")
            subprocess.call(['./scripts/alert.sh'])
        
        if metrics['disk_io'] > self.thresholds['disk_io']:
            logging.warning(f"High disk I/O detected: {metrics['disk_io']} MB/s")
            subprocess.call(['./scripts/cleanup.sh'])
        
        if metrics['network_usage'] > self.thresholds['network_usage']:
            logging.warning(f"High network usage detected: {metrics['network_usage']} MB/s")
            subprocess.call(['./scripts/alert.sh'])

    def run(self):
        while True:
            if not self.connect():
                time.sleep(5)
                continue
            
            try:
                metrics = self.receive_metrics()
                if metrics:
                    self.db.insert_data(metrics)
                    self.trigger_automated_actions(metrics)
            except Exception as e:
                logging.error(f"Error in main loop: {e}")
            finally:
                self.socket.close()
            
            time.sleep(1)

if __name__ == '__main__':
    receiver = MetricsReceiver()
    receiver.run()


