@echo off
echo ================================================================
echo   Building A360 to Power Automate Standalone Windows Executable
echo ================================================================
echo.

:: Build React frontend first
echo [1/2] Building Frontend...
cd frontend
call npm run build
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Frontend build failed.
    pause
    exit /b %ERRORLEVEL%
)
cd ..

:: Build Python executable with PyInstaller using safe temp workpath
echo.
echo [2/2] Building Executable with PyInstaller...
python -m PyInstaller --noconfirm --workpath "%TEMP%\a360_migration_build" --distpath "dist" A360_Migration_Analyzer.spec
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] PyInstaller packaging failed.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ================================================================
echo   BUILD COMPLETED SUCCESSFULLY!
echo   Executable generated at: dist\A360_to_PowerAutomate_Migration_Analyzer.exe
echo ================================================================
pause
