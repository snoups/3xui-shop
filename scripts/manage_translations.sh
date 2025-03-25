#!/bin/bash

# manage_translations.sh
# ─────────────────────────────────────────────────────────────────────────────
# Script for managing translations using Babel
#
# Options:
#     --test init    - Create a test project
#     --test merge   - Update translations in the test project
#     --merge        - Update translations in the production project
#     --update       - Extract and compile translations
#     --help         - Show help
# ─────────────────────────────────────────────────────────────────────────────

set -e

DOMAIN="bot"
MAIN_TRANSLATIONS_DIR="app/locales"
BACKUP_TRANSLATIONS_DIR="app/locales/backup"
LOCALES_DIR="app/locales"
MESSAGES_POT="$LOCALES_DIR/$DOMAIN.pot"
PROJECT_NAME="$DOMAIN"
VERSION="0.1"
COPYRIGHT_HOLDER="snoups"
INPUT_DIR="."

enable_test_mode() {
    echo "🧪 Test mode enabled."
    TMP_TEST_DIR="tmp_test"
    MAIN_TRANSLATIONS_DIR="$TMP_TEST_DIR/main_project/locales"
    BACKUP_TRANSLATIONS_DIR="$TMP_TEST_DIR/backup_project/locales"
}

test_init() {
    enable_test_mode
    echo "🔨 Creating mock structure..."
    mkdir -p "$MAIN_TRANSLATIONS_DIR/ru/LC_MESSAGES" "$BACKUP_TRANSLATIONS_DIR/ru/LC_MESSAGES"

    cat > "$MAIN_TRANSLATIONS_DIR/ru/LC_MESSAGES/bot.po" <<EOF
msgid ""
msgstr ""
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=utf-8\n"

msgid "hello"
msgstr "custom hello"

msgid "unused_key"
msgstr "unused key"
EOF

    cat > "$BACKUP_TRANSLATIONS_DIR/ru/LC_MESSAGES/bot.po" <<EOF
msgid ""
msgstr ""
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=utf-8\n"

msgid "hello"
msgstr "original hello"

msgid "bye"
msgstr "original bye"
EOF
    echo "✅ Test project created."
}

merge_translations() {
    echo "🔄 Updating translations..."
    languages=$(find "$BACKUP_TRANSLATIONS_DIR" -mindepth 1 -maxdepth 1 -type d -exec basename {} \;)
    for lang in $languages; do
        main_po="$MAIN_TRANSLATIONS_DIR/$lang/LC_MESSAGES/bot.po"
        backup_po="$BACKUP_TRANSLATIONS_DIR/$lang/LC_MESSAGES/bot.po"

        echo "🔄 Updating: $lang"
        if [[ -f "$backup_po" ]]; then
            mkdir -p "$(dirname "$main_po")"
            if [[ -f "$main_po" ]]; then
                temp_po=$(mktemp)
                cp "$backup_po" "$temp_po"
                msgmerge --no-fuzzy-matching --backup=none --update "$temp_po" "$main_po"
                cp "$temp_po" "$main_po"
                rm "$temp_po"
            else
                cp "$backup_po" "$main_po"
            fi
            msgattrib --no-obsolete "$main_po" -o "$main_po"
            echo "✅ $lang updated."
        else
            echo "⚠️ Skipping: $backup_po not found."
        fi
    done
}

extract_messages() {
    echo "📤 Extracting messages..."
    pybabel extract \
        -o "$MESSAGES_POT" \
        -k _:1,1t -k _:1,2 -k __ \
        --copyright-holder="$COPYRIGHT_HOLDER" \
        --project="$PROJECT_NAME" \
        --version="$VERSION" \
        --input-dirs="$INPUT_DIR"
    echo "✅ Messages extracted to $MESSAGES_POT."
}

update_translations() {
    echo "🔄 Updating translations..."
    pybabel update \
        -D "$DOMAIN" \
        -i "$MESSAGES_POT" \
        -d "$LOCALES_DIR"
    echo "✅ Translations updated in $LOCALE_DIR."
}

compile_translations() {
    echo "⚙️ Compiling..."
    pybabel compile -d "$LOCALES_DIR" -D "$PROJECT_NAME"
    echo "✅ Compilation completed."
}

show_help() {
    echo "📖 Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "    --test init     Create test project"
    echo "    --test merge    Update translations in test project"
    echo "    --merge         Update translations in production project"
    echo "    --update        Extract and compile translations"
    echo "    --help          Show help"
}

if [[ $# -eq 0 ]]; then
    echo "❌ Error: no arguments."
    show_help
    exit 1
fi

case "$1" in
    --test)
        case "$2" in
            init)
                test_init
                ;;
            merge)
                enable_test_mode
                merge_translations
                ;;
            *)
                echo "❌ Error: unknown option '$2' for --test."
                show_help
                exit 1
                ;;
        esac
        ;;
    --merge)
        merge_translations
        ;;
    --update)
        extract_messages
        update_translations
        compile_translations
        ;;
    --help)
        show_help
        ;;
    *)
        echo "❌ Unknown option: $1"
        show_help
        exit 1
        ;;
esac
