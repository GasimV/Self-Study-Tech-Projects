@echo off
setlocal
rem Build beside the source, regardless of the caller's working directory.
set "paxosTarget=paxos"
if not "%~2"=="" goto usage
if "%~1"=="" goto build
if /I "%~1"=="dsa" (
    set "paxosTarget=paxos_dsa"
    goto build
)
goto usage

:build
g++ -std=c++17 -Wall -Wextra -Wpedantic "%~dp0%paxosTarget%.cpp" -o "%~dp0%paxosTarget%.exe"
if errorlevel 1 exit /b %errorlevel%
echo Built: %~dp0%paxosTarget%.exe
exit /b 0

:usage
echo Usage: build.cmd [dsa] 1>&2
exit /b 1
