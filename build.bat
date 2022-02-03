@echo off

rem Always work from the directory containing this batch file
pushd %~dp0

rem Capture the output from app\version.py into an environment variable for use by Inno Setup
for /f %%i in ('poetry run python app\version.py') do set FSCAN_INSTALLER_VERSION=%%i
echo Attempting to build installer for FScan v%FSCAN_INSTALLER_VERSION%.
echo Remember to increment version number in app\version.py for new releases.

rem Remove leftover intermediate and output files from previous pyinstaller runs
rmdir /s /q build
rmdir /s /q dist

rem Run pyinstaller to build FScan into a single folder containing an EXE
call poetry run pyinstaller --noconfirm main.spec
if not '%errorlevel%'=='0' goto failure

rem Use verpatch to bake the version number into the newly-built EXE
call util\verpatch dist\FScan\FScan.exe %FSCAN_INSTALLER_VERSION% /va /pv %FSCAN_INSTALLER_VERSION% /high
echo Wrote product version %FSCAN_INSTALLER_VERSION% into FScan.exe.

rem Run Inno Setup to build a distributable installer
call util\innosetup\ISCC.exe setup.iss
if not '%errorlevel%'=='0' goto failure

popd
echo Build succeeded.
echo Remember to increment version number in app\version.py for new releases.
exit /b 0

:failure
popd
echo BUILD FAILED.
exit /b 1
