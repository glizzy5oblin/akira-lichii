@echo off
rem Lab-only. Run this FIRST in an elevated Command Prompt (Run as administrator).
rem Stops Windows background maintenance (defrag/servicing/updates) from writing tens of GB into the overlay.
rem These are changes to the throw-away overlay only; the real disk is never written.
schtasks /change /tn "\Microsoft\Windows\Defrag\ScheduledDefrag" /disable
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Schedule\Maintenance" /v MaintenanceDisabled /t REG_DWORD /d 1 /f
sc config wuauserv start= disabled
sc stop wuauserv
sc config UsoSvc start= disabled
sc stop UsoSvc
sc config TrustedInstaller start= disabled
sc stop TrustedInstaller
sc config WSearch start= disabled
sc stop WSearch
echo prep done
