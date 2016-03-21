@echo off
set THIS=%~p0
set MNG=%THIS%\env\Scripts\python.exe manage.py
if exist db.sqlite3 del db.sqlite3
%MNG% migrate
%MNG% runserver
