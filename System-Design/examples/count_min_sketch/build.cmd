@echo off
setlocal
if not "%~1"=="" goto usage
g++ -std=c++17 -Wall -Wextra -Wpedantic "%~dp0count_min_sketch_dsa.cpp" -o "%~dp0count_min_sketch_dsa.exe"
if errorlevel 1 exit /b %errorlevel%
echo Built: %~dp0count_min_sketch_dsa.exe
exit /b 0

:usage
echo Usage: build.cmd 1>&2
exit /b 1
