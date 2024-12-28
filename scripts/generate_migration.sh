#!/bin/bash
ALEMBIC_INI_PATH="app/db/alembic.ini"

# Prompt the user for a description of the migration
read -p "Enter migration description: " description

# Generate the migration with the provided description
alembic -c "$ALEMBIC_INI_PATH" revision --autogenerate -m "$description"

# Print a message indicating the migration was created successfully
echo "Migration created with description: $description"

# Apply the migration (upgrade to the latest version)
alembic -c "$ALEMBIC_INI_PATH" upgrade head