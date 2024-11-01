#!/bin/bash

# SysMoniTool/scripts/alert.sh

LOG_FILE="/var/log/system_monitor_alerts.log"
ADMIN_EMAIL="admin@example.com"
SLACK_WEBHOOK_URL="your_slack_webhook_url"  # Optional: Add if using Slack

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
    echo "$1"
}

send_email_alert() {
    local subject="$1"
    local message="$2"
    echo "$message" | mail -s "$subject" "$ADMIN_EMAIL" || true
    log_message "Email alert sent: $subject"
}

# Optional: Add Slack notification
send_slack_alert() {
    local message="$1"
    if [ -n "$SLACK_WEBHOOK_URL" ]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"$message\"}" \
            "$SLACK_WEBHOOK_URL"
        log_message "Slack alert sent"
    fi
}

main() {
    local alert_type="$1"
    local metric_value="$2"
    
    # Add debug logging for script triggering
    log_message "Alert script triggered with parameters: type=$alert_type, value=$metric_value"
    
    case "$alert_type" in
        "cpu")
            message="High CPU usage detected: ${metric_value}%"
            ;;
        "memory")
            message="High memory usage detected: ${metric_value}%"
            ;;
        "disk")
            message="High disk I/O detected: ${metric_value} MB/s"
            ;;
        "network")
            message="High network usage detected: ${metric_value} MB/s"
            ;;
        *)
            message="System alert: Unknown metric exceeded threshold"
            ;;
    esac
    
    log_message "$message"
    send_email_alert "System Alert: $alert_type" "$message"
}

# Create log directory and file if they don't exist
mkdir -p "$(dirname "$LOG_FILE")"
touch "$LOG_FILE"

main "$@"


