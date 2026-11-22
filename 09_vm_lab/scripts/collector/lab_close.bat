@echo off
rem Lab-only. Run in the guest AFTER lab_prep.bat. Step 1 records what is running, step 2 closes the user apps.
rem python is deliberately NOT closed: if a loader is running we want to record it, not kill it.
set P=C:\lab_pre
mkdir %P% 2>nul
echo [1/2] snapshot before closing anything
tasklist /v /fo csv > %P%\tasklist.csv
wmic process get ProcessId,ParentProcessId,Name,ExecutablePath,CommandLine /format:csv > %P%\procs.csv
netstat -ano > %P%\netstat.txt
ipconfig /displaydns > %P%\dnscache.txt
echo [2/2] closing user apps
powershell -NoProfile -c "Stop-Process -Name Discord,hermes*,firefox,chrome,steam*,EpicGamesLauncher,'LM Studio' -Force -ErrorAction SilentlyContinue"
echo.
echo apps closed. snapshot is in %P%. now leave the VM idle for about 10 minutes, then run collect.bat watch
