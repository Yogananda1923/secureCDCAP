#!/usr/bin/env bash
echo "========================================================"
echo " SecureCompilerAI: Starting Frontend Server (Vite React)"
echo " URL: http://localhost:5173"
echo "========================================================"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/frontend"
npm run dev

