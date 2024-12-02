#!/bin/bash
# Script to delete .log files in the specified directory.

# Default log directory path
DEFAULT_LOG_DIR="./logs"

# If a directory path is provided as an argument, use it; otherwise, use the default
LOG_DIR="${1:-$DEFAULT_LOG_DIR}"

# Check if the specified directory exists
if [ -d "$LOG_DIR" ]; then
    echo "Searching for .log files in directory: $LOG_DIR"
    
    # Find and delete .log files in the specified directory
    find "$LOG_DIR" -type f -name "*.log" -exec rm -f {} +

    # Check if the deletion was successful
    if [ $? -eq 0 ]; then
        echo "All .log files successfully deleted in directory: $LOG_DIR"
    else
        echo "Error: Failed to delete .log files in the directory." >&2
        exit 1
    fi
else
    echo "Log directory '$LOG_DIR' does not exist."
    exit 1
fi
