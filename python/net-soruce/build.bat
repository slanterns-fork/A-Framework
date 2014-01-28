@echo off

python.exe C:\Python27\Scripts\cxfreeze %* D:\A-Framework-Windows\NAT\src\server.py --target-dir=D:\A-Framework-Windows\NAT\bin\server

python.exe C:\Python27\Scripts\cxfreeze %* D:\A-Framework-Windows\NAT\src\client.py --target-dir=D:\A-Framework-Windows\NAT\bin\client

cd D:\A-Framework-Windows\NAT\bin\

del bin.rar

RAR.exe a bin.rar client\*.*

pause