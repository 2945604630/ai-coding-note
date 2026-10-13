@echo off
cd /d "%~dp0"
python -X utf8 -m web_lab.launch --port 8008 --data-dir output\aic-v3-test
if errorlevel 1 pause
