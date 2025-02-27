#!/bin/bash

# manage_migrations.sh
# ────────────────────────────────────────────────────────────────
# Script for managing database migrations using Alembic.
#
# Options:
#     --generate "Migration description"   Generate a new migration
#     --upgrade                            Upgrade database to the latest version
#     --downgrade VERSION                  Downgrade database to a specific version
#     --help                               Show usage information
# ────────────────────────────────────────────────────────────────

set -e

ALEMBIC_INI_PATH="app/db/alembic.ini"

show_help() {
    echo "Usage:"
    echo "    --generate \"description\"   Generate a new migration with the given description."
    echo "    --upgrade                   Upgrade database to the latest version."
    echo "    --downgrade VERSION         Downgrade database to the specified version."
    echo "    --help                      Show this help message."
}

if [[ $# -eq 0 ]]; then
    echo "❌ Error: No options provided. Use --help for usage information."
    exit 1
fi

case "$1" in
    --generate)
        if [[ -z "$2" ]]; then
            echo "❌ Error: Migration description is required."
            exit 1
        fi
        alembic -c "$ALEMBIC_INI_PATH" revision --autogenerate -m "$2"
        echo "✅ Migration created with description: $2"
        ;;
    --upgrade)
        alembic -c "$ALEMBIC_INI_PATH" upgrade head
        echo "✅ Database upgraded to the latest version."
        ;;
    --downgrade)
        if [[ -z "$2" ]]; then
            echo "❌ Error: Version is required for downgrade."
            exit 1
        fi
        alembic -c "$ALEMBIC_INI_PATH" downgrade "$2"
        echo "✅ Database downgraded to version: $2"
        ;;
    --help)
        show_help
        ;;
    *)
        echo "❌ Error: Unknown option '$1'. Use --help for usage information."
        exit 1
        ;;
esac
