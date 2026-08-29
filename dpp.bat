@echo off
setlocal
set "PYTHONUTF8=1"
powershell.exe -NoProfile -File "%~dp0dpp.ps1" %*
set "exitCode=%errorlevel%"
endlocal & exit /b %exitCode%