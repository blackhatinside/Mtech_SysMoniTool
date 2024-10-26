// SysMoniTool/src/cpp/monitor.cpp
#include "metrics.h"

// Add at the top of monitor.cpp after includes
void write_pid_file() {
    std::ofstream pid_file("/tmp/monitor.pid");
    pid_file << getpid();
    pid_file.close();
}

void remove_pid_file() {
    std::remove("/tmp/monitor.pid");
}
    
MetricsCollector::MetricsCollector() {
    last_cpu_stats = read_cpu_stats();
    last_disk_read_time = std::chrono::steady_clock::now();
    last_net_time = std::chrono::steady_clock::now();  // Initialize last_net_time
    
    // Initialize disk and network counters
    std::ifstream disk_stats("/proc/diskstats");
    std::string line;
    while (std::getline(disk_stats, line)) {
        if (line.find(" sda ") != std::string::npos) {
            std::istringstream iss(line);
            std::string token;
            for (int i = 0; i < 6; i++) iss >> token;
            last_disk_bytes_read = std::stoull(token) * 512; // Convert sectors to bytes
            break;
        }
    }
    
    std::ifstream net_stats("/proc/net/dev");
    while (std::getline(net_stats, line)) {
        if (line.find("eth0:") != std::string::npos || line.find("wlan0:") != std::string::npos) {
            std::istringstream iss(line);
            std::string interface;
            iss >> interface;
            iss >> last_net_bytes;
            break;
        }
    }
    
    setup_server_socket();
}

MetricsCollector::~MetricsCollector() {
    close(server_socket);
}

