@echo off
rem Evidence collector for the lab guest. Writes everything to C:\lab_out. Read-only on the system (no changes except files in lab_out).
rem usage:  collect.bat          volatile + persistence + hashes
rem         collect.bat watch    also records process/connection snapshots every 20 s for ~6 min
rem         collect.bat copy     also copies the Python399 folder into lab_out (can be big)
set O=C:\lab_out
mkdir %O% 2>nul
cd /d %O%
echo started %date% %time% > done.txt

echo [1/6] volatile
tasklist /v /fo csv > tasklist.csv
wmic process get ProcessId,ParentProcessId,Name,ExecutablePath,CommandLine /format:csv > procs.csv
netstat -ano > netstat.txt
ipconfig /displaydns > dnscache.txt
ipconfig /all > ipconfig.txt
powershell -NoProfile -c "Get-NetTCPConnection | Select State,LocalAddress,LocalPort,RemoteAddress,RemotePort,OwningProcess | Export-Csv -NoTypeInformation C:\lab_out\tcp_ps.csv"

echo [2/6] persistence
reg query HKCU\Software\Microsoft\Windows\CurrentVersion\Run > run_hkcu.txt
reg query HKLM\Software\Microsoft\Windows\CurrentVersion\Run > run_hklm.txt
reg query HKCU\Software\Microsoft\Windows\CurrentVersion\RunOnce > runonce_hkcu.txt
reg query "HKLM\Software\Microsoft\Windows NT\CurrentVersion\Winlogon" > winlogon.txt
schtasks /query /fo csv /v > schtasks.csv
sc query type= service state= all > services.txt
dir /a "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup" > startup.txt
dir /a "%ProgramData%\Microsoft\Windows\Start Menu\Programs\Startup" > startup_all.txt

echo [3/6] loader files
dir /a /s "%LOCALAPPDATA%\Programs\Python399" > python399_dir.txt 2>&1
dir /a /s "%LOCALAPPDATA%\Programs" > programs_dir.txt 2>&1
dir /a /o-d /t:w "%TEMP%" > temp_dir.txt 2>&1
dir /a "%APPDATA%" > appdata_dir.txt 2>&1
dir /a "%APPDATA%\Microsoft\Internet Explorer" > ie_dir.txt 2>&1
type "%APPDATA%\t_id.txt" > t_id.txt 2>&1
type "%APPDATA%\Microsoft\Internet Explorer\wd.pid" > wd_pid.txt 2>&1
dir /a /s C:\Windows\Fonts\*.exe > fonts_exe.txt 2>&1
type C:\Windows\System32\drivers\etc\hosts > hosts.txt

echo [4/6] hashes
powershell -NoProfile -c "Get-ChildItem $env:LOCALAPPDATA\Programs\Python399 -Recurse -File -ErrorAction SilentlyContinue | Get-FileHash -ErrorAction SilentlyContinue | Out-File C:\lab_out\python399_hashes.txt -Width 400"

echo [5/6] system and defender
systeminfo > systeminfo.txt
whoami /all > whoami.txt
powershell -NoProfile -c "Get-MpComputerStatus | Format-List * | Out-File C:\lab_out\defender_status.txt"
powershell -NoProfile -c "Get-MpThreatDetection | Format-List * | Out-File C:\lab_out\defender_detections.txt"

if /i "%1"=="watch" goto watch
if /i "%2"=="watch" goto watch
goto after_watch
:watch
echo [watch] 18 rounds x 20 s
for /l %%i in (1,1,18) do (
  tasklist /v /fo csv > p_%%i.csv
  netstat -ano > n_%%i.txt
  timeout /t 20 /nobreak >nul
)
:after_watch

if /i "%1"=="copy" xcopy "%LOCALAPPDATA%\Programs\Python399" %O%\Python399 /e /i /h /y /q
if /i "%2"=="copy" xcopy "%LOCALAPPDATA%\Programs\Python399" %O%\Python399 /e /i /h /y /q

echo [6/6] done
echo finished %date% %time% >> done.txt
echo collection finished. files are in %O%
