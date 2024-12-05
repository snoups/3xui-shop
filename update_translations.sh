#!/bin/bash
# The script extracts all messages with babel, 
# updates the translation files, stops before compiling to make changes, 
# and continues the process after a keystroke.

# Check to see if pybabel is installed
if ! command -v pybabel &> /dev/null; then
    echo “pybabel was not found.”
    exit 1
fi

# Set the variables
LOCALES_DIR="app/locales"
MESSAGES_POT="$LOCALES_DIR/messages.pot"
PROJECT_NAME="bot"
VERSION="0.1"
COPYRIGHT_HOLDER="snoups"
INPUT_DIR="."

echo "Retrieving messages..."
pybabel extract -o "$MESSAGES_POT" --copyright-holder="$COPYRIGHT_HOLDER" --project="$PROJECT_NAME" --version="$VERSION" --input-dirs="$INPUT_DIR"

echo "Russian translation update..."
pybabel update -i "$MESSAGES_POT" -d "$LOCALES_DIR" -D "$PROJECT_NAME" -l ru

echo "English translation update..."
pybabel update -i "$MESSAGES_POT" -d "$LOCALES_DIR" -D "$PROJECT_NAME" -l en

echo "Pause to edit translations. Press Enter to continue..."
read -r

echo "Compilation of translations..."
pybabel compile -d "$LOCALES_DIR" -D "$PROJECT_NAME"

echo "Done!"
