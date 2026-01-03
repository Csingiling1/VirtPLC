@echo off
echo VirtPLC PAC Control Project Setup
echo ==================================

echo.
echo Files created:
echo - virtplc_project.groov (Main PAC Control project)
echo - virtplc_strategy.csv (Strategy export)
echo - variables.txt (Variable definitions)
echo - README.md (Complete setup instructions)
echo.

echo Next steps:
echo 1. Open PAC Control
echo 2. File -^> Open Project
echo 3. Select virtplc_project.groov
echo 4. Build the strategy
echo 5. Download to your Groov PLC
echo.

echo For Ignition Edge setup:
echo - Add Modbus TCP device (PLC_IP:502)
echo - Import tags from the README.md
echo - Create HMI with toggle buttons
echo.

echo For Node-RED setup:
echo - Install node-red-contrib-modbus
echo - Add Modbus client (PLC_IP:502)
echo - Create flows to read/write registers
echo.

pause