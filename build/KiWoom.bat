@echo off
cd /d "%~dp0"
if exist "KiWoom.exe" (
    start "" "KiWoom.exe"
) else (
    echo Run from dist\KiWoom after pyinstaller build.
    pause
)
