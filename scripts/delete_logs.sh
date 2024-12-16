#!/bin/bash
# Script to delete .log files in a specified directory.

# Default directory for logs
DEFAULT_LOG_DIR="./logs"

# Use the provided directory path or default to the predefined one
LOG_DIR="${1:-$DEFAULT_LOG_DIR}"

# Check if the directory exists
if [ -d "$LOG_DIR" ]; then
    echo "Looking for .log files in: $LOG_DIR"
    
    # Find and delete all .log files
    find "$LOG_DIR" -type f -name "*.log" -exec rm -f {} +

    # Verify if deletion succeeded
    if [ $? -eq 0 ]; then
        echo "All .log files were successfully deleted from: $LOG_DIR"
    else
        echo "Error: Failed to delete some .log files." >&2
        exit 1
    fi
else
    echo "Error: Directory '$LOG_DIR' does not exist." >&2
    exit 1
fi
