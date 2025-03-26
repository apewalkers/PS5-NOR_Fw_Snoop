@echo off
SETLOCAL

:: Check for Python version 3.x
python --version >nul 2>&1
IF %ERRORLEVEL% EQU 0 (
    SET PYTHON_CMD=python
) ELSE (
    python3 --version >nul 2>&1
    IF %ERRORLEVEL% EQU 0 (
        SET PYTHON_CMD=python3
    ) ELSE (
        echo Python is not installed. Please install Python 3.x.
        EXIT /B 1
    )
)

:: Run the Python script
%PYTHON_CMD% main.py

:: Wait for the user to press any key before closing
echo.
echo Press any key to exit...
pause >nul

ENDLOCAL
