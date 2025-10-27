@echo off
echo.
echo ========================================
echo  NFLReadPy Setup
echo ========================================
echo.
echo This will set up nflreadpy for NFL data collection.
echo.
echo nflreadpy is a Python package specifically designed for NFL data.
echo It includes live odds and historical data - no external APIs needed!
echo.
echo What this will do:
echo 1. Check if Python is installed
echo 2. Install nflreadpy package
echo 3. Test the installation
echo.
pause

echo.
echo Checking Python installation...
python --version
if errorlevel 1 (
    echo.
    echo ❌ Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

echo.
echo ✅ Python is installed
echo.
echo Installing nflreadpy...
pip install nflreadpy

if errorlevel 1 (
    echo.
    echo ❌ Failed to install nflreadpy
    echo Please check your internet connection and try again
    pause
    exit /b 1
)

echo.
echo ✅ nflreadpy installed successfully
echo.
echo Testing nflreadpy installation...
python -c "import nflreadpy as nfl; print('✅ nflreadpy is working!')"

if errorlevel 1 (
    echo.
    echo ❌ nflreadpy test failed
    echo Please try reinstalling: pip install nflreadpy
    pause
    exit /b 1
)

echo.
echo ========================================
echo  Setup Complete!
echo ========================================
echo.
echo ✅ nflreadpy is ready to use!
echo.
echo You can now run:
echo - collect-odds-nflreadpy.bat (for live odds)
echo - download-nfl-data-nflreadpy.bat (for historical data)
echo.
pause


