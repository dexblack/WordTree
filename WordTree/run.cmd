@echo off
setlocal
set THISDIR=%~dp0
rem echo %THISDIR%
start "RUMenuEditor" "%THISDIR%\env\Scripts\python.exe" manage.py runserver 0.0.0.0:8000
explorer http://127.0.0.1:8000
endlocal
