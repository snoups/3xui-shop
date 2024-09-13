#!/bin/bash
# Script to delete log directories.

# Default log directory path
DEFAULT_LOG_DIR="./logs"

# If a directory path is provided as an argument, use it; otherwise, use the default
LOG_DIR="${1:-$DEFAULT_LOG_DIR}"

# Check if the specified directory exists
if [ -d "$LOG_DIR" ]; then
    echo "Deleting log directory: $LOG_DIR"
    
    # Attempt to remove the directory and its contents recursively and forcefully
    rm -rf "$LOG_DIR"
    
    # Check if the deletion was successful
    if [ $? -eq 0 ]; then
        echo "Log directory successfully deleted."
    else
        echo "Error: Failed to delete the log directory." >&2
        exit 1
    fi
else
    echo "Log directory '$LOG_DIR' does not exist."
    exit 1
fi