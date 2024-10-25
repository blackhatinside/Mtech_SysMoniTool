#ifndef METRICS_H
#define METRICS_H

#include <iostream>
#include <string>
#include <sys/stat.h>

struct SystemMetrics {
    double cpu_usage;
    double memory_usage;
    double disk_io;
    double network_usage;
    // Add more metrics as needed
};

void collect_system_metrics(SystemMetrics& metrics);
void send_metrics_to_python(const SystemMetrics& metrics);

#endif
