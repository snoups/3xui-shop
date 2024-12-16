#!/bin/bash
# Script for managing translations: extracting messages, updating translation files, and compiling.

# Ensure pybabel is installed
if ! command -v pybabel &> /dev/null; then
    echo "Error: pybabel is not installed. Please install it first." >&2
    exit 1
fi

# Variables
LOCALES_DIR="app/locales"                   # Directory containing locale files
MESSAGES_POT="$LOCALES_DIR/messages.pot"    # Path to the messages template
PROJECT_NAME="bot"                          # Project name
VERSION="0.1"                               # Project version
COPYRIGHT_HOLDER="snoups"                   # Copyright holder
INPUT_DIR="."                               # Input directory for extracting messages

# Extract messages
echo "Extracting messages..."
pybabel extract \
    -o "$MESSAGES_POT" \
    -k _:1,1t \
    -k _:1,2 \
    -k __ \
    --copyright-holder="$COPYRIGHT_HOLDER" \
    --project="$PROJECT_NAME" \
    --version="$VERSION" \
    --input-dirs="$INPUT_DIR"

# Update translations
echo "Updating Russian translations..."
pybabel update -i "$MESSAGES_POT" -d "$LOCALES_DIR" -D "$PROJECT_NAME" -l ru

echo "Updating English translations..."
pybabel update -i "$MESSAGES_POT" -d "$LOCALES_DIR" -D "$PROJECT_NAME" -l en

# Pause for editing
echo "Pause for editing translations. Press Enter to continue..."
read -r

# Compile translations
echo "Compiling translations..."
pybabel compile -d "$LOCALES_DIR" -D "$PROJECT_NAME"

echo "Translation management complete!"
