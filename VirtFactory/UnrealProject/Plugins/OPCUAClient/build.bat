@echo off
REM Build script for OPC-UA Client Plugin (Windows)

echo Building OPC-UA Client Plugin...

set PLUGIN_DIR=%~dp0
set BUILD_DIR=%PLUGIN_DIR%Build

REM Create build directory
if not exist "%BUILD_DIR%" mkdir "%BUILD_DIR%"
cd /d "%BUILD_DIR%"

REM Configure with CMake
echo Configuring with CMake...
cmake .. -G "Visual Studio 17 2022"

REM Build
echo Building...
cmake --build . --config Release

echo Build complete!
echo Plugin library is in: %BUILD_DIR%

pause
