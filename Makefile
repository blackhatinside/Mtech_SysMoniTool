CXX = g++
CXXFLAGS = -Wall -std=c++17
SRC_DIR = src/cpp
BUILD_DIR = build

all: monitor

monitor: $(SRC_DIR)/monitor.cpp $(SRC_DIR)/metrics.h
	@mkdir -p $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) $(SRC_DIR)/monitor.cpp -o $(BUILD_DIR)/monitor

clean:
	rm -rf $(BUILD_DIR)

.PHONY: all clean


