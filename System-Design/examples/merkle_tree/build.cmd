@echo off
setlocal
if not "%~1"=="" goto usage
if not "%1"=="" goto usage
g++ -std=c++17 -Wall -Wextra -Wpedantic "%~dp0merkle_tree_dsa.cpp" -o "%~dp0merkle_tree_dsa.exe"
if errorlevel 1 exit /b %errorlevel%

echo Built: %~dp0merkle_tree_dsa.exe
exit /b 0

:usage
echo Usage: build.cmd 1>&2
exit /b 1
