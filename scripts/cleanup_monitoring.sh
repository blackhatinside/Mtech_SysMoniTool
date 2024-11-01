#!/bin/bash

# SysMoniTool/scripts/cleanup_monitoring.sh

# cleanup_monitoring.sh
echo "Cleaning up monitoring system..."

# Kill any existing monitor processes
pkill -f "./build/monitor"
pkill -f "automation.py"

# Clean up socket
lsof -ti :12345 | xargs kill -9 2>/dev/null

# Remove PID files
rm -f /tmp/monitor.pid
rm -f data/monitor.pid

# Wait a moment for processes to completely terminate
sleep 2

echo "Cleanup completed"



