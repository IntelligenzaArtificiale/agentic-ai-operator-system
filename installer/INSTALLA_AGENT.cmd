@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Install-WinBridge.ps1" -NonInteractive -ResultPath "%~dp0INSTALL_RESULT.json"
exit /b %ERRORLEVEL%
