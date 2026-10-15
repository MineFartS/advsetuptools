@echo off
cls
pushd %~dp0

if "%~1"=="-f" (
    rmdir /s /q "build"
    pip cache purge
)

python.exe -m pip install ^
    --user -vvv . ^
    || exit /B

popd
