@echo off
if exist "%~dp0.venv\Scripts\python.exe" (
    "%~dp0.venv\Scripts\python.exe" -m cryptolab %*
) else (
    python -m cryptolab %*
)
