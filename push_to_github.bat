@echo off
setlocal enabledelayedexpansion

echo ========================================================
echo  SecureCompilerAI: Push to GitHub Helper
echo ========================================================
echo.

cd /d "%~dp0"

:: Set remote with explicit username
git remote set-url origin https://Yogananda1923@github.com/Yogananda1923/secureCDCAP.git >nul 2>&1

echo Current target: https://github.com/Yogananda1923/secureCDCAP.git
echo Target GitHub User: Yogananda1923
echo.
echo [1] Push using Browser Login (will clear any conflicting saved credentials)
echo [2] Push using a Personal Access Token (PAT)
echo.
set /p CHOICE="Select an option (1 or 2): "

if "%CHOICE%"=="2" (
    echo.
    echo Generate a token at: https://github.com/settings/tokens (Select 'repo' scope)
    echo.
    set /p TOKEN="Paste your GitHub Token (starts with ghp_): "
    if not "!TOKEN!"=="" (
        git remote set-url origin https://!TOKEN!@github.com/Yogananda1923/secureCDCAP.git
    )
) else (
    echo.
    echo Resetting cached Windows credentials for github.com...
    cmdkey /delete:LegacyGeneric:target=git:https://github.com >nul 2>&1
    cmdkey /delete:git:https://github.com >nul 2>&1
    git remote set-url origin https://Yogananda1923@github.com/Yogananda1923/secureCDCAP.git
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
    echo  https://github.com/Yogananda1923/secureCDCAP
    echo ========================================================
) else (
    echo.
    echo ========================================================
    echo  Push failed. If the error mentions 403 or permission:
    echo  Please run this script again and choose Option [2]
    echo  using a GitHub Personal Access Token (with 'repo' scope).
    echo ========================================================
)

echo.
pause
