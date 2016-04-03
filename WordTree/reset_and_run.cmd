@echo off
set THISDIR=%~dp0
set MNG="%THISDIR%env\Scripts\python.exe" manage.py
if exist db.sqlite3 del db.sqlite3
%MNG% migrate
%MNG% runserver
pause