void MetricsCollector::setup_server_socket() {
    server_socket = socket(AF_INET, SOCK_STREAM, 0);
    if (server_socket < 0) {
        throw std::runtime_error("Failed to create socket");
    }
    
    sockaddr_in server_addr;
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(12345);
    server_addr.sin_addr.s_addr = INADDR_ANY;
    
    if (bind(server_socket, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
        throw std::runtime_error("Failed to bind socket");
    }
    
    listen(server_socket, 1);
}

CPUStats MetricsCollector::read_cpu_stats() {
    std::ifstream stat_file("/proc/stat");
    std::string line;
    std::getline(stat_file, line);
    
    CPUStats stats;
    std::istringstream iss(line);
    std::string cpu;
    iss >> cpu >> stats.user >> stats.nice >> stats.system >> stats.idle
        >> stats.iowait >> stats.irq >> stats.softirq >> stats.steal;
    
    return stats;
}

double MetricsCollector::calculate_cpu_usage(const CPUStats& current, const CPUStats& last) {
    unsigned long long prev_idle = last.idle + last.iowait;
    unsigned long long idle = current.idle + current.iowait;
    
    unsigned long long prev_non_idle = last.user + last.nice + last.system + 
                                     last.irq + last.softirq + last.steal;
    unsigned long long non_idle = current.user + current.nice + current.system + 
                                 current.irq + current.softirq + current.steal;
    
    unsigned long long prev_total = prev_idle + prev_non_idle;
    unsigned long long total = idle + non_idle;
    
    unsigned long long total_diff = total - prev_total;
    unsigned long long idle_diff = idle - prev_idle;
    
    return total_diff == 0 ? 0.0 : (100.0 * (total_diff - idle_diff)) / total_diff;
}

double MetricsCollector::get_memory_usage() {
    struct sysinfo si;
    if (sysinfo(&si) != 0) {
        return 0.0;
    }
    
    unsigned long total_ram = si.totalram;
    unsigned long free_ram = si.freeram;
    return 100.0 * (1.0 - ((double)free_ram / total_ram));
}

double MetricsCollector::get_disk_io() {
    std::ifstream disk_stats("/proc/diskstats");
    std::string line;
    unsigned long long current_bytes_read = 0;
    
    while (std::getline(disk_stats, line)) {
        if (line.find(" sda ") != std::string::npos) {
            std::istringstream iss(line);
            std::string token;
            for (int i = 0; i < 6; i++) iss >> token;
            current_bytes_read = std::stoull(token) * 512; // Convert sectors to bytes
            break;
        }
    }
    
    auto current_time = std::chrono::steady_clock::now();
    double seconds = std::chrono::duration<double>(current_time - last_disk_read_time).count();
    
    // Add bounds checking
    if (seconds < 0.001) seconds = 0.001; // Prevent division by very small numbers
    if (current_bytes_read < last_disk_bytes_read) current_bytes_read = last_disk_bytes_read; // Prevent negative values
    
    double mb_per_second = (current_bytes_read - last_disk_bytes_read) / (1024.0 * 1024.0) / seconds;
    
    // Add sanity check for unrealistic values
    if (mb_per_second > 10000) // Cap at 10GB/s which is already very high
        mb_per_second = 0;
    
    last_disk_bytes_read = current_bytes_read;
    last_disk_read_time = current_time;
    
    return mb_per_second;
}

double MetricsCollector::get_network_usage() {
    std::ifstream net_stats("/proc/net/dev");
    std::string line;
    unsigned long long current_bytes = 0;
    
    while (std::getline(net_stats, line)) {
        if (line.find("eth0:") != std::string::npos || line.find("wlan0:") != std::string::npos) {
            std::istringstream iss(line);
            std::string interface;
            iss >> interface;
            iss >> current_bytes;
            break;
        }
    }
    
    auto current_time = std::chrono::steady_clock::now();
    double seconds = std::chrono::duration<double>(current_time - last_net_time).count();
    
    // Add bounds checking
    if (seconds < 0.001) seconds = 0.001; // Prevent division by very small numbers
    if (current_bytes < last_net_bytes) current_bytes = last_net_bytes; // Prevent negative values
    
    double mb_per_second = (current_bytes - last_net_bytes) / (1024.0 * 1024.0) / seconds;
    
    // Add sanity check for unrealistic values
    if (mb_per_second > 1000) // Cap at 1GB/s which is already very high
        mb_per_second = 0;
    
    last_net_bytes = current_bytes;
    last_net_time = current_time;
    
    return mb_per_second;
}

std::string MetricsCollector::get_current_timestamp() {
    auto now = std::chrono::system_clock::now();
    auto now_c = std::chrono::system_clock::to_time_t(now);
    std::stringstream ss;
    ss << std::put_time(std::localtime(&now_c), "%Y-%m-%d %H:%M:%S");
    return ss.str();
}

void MetricsCollector::collect_metrics(SystemMetrics& metrics) {
    CPUStats current_cpu_stats = read_cpu_stats();
    metrics.cpu_usage = calculate_cpu_usage(current_cpu_stats, last_cpu_stats);
    last_cpu_stats = current_cpu_stats;
    
    metrics.memory_usage = get_memory_usage();
    metrics.disk_io = get_disk_io();
    metrics.network_usage = get_network_usage();
    metrics.timestamp = get_current_timestamp();
}

void MetricsCollector::send_metrics(const SystemMetrics& metrics) {
    sockaddr_in client_addr;
    socklen_t client_len = sizeof(client_addr);
    int client_socket = accept(server_socket, (struct sockaddr*)&client_addr, &client_len);
    
    if (client_socket >= 0) {
        std::string data = metrics.serialize();
        send(client_socket, data.c_str(), data.length(), 0);
        close(client_socket);
    }
}

// Add in main() function, right at the start:
int main() {
    try {
        // Check if already running
        std::ifstream existing_pid("/tmp/monitor.pid");
        if (existing_pid.good()) {
            std::string pid_str;
            existing_pid.close();
            std::cerr << "Monitor process already running" << std::endl;
            return 1;
        }
        
        write_pid_file();
        
        MetricsCollector collector;
        SystemMetrics metrics;
        
        // Set up signal handler for cleanup
        signal(SIGTERM, [](int) {
            remove_pid_file();
            exit(0);
        });
        
        while (true) {
            collector.collect_metrics(metrics);
            collector.send_metrics(metrics);
            sleep(1);  // Collect metrics every second
        }
    } catch (const std::exception& e) {
        remove_pid_file();
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }
    
    remove_pid_file();
    return 0;
}


