### System Monitoring and Automation Tool

This project is a comprehensive Linux-based system monitoring and automation tool that tracks CPU, memory, disk I/O, network usage, and process performance. It includes an automated alerting system that triggers scripts based on system thresholds.



## Features
```
- Real-time system metrics monitoring
- Automated actions based on defined thresholds
- Historical data storage and querying
- Command-line interface for interaction
```

## Requirements
```
- Linux-based operating system
- C++ compiler (e.g., g++)
- Python 3
- SQLite
```

## Setup
```
1. Clone the repository:

if port is already in use:
	sudo lsof -i :12345
	sudo kill -9 <PID>
```
## Project Directory Structure
``` 
SysMoniTool/
├── build/
│   └── monitor
├── data/
│   ├── logs.db
│   └── system_monitor.log
├── Makefile
├── output/
│   └── SysMoniTool.png
├── README.md
├── requirements.txt
├── scripts/
│   ├── alert.sh
│   ├── cleanup_monitoring.sh
│   └── cleanup.sh
├── src/
│   ├── cpp/
│   │   ├── metrics.h
│   │   └── monitor.cpp
│   └── python/
│       ├── automation.py
│       ├── cli.py
│       ├── database.py
│       └── __pycache__/
│           ├── automation.cpython-310.pyc
│           └── database.cpython-310.pyc
└── SRS_doc.txt
```

## Demo Run the Project
```
sudo mkdir -p /var/log
sudo touch /var/log/system_monitor_cleanup.log
sudo chown -R $USER:$USER /var/log/system_monitor_cleanup.log

chmod +x scripts/*.sh
g++ -o build/monitor src/cpp/monitor.cpp -std=c++11
chmod +x build/monitor

python3 src/python/cli.py --start
python3 src/python/cli.py --view
python3 src/python/cli.py --config
python3 src/python/cli.py --view
python3 src/python/cli.py --stop
python3 -m unittest discover tests
```



