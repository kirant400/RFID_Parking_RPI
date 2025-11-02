@echo off
setlocal enabledelayedexpansion
:: =============================================
:: GATE OPENER: Serial → curl
:: Listens on COM port for "gateopen"
:: Then runs curl to open gate
:: =============================================

:: === CONFIGURE THESE ===
set COM_PORT=COM4
set BAUD=115200
set RPI_IP=10.235.1.188
set USER=admin
set PASS=password
:: =======================

echo.
echo [GATE LISTENER] Starting on %COM_PORT%@%BAUD%...
echo Waiting for "gateopen" to trigger gate...
echo.

:: Configure COM port
mode %COM_PORT%: baud=%BAUD% parity=n data=8 stop=1 to=on >nul

:loop
    :: Read one line from serial (timeout 1 sec)
    set "line="
    for /f "delims=" %%a in ('powershell -command "$port = [System.IO.Ports.SerialPort]::new('%COM_PORT%', %BAUD%); $port.ReadTimeout = 1000; $port.Open(); try { $port.ReadLine() } catch { $port.Close(); exit 1 } finally { $port.Close() }"') do set "line=%%a"

    :: Check if we received anything
    if defined line (
        echo [RECEIVED] !line!
        
        :: Exact word match: gateopen
        echo !line! | findstr /i /r "\<gateopen\>" >nul
        if !errorlevel! == 0 (
            echo.
            echo [TRIGGER] "gateopen" DETECTED! Opening gate...
            
            :: Run curl
            curl -u %USER%:%PASS% -X POST -s "http://%RPI_IP%:5000/open_gate" >nul
            if !errorlevel! == 0 (
                echo [SUCCESS] Gate opened via curl!
            ) else (
                echo [ERROR] curl failed. Check IP, network, or Flask app.
            )
            echo.
        )
    )

    :: Prevent 100% CPU
    timeout /t 1 >nul
goto loop