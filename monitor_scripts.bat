@echo off
:loop
echo Checking Python processes...
powershell -Command "Get-Process python -ErrorAction SilentlyContinue | Measure-Object | Select-Object -ExpandProperty Count"
set count=%errorlevel%

if %count%==0 (
    echo No Python processes running. Starting all scripts...
    call start_all_monitoring.bat
    timeout /t 30 /nobreak
) else (
    echo %count% Python processes are running. All good!
)

timeout /t 60 /nobreak
goto loop
