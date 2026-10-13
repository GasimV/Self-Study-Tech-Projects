@echo off
setlocal
if not "%~1"=="" goto usage
g++ -std=c++17 -Wall -Wextra -Wpedantic "%~dp0hyperloglog_dsa.cpp" -o "%~dp0hyperloglog_dsa.exe"
if errorlevel 1 exit /b %errorlevel%
echo Built: %~dp0hyperloglog_dsa.exe
exit /b 0

:usage
echo Usage: build.cmd 1>&2
exit /b 1
