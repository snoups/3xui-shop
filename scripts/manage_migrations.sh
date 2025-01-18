#!/bin/bash

ALEMBIC_INI_PATH="app/db/alembic.ini"

echo "Select an action:"
echo "1) Generate migration"
echo "2) Upgrade database"
echo "3) Downgrade database"
read -p "Enter the number of the action: " action

case $action in
    1)
        # Prompt the user for a description of the migration
        read -p "Enter migration description: " description
        # Generate the migration with the provided description
        alembic -c "$ALEMBIC_INI_PATH" revision --autogenerate -m "$description"
        echo "Migration created with description: $description"
        ;;
    2)
        # Apply migrations to upgrade to the latest version
        alembic -c "$ALEMBIC_INI_PATH" upgrade head
        echo "Database upgraded to the latest version."
        ;;
    3)
        # Prompt the user for the downgrade version
        read -p "Enter the version to downgrade to (or use '-1' for the previous revision): " version
        alembic -c "$ALEMBIC_INI_PATH" downgrade $version
        echo "Database downgraded to version: $version"
        ;;
    *)
        echo "Invalid option. Please select 1, 2, or 3."
        ;;
esac
