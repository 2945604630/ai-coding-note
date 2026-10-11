@echo off
cd /d "%~dp0"
python -X utf8 -m web_lab.launch --port 8006 --data-dir data\aic_demo
if errorlevel 1 pause
