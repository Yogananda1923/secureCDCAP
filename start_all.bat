@echo off
echo ========================================================
echo  SecureCompilerAI: Launching Full-Stack Local Platform
echo  Backend:  http://127.0.0.1:8000
echo  Docs:     http://127.0.0.1:8000/docs
echo  Frontend: http://localhost:5173
echo ========================================================

start "SecureCompilerAI Backend" cmd /c "%~dp0start_backend.bat"
timeout /t 3 /nobreak >nul
start "SecureCompilerAI Frontend" cmd /c "%~dp0start_frontend.bat"

echo SecureCompilerAI backend and frontend launched in separate terminal windows.
pause

