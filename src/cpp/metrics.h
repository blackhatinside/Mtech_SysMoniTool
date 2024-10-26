// SysMoniTool/src/cpp/metrics.h
#ifndef METRICS_H
#define METRICS_H

#include <iostream>
#include <string>
#include <vector>
#include <sys/stat.h>
#include <sys/sysinfo.h>
#include <fstream>
#include <sstream>
#include <chrono>
#include <cstring>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <iomanip>  // Added for std::put_time
#include <csignal>    // Added for signal handling
#include <signal.h>   // Added for signal handling
#include <cstdio>     // Added for remove()

struct CPUStats {
    unsigned long long user;
    unsigned long long nice;
    unsigned long long system;
    unsigned long long idle;
    unsigned long long iowait;
    unsigned long long irq;
    unsigned long long softirq;
    unsigned long long steal;
};

struct SystemMetrics {
    double cpu_usage;        // Percentage (0-100)
    double memory_usage;     // Percentage (0-100)
    double disk_io;         // MB/s
    double network_usage;   // MB/s
    std::string timestamp;  // ISO 8601 format
    // Add more metrics as needed
    
    // Helper method to serialize metrics for network transmission
    std::string serialize() const {
        std::stringstream ss;
        ss << cpu_usage << "," 
           << memory_usage << "," 
           << disk_io << "," 
           << network_usage << ","
           << timestamp;
        return ss.str();
    }
};

class MetricsCollector {
private:
    CPUStats last_cpu_stats;
    std::chrono::steady_clock::time_point last_disk_read_time;
    unsigned long long last_disk_bytes_read;
    unsigned long long last_net_bytes;
    std::chrono::steady_clock::time_point last_net_time;  // Added this line
    int server_socket;
    
    CPUStats read_cpu_stats();
    double calculate_cpu_usage(const CPUStats& current, const CPUStats& last);
    double get_memory_usage();
    double get_disk_io();
    double get_network_usage();
    std::string get_current_timestamp();
    void setup_server_socket();

public:
    MetricsCollector();
    ~MetricsCollector();
    void collect_metrics(SystemMetrics& metrics);
    void send_metrics(const SystemMetrics& metrics);
};

#endif


