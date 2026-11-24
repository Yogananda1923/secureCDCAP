@echo off
setlocal enabledelayedexpansion

echo ========================================================
echo  SecureCompilerAI: Push to GitHub Helper
echo ========================================================
echo.

cd /d "%~dp0"

:: Check if git remote origin is already set
git remote get-url origin >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    for /f "delims=" %%i in ('git remote get-url origin') do set REMOTE_URL=%%i
    echo Current remote origin: !REMOTE_URL!
    echo.
    set /p CONFIRM="Do you want to push to this remote? (Y/N): "
    if /i "!CONFIRM!" neq "Y" (
        set /p NEW_URL="Enter new GitHub repository URL: "
        if not "!NEW_URL!"=="" (
            git remote set-url origin !NEW_URL!
            set REMOTE_URL=!NEW_URL!
        )
    )
) else (
    echo No remote repository configured yet.
    echo Please create a new empty repository on https://github.com/new
    echo Example: https://github.com/your-username/SecureCompilerAI.git
    echo.
    set /p REMOTE_URL="Enter your GitHub repository URL: "
    if "!REMOTE_URL!"=="" (
        echo [ERROR] No repository URL provided. Aborting.
        pause
        exit /b 1
    )
    git remote add origin !REMOTE_URL!
)

echo.
echo Ensuring all latest files are staged...
git add .
git commit -m "feat: Synchronize updates and hosting setup" >nul 2>&1

echo.
echo Pushing to GitHub (branch: main)...
git branch -M main
git push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================================
    echo  SUCCESS! Your project is now published on GitHub:
    echo  !REMOTE_URL!
    echo ========================================================
) else (
    echo.
    echo [NOTE] Push encountered an issue. If your remote repo already has a README/license,
    echo run: git pull origin main --rebase
    echo and then re-run this script.
)

echo.
pause
