@echo off
setlocal
rem Build beside the source, regardless of the caller's working directory.
g++ -std=c++17 -Wall -Wextra -Wpedantic "%~dp0paxos.cpp" -o "%~dp0paxos.exe"
if errorlevel 1 exit /b %errorlevel%
echo Built: %~dp0paxos.exe
exit /b 0
