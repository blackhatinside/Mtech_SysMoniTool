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
import socket

class MonitoringCLI:
    def __init__(self):
        self.db = Database('data/logs.db')
        self.pid_file = 'data/monitor.pid'
        self.cpp_pid_file = '/tmp/monitor.pid'
        self.port = 12345

    def is_port_in_use(self):
        """Check if the monitoring port is already in use."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                return s.connect_ex(('localhost', self.port)) == 0
        except:
            return False

    def kill_process_and_children(self, pid):
        """Recursively kill a process and all its children."""
        try:
            parent = psutil.Process(pid)
            children = parent.children(recursive=True)
            for child in children:
                try:
                    child.kill()
                except psutil.NoSuchProcess:
                    pass
            parent.kill()
        except psutil.NoSuchProcess:
            pass

    def cleanup_existing_processes(self):
        """Clean up any existing monitor and automation processes."""
        # Clean up processes by name
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.cmdline()
                if len(cmdline) >= 2:
                    if './build/monitor' in ' '.join(cmdline) or 'automation.py' in cmdline[1]:
                        self.kill_process_and_children(proc.pid)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        # Clean up socket if it exists
        try:
            subprocess.run(['pkill', '-f', '12345'], stderr=subprocess.DEVNULL)
        except subprocess.SubprocessError:
            pass

        # Remove PID files
        if os.path.exists(self.pid_file):
            os.remove(self.pid_file)
        if os.path.exists(self.cpp_pid_file):
            os.remove(self.cpp_pid_file)

        # Wait for port to be released
        timeout = time.time() + 5  # 5 second timeout
        while self.is_port_in_use() and time.time() < timeout:
            time.sleep(0.1)

    def start_monitoring(self):
        print("Starting monitoring system...")
        
        # Clean up any existing processes first
        self.cleanup_existing_processes()
        
        # Check if port is still in use after cleanup
        if self.is_port_in_use():
            print("Error: Port 12345 is still in use after cleanup. Please check for blocking processes.")
            return
        
        try:
            # Start the C++ monitor process
            cpp_process = subprocess.Popen(['./build/monitor'])
            time.sleep(1)  # Give the monitor time to start
            
            if not cpp_process.poll() is None:  # Check if process is still running
                raise Exception("Monitor process failed to start")
            
            # Start the Python automation process
            python_process = subprocess.Popen(['python3', 'src/python/automation.py'])
            time.sleep(1)  # Give the automation process time to start
            
            if not python_process.poll() is None:  # Check if process is still running
                cpp_process.terminate()
                raise Exception("Automation process failed to start")
            
            # Save PIDs
            with open(self.pid_file, 'w') as f:
                json.dump({
                    'cpp_pid': cpp_process.pid,
                    'python_pid': python_process.pid,
                    'start_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }, f)
            
            print("Monitoring started successfully.")
        except Exception as e:
            print(f"Failed to start monitoring: {e}")
            self.cleanup_existing_processes()

    def stop_monitoring(self):
        print("Stopping monitoring system...")
        if os.path.exists(self.pid_file):
            try:
                with open(self.pid_file, 'r') as f:
                    pids = json.load(f)
                
                # Terminate processes
                for name, pid in pids.items():
                    if name != 'start_time':  # Skip the timestamp
                        try:
                            process = psutil.Process(pid)
                            self.kill_process_and_children(pid)
                        except psutil.NoSuchProcess:
                            pass
                
                self.cleanup_existing_processes()
                print("Monitoring stopped successfully.")
            except Exception as e:
                print(f"Failed to stop monitoring: {e}")
        else:
            print("Monitoring is not running.")

    def is_monitoring_running(self):
        if not os.path.exists(self.pid_file):
            return False
        
        try:
            with open(self.pid_file, 'r') as f:
                pids = json.load(f)
            
            # Check each process
            for name, pid in pids.items():
                if name != 'start_time':  # Skip the timestamp
                    if not psutil.pid_exists(pid):
                        return False
                    try:
                        process = psutil.Process(pid)
                        if process.status() == 'zombie':
                            return False
                    except psutil.NoSuchProcess:
                        return False
            return True
        except:
            return False

    # [Rest of the code remains unchanged: view_current_metrics, query_historical_data, configure_thresholds]
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
        # Default thresholds if none exist
        default_thresholds = {
            'cpu_usage': 80.0,
            'memory_usage': 90.0,
            'disk_io': 100.0,
            'network_usage': 50.0
        }

        # Get current thresholds, use defaults if none exist
        current_thresholds = self.db.get_thresholds()
        if not current_thresholds:
            current_thresholds = default_thresholds
            # Initialize database with defaults
            for name, value in default_thresholds.items():
                self.db.update_threshold(name, value)

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


