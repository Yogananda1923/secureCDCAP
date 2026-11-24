@echo off
echo ========================================================
echo  SecureCompilerAI: Starting Frontend Server (Vite React)
echo  URL: http://localhost:5173
echo ========================================================
cd /d "%~dp0frontend"
npm.cmd run dev
pause

