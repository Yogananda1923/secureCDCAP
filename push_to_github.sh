#!/usr/bin/env bash
set -e

echo "========================================================"
echo " SecureCompilerAI: Push to GitHub Helper"
echo "========================================================"
echo ""

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

if git remote get-url origin >/dev/null 2>&1; then
    CURRENT_URL=$(git remote get-url origin)
    echo "Current remote origin: $CURRENT_URL"
    read -p "Do you want to push to this remote? (y/n): " CONFIRM
    if [[ "$CONFIRM" =~ ^[Nn] ]]; then
        read -p "Enter new GitHub repository URL: " NEW_URL
        if [ -n "$NEW_URL" ]; then
            git remote set-url origin "$NEW_URL"
            REMOTE_URL="$NEW_URL"
        fi
    else
        REMOTE_URL="$CURRENT_URL"
    fi
else
    echo "No remote repository configured yet."
    echo "Please create a new empty repository on https://github.com/new"
    echo "Example: https://github.com/your-username/SecureCompilerAI.git"
    echo ""
    read -p "Enter your GitHub repository URL: " REMOTE_URL
    if [ -z "$REMOTE_URL" ]; then
        echo "[ERROR] No repository URL provided. Aborting."
        exit 1
    fi
    git remote add origin "$REMOTE_URL"
fi

echo ""
echo "Ensuring all latest files are staged..."
git add .
git commit -m "feat: Synchronize updates and hosting setup" >/dev/null 2>&1 || true

echo ""
echo "Pushing to GitHub (branch: main)..."
git branch -M main
git push -u origin main

echo ""
echo "========================================================"
echo " SUCCESS! Your project is now published on GitHub:"
echo " $REMOTE_URL"
echo "========================================================"
