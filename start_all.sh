#!/usr/bin/env bash
echo "========================================================"
echo " SecureCompilerAI: Launching Full-Stack Platform"
echo " Backend:  http://127.0.0.1:8000"
echo " Docs:     http://127.0.0.1:8000/docs"
echo " Frontend: http://localhost:5173"
echo "========================================================"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Start backend in background
bash "$SCRIPT_DIR/start_backend.sh" &
BACKEND_PID=$!

sleep 3

# Start frontend in background
bash "$SCRIPT_DIR/start_frontend.sh" &
FRONTEND_PID=$!

echo "SecureCompilerAI started (Backend PID: $BACKEND_PID, Frontend PID: $FRONTEND_PID)."
echo "Press Ctrl+C to terminate both servers."

trap "kill $BACKEND_PID $FRONTEND_PID; exit" SIGINT SIGTERM
wait

