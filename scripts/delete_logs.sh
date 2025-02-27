#!/bin/bash

# delete_logs.sh
# -----------------------------------------------------------------------------
# Script to delete .log, .zip, and .gz files from a specified directory.
#
# Options:
#     --dir PATH   Specify the directory to clean logs and archives from (default: app/logs).
#     --help       Display this help message.
# -----------------------------------------------------------------------------

DEFAULT_LOG_DIR="app/logs"
LOG_DIR="$DEFAULT_LOG_DIR"

show_help() {
    grep '^#' "$0" | cut -c 5-
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dir)
            shift
            if [[ -n "$1" ]]; then
                LOG_DIR="$1"
                shift
            else
                echo "❌ Error: --dir flag requires a directory path." >&2
                exit 1
            fi
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            echo "❌ Error: Unknown option '$1'. Use --help for usage information." >&2
            exit 1
            ;;
    esac
done

if [[ -d "$LOG_DIR" ]]; then
    echo "🔍 Searching for .log, .zip, and .gz files in: $LOG_DIR"

    if find "$LOG_DIR" -type f \( -name "*.log" -o -name "*.zip" -o -name "*.gz" \) -exec rm -f {} +; then
        echo "✅ All .log, .zip, and .gz files were successfully deleted from: $LOG_DIR"
    else
        echo "❌ Failed to delete some files." >&2
        exit 1
    fi
else
    echo "❌ Directory '$LOG_DIR' does not exist." >&2
    exit 1
fi
