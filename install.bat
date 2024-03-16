@echo off

REM This batch file is used to create a virtual environment and install the required dependencies for the project.

setlocal
pushd %~dp0

set VENV=%TEMP%\dog-poop-detector-yolov5
set PYTHON_VERSION=3.9
set REQUIREMENTS=requirements.txt

REM Create symbolic link for virtual environment folder at '%VENV%-%PYTHON_VERSION%'
if exist "%VENV%-%PYTHON_VERSION%" (
    echo [1mRemoving existing symbolic linked virtual environment folder...[0m
    rd /s /q "%VENV%-%PYTHON_VERSION%"
)

if exist ".venv" (
    echo [1mRemoving existing local virtual environment folder...[0m
    rd /s /q ".venv"
)

echo [1mCreate symbolic link for virtual environment folder at '%VENV%-%PYTHON_VERSION%'...[0m
md "%VENV%-%PYTHON_VERSION%"
mklink /j ".venv" "%VENV%-%PYTHON_VERSION%"
IF %ERRORLEVEL% NEQ 0 GOTO END

REM Creating virtual environment
echo.
echo [1mCreating virtual environment...[0m
py -%PYTHON_VERSION% -m venv .venv
IF %ERRORLEVEL% NEQ 0 GOTO END

REM Activate virtual environment
echo.
echo [1mActivate virtual environment...[0m
call .venv\Scripts\activate

REM Upgrading pip
echo.
echo [1mUpgrading pip...[0m
pip -V
pip install --upgrade pip
pip -V

REM Install dependencies
echo.
echo [1mInstall dependencies...[0m
pip install -r %REQUIREMENTS%
IF %ERRORLEVEL% NEQ 0 GOTO END

:END
echo.
IF %ERRORLEVEL% NEQ 0 (
	echo [101;93mERROR DETECTED. Errorlevel: !EXITCODE![0m
) ELSE (
	echo [104mDone![0m
)

popd
endlocal

pause