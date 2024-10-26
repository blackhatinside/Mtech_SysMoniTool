# System Monitoring and Automation Tool

This project is a comprehensive Linux-based system monitoring and automation tool that tracks CPU, memory, disk I/O, network usage, and process performance. It includes an automated alerting system that triggers scripts based on system thresholds.

## Features
- Real-time system metrics monitoring
- Automated actions based on defined thresholds
- Historical data storage and querying
- Command-line interface for interaction

## Requirements
- Linux-based operating system
- C++ compiler (e.g., g++)
- Python 3
- SQLite

## Setup
1. Clone the repository:

# Project Directory Structure
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



