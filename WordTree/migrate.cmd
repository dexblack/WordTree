@echo off
set THISDIR=%~dp0
set MNG="%THISDIR%env\Scripts\python.exe" manage.py
%MNG% makemigrations
%MNG% migrate
pause
