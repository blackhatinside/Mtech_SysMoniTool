# SysMoniTool/src/python/cli.py
import argparse
import json
import time
from datetime import datetime, timedelta
from database import Database
from automation import MetricsReceiver
import subprocess
import signal
import os
import psutil
import tabulate

class MonitoringCLI:
    def __init__(self):
        self.db = Database('data/logs.db')
        self.pid_file = 'data/monitor.pid'

    def start_monitoring(self):
        if self.is_monitoring_running():
            print("Monitoring is already running.")
            return
        
        try:
            # Start the C++ monitor process
            cpp_process = subprocess.Popen(['./build/monitor'])
            
            # Start the Python automation process
            python_process = subprocess.Popen(['python3', 'src/python/automation.py'])
            
            # Save PIDs
            with open(self.pid_file, 'w') as f:
                json.dump({
                    'cpp_pid': cpp_process.pid,
                    'python_pid': python_process.pid
                }, f)
            
            print("Monitoring started successfully.")
        except Exception as e:
            print(f"Failed to start monitoring: {e}")

    def stop_monitoring(self):
        if not self.is_monitoring_running():
            print("Monitoring is not running.")
            return
        
        try:
            with open(self.pid_file, 'r') as f:
                pids = json.load(f)
            
            # Terminate processes
            for name, pid in pids.items():
                try:
                    os.kill(pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
            
            # Remove PID file
            os.remove(self.pid_file)
            print("Monitoring stopped successfully.")
        except Exception as e:
            print(f"Failed to stop monitoring: {e}")

    def is_monitoring_running(self):
        if not os.path.exists(self.pid_file):
            return False
        
        try:
            with open(self.pid_file, 'r') as f:
                pids = json.load(f)
            
            for pid in pids.values():
                if not psutil.pid_exists(pid):
                    return False
            return True
        except:
            return False

    def view_current_metrics(self):
        latest = self.db.get_latest_metrics()
        if not latest:
            print("No metrics available.")
            return
        
        headers = ['Metric', 'Value']
        data = [
            ['Timestamp', latest[1]],
            ['CPU Usage', f"{latest[2]:.1f}%"],
            ['Memory Usage', f"{latest[3]:.1f}%"],
            ['Disk I/O', f"{latest[4]:.1f} MB/s"],
            ['Network Usage', f"{latest[5]:.1f} MB/s"]
        ]
        
        print("\nCurrent System Metrics:")
        print(tabulate.tabulate(data, headers=headers, tablefmt='grid'))

    def query_historical_data(self, start_date, end_date):
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            data = self.db.query_data(start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))
            
            if not data:
                print("No data found for the specified period.")
                return
            
            headers = ['Timestamp', 'CPU Usage (%)', 'Memory Usage (%)', 
                      'Disk I/O (MB/s)', 'Network Usage (MB/s)']
            formatted_data = [
                [row[1], f"{row[2]:.1f}", f"{row[3]:.1f}", 
                 f"{row[4]:.1f}", f"{row[5]:.1f}"] 
                for row in data
            ]
            
            print(f"\nHistorical Data ({start_date} to {end_date}):")
            print(tabulate.tabulate(formatted_data, headers=headers, tablefmt='grid'))
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD format.")

    def configure_thresholds(self):
        current_thresholds = self.db.get_thresholds()
        
        print("\nCurrent Thresholds:")
        for name, value in current_thresholds.items():
            print(f"{name}: {value}")
        
        print("\nEnter new threshold values (press Enter to keep current value):")
        metrics = {
            'cpu_usage': 'CPU Usage (%)',
            'memory_usage': 'Memory Usage (%)',
            'disk_io': 'Disk I/O (MB/s)',
            'network_usage': 'Network Usage (MB/s)'
        }
        
        for key, description in metrics.items():
            current = current_thresholds.get(key, 0)
            while True:
                try:
                    value = input(f"{description} [{current}]: ").strip()
                    if not value:
                        value = current
                    value = float(value)
                    if 0 <= value <= 100 or key in ['disk_io', 'network_usage']:
                        self.db.update_threshold(key, value)
                        break
                    print("Please enter a valid percentage (0-100)")
                except ValueError:
                    print("Please enter a valid number")
        
        print("\nThresholds updated successfully.")

def main():
    parser = argparse.ArgumentParser(description='System Monitoring and Automation Tool')
    parser.add_argument('--start', action='store_true', help='Start monitoring')
    parser.add_argument('--stop', action='store_true', help='Stop monitoring')
    parser.add_argument('--view', action='store_true', help='View current system metrics')
    parser.add_argument('--query', nargs=2, metavar=('START_DATE', 'END_DATE'), 
                        help='Query historical data (format: YYYY-MM-DD)')
    parser.add_argument('--config', action='store_true', help='Configure thresholds')

    args = parser.parse_args()
    cli = MonitoringCLI()

    if args.start:
        cli.start_monitoring()
    elif args.stop:
        cli.stop_monitoring()
    elif args.view:
        cli.view_current_metrics()
    elif args.query:
        cli.query_historical_data(args.query[0], args.query[1])
    elif args.config:
        cli.configure_thresholds()
    else:
        parser.print_help()

if __name__ == '__main__':
    main()


