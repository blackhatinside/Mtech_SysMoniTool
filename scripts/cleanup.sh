# SysMoniTool/scripts/cleanup.sh
#!/bin/bash

LOG_FILE="/var/log/system_monitor_cleanup.log"

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
    echo "$1"
}

cleanup_temp_files() {
    log_message "Starting temporary files cleanup"
    find /tmp -type f -atime +7 -delete 2>/dev/null || true
    find /var/tmp -type f -atime +7 -delete 2>/dev/null || true
    log_message "Completed temporary files cleanup"
}

cleanup_system_cache() {
    log_message "Starting system cache cleanup"
    sync
    echo 1 > /proc/sys/vm/drop_caches 2>/dev/null || true
    log_message "Completed system cache cleanup"
}

manage_processes() {
    log_message "Starting process management"
    
    # Get top 5 memory-consuming processes
    ps aux | sort -nrk 4,4 | head -n 5 | while read -r user pid cpu mem rest; do
        if [ "$mem" -gt 80 ]; then  # Only kill if using >80% memory
            process_name=$(ps -p "$pid" -o comm=)
            log_message "Terminating high-memory process: $process_name (PID: $pid, Memory: $mem%)"
            kill -15 "$pid" 2>/dev/null || true  # SIGTERM first
            sleep 2
            kill -9 "$pid" 2>/dev/null || true   # SIGKILL if still running
        fi
    done
    
    log_message "Completed process management"
}

main() {
    log_message "Starting cleanup script"
    
    cleanup_temp_files
    cleanup_system_cache
    manage_processes
    
    log_message "Cleanup script completed"
}

main "$@"


