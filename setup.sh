#!/bin/bash

# Create top-level files and folders
mkdir -p .vscode
mkdir -p .github/workflows
mkdir -p src
mkdir -p notebooks
mkdir -p tests
mkdir -p scripts

# Create files
touch .vscode/settings.json
touch .github/workflows/unittests.yml
touch .gitignore
touch requirements.txt
touch README.md

touch src/__init__.py

touch notebooks/__init__.py
touch notebooks/README.md

touch tests/__init__.py

touch scripts/__init__.py
touch scripts/README.md

echo "Folder structure created successfully."
