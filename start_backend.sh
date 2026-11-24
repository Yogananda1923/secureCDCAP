#!/usr/bin/env bash
echo "========================================================"
echo " SecureCompilerAI: Starting Backend Server (FastAPI)"
echo " Host: http://127.0.0.1:8000"
echo " Docs: http://127.0.0.1:8000/docs"
echo "========================================================"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/backend"
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

