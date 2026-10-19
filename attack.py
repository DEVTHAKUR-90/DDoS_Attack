@echo off
setlocal EnableExtensions DisableDelayedExpansion
title Edge Isolation

:: ======================================================================
:: EDGE ISOLATION - manual, on-demand utility.
:: Runs only when you start it. Creates no scheduled task, service,
:: startup entry, watcher or background process, and exits when done.
::
:: PURPOSE  Stop the Edge BROWSER from running in the background and from
::          starting at sign-in. The WebView2 Runtime is never modified.
::
:: APPLY    1. Policy StartupBoostEnabled = 0      (REG_DWORD)
::          2. Policy BackgroundModeEnabled = 0    (REG_DWORD)
::             both in HKLM\SOFTWARE\Policies\Microsoft\Edge, only when
::             the value is not configured yet. A different existing value
::             is treated as managed by someone else and left alone.
::          3. Edge auto-launch entries (MicrosoftEdgeAutoLaunch*) found in
::             the Run keys are switched OFF in StartupApproved, the same
::             switch Task Manager > Startup apps uses. Run values are NOT
::             deleted.
::          Before each change the original state is recorded in
::          HKLM\SOFTWARE\EdgeIsolationTool (and HKCU\Software\...). That is
::          the only thing this tool keeps. Restore uses it.
::
:: NEVER    WebView2 Runtime, msedgewebview2.exe, Edge Update services and
::          scheduled tasks (one shared updater serves Edge AND WebView2),
::          Run values, other policies, unrelated startup items.
::          Edge processes are only closed when you answer Y, and only
::          main Edge browser processes that have no window.
::
:: COMMANDS (none = menu)
::   /apply /status /check /update /restore  [/silent] [/plain]
::   /silent  no prompts, no pauses, plain text      /plain  no colors
::
:: EXIT CODES
::   0 ok / compliant        1 failed, or still not compliant
::   2 winget unavailable    3 WebView2 update or check failed/unverified
::   4 no admin rights       5 invalid usage
::   10 (/check only) a WebView2 update is available
:: ======================================================================

:: ------------------------------ CONFIG --------------------------------
set "P_EDGE=HKLM\SOFTWARE\Policies\Microsoft\Edge"
set "POLICIES=StartupBoostEnabled BackgroundModeEnabled"
set "SVC_ROOT=HKLM\SYSTEM\CurrentControlSet\Services"
set "UPDATE_SVCS=edgeupdate edgeupdatem MicrosoftEdgeElevationService"

set "RUN_U=HKCU\Software\Microsoft\Windows\CurrentVersion\Run"
set "RUN_M=HKLM\Software\Microsoft\Windows\CurrentVersion\Run"
set "RUN_M32=HKLM\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Run"
set "APPR_U=HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run"
set "APPR_M=HKLM\Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run"
set "APPR_M32=HKLM\Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run32"
set "APPR_OFF=030000000000000000000000"

:: Recorded original state (REG_SZ values). HKLM is writable by admins only.
set "ST_M=HKLM\SOFTWARE\EdgeIsolationTool"
set "ST_U=HKCU\Software\EdgeIsolationTool"

set "GUID_EDGE={56EB18F8-B008-4CBD-B6D2-8C97FE7E9062}"
set "GUID_WV2={F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}"
set "WV2_ID=Microsoft.EdgeWebView2Runtime"

set "RC=0"
set "SILENT="
set "PLAIN="
set "ELEV="
set "ACTION="
set "SID_ORIG="
set "MENUMODE="
set "ARGS=%*"
set "ARGS_PS="
set "SELF=%~f0"
set "SELF_PS=%SELF:'=''%"
if defined ARGS set "ARGS_PS=%ARGS:'=''%"
call :reset

:: ----------------------------- ARGUMENTS ------------------------------
:: SHIFT is used instead of FOR: in FOR, the ? in /? is a wildcard and the
:: argument would be dropped silently.
:arg_loop
if "%~1"=="" goto arg_done
call :parse_arg "%~1"
shift
goto arg_loop
:arg_done
call :ui_init

if /I "%ACTION%"=="/?" goto HELP
if /I "%ACTION%"=="/help" goto HELP
if not defined ACTION (
    if defined SILENT goto USAGE
) else (
    set "VALID="
    for %%V in (/apply /status /check /update /restore) do if /I "%ACTION%"=="%%V" set "VALID=1"
    if not defined VALID goto USAGE
)

:: ----------------------- 64-BIT REGISTRY VIEW -------------------------
:: A 32-bit cmd.exe on 64-bit Windows silently redirects HKLM\SOFTWARE to the
:: 32-bit view. Edge would never see the policies, yet read-back would still
:: pass, so the tool would report a success that has no effect.
if defined PROCESSOR_ARCHITEW6432 (
    call :fail "32-bit Command Prompt on 64-bit Windows, registry changes would go to the wrong place"
    call :note "Start this file from the normal 64-bit Command Prompt or by double-clicking it."
    set "RC=1"
    goto END
)

:: ------------------------ ADMINISTRATOR RIGHTS ------------------------
:: /status and /check are read-only and need no elevation.
set "NEEDADMIN=1"
if /I "%ACTION%"=="/status" set "NEEDADMIN="
if /I "%ACTION%"=="/check" set "NEEDADMIN="
if not defined NEEDADMIN goto START
fltmc >nul 2>&1
if not errorlevel 1 goto START
if defined ELEV (
    call :fail "Administrator rights could not be obtained"
    set "RC=4"
    call :wait_key "Press any key to close this window..."
    goto END
)
call :get_sid SID_ORIG
call :info "Administrator rights needed, requesting elevation"
if defined SILENT goto ELEVATE_WAIT
powershell.exe -NoProfile -Command "try { Start-Process -FilePath '%SELF_PS%' -ArgumentList '%ARGS_PS% /elevated /sid:%SID_ORIG%' -Verb RunAs } catch { exit 4 }" >nul 2>&1
set "RC=%errorlevel%"
if not "%RC%"=="0" call :fail "Elevation was cancelled or failed"
if not "%RC%"=="0" call :wait_key "Press any key to close this window..."
goto END

:ELEVATE_WAIT
powershell.exe -NoProfile -Command "try { $p = Start-Process -FilePath '%SELF_PS%' -ArgumentList '%ARGS_PS% /elevated /sid:%SID_ORIG%' -Verb RunAs -Wait -PassThru; exit $p.ExitCode } catch { exit 4 }" >nul 2>&1
set "RC=%errorlevel%"
goto END

:: ------------------------------- START --------------------------------
:START
:: Per-user (HKCU) settings only make sense if the elevated account is the
:: same account that started the tool.
call :get_sid CUR_SID
set "HKCU_OK=1"
if defined SID_ORIG if /I not "%SID_ORIG%"=="%CUR_SID%" set "HKCU_OK="
if not defined ACTION goto MENU
call :act_%ACTION:/=%
if defined ELEV call :wait_key "Press any key to close this window..."
goto END

:: ------------------------------- MENU ---------------------------------
:MENU
set "MENUMODE=1"
call :clear
call :title "Edge Isolation"
call :menu_state
echo.
echo     %C_CY%1%C_R%   Apply Edge isolation
echo     %C_CY%2%C_R%   Check current configuration
echo     %C_CY%3%C_R%   Check for a WebView2 Runtime update
echo     %C_CY%4%C_R%   Update WebView2 Runtime
echo     %C_CY%5%C_R%   Restore settings changed by this tool
echo     %C_CY%6%C_R%   Exit
echo.
choice /c 123456 /n /m "  Select [1-6]: "
set "SEL=%errorlevel%"
if "%SEL%"=="6" goto MENU_EXIT
if "%SEL%"=="1" call :panel act_apply
if "%SEL%"=="2" call :panel act_status
if "%SEL%"=="3" call :panel act_check
if "%SEL%"=="4" call :panel act_update
if "%SEL%"=="5" call :panel act_restore
if %SEL% GEQ 1 if %SEL% LEQ 5 goto MENU

:: choice failed or input was closed: leave instead of redrawing forever
:MENU_EXIT
set "RC=0"
goto END

:USAGE
set "RC=5"
:HELP
echo.
echo   Usage: edge-isolation.bat [/apply ^| /status ^| /check ^| /update ^| /restore] [/silent] [/plain]
echo.
echo     no argument   interactive menu
echo     /status       read-only configuration report, no admin needed
echo     /apply        isolate the Edge browser
echo     /restore      undo what this tool recorded
echo     /check        look for a WebView2 Runtime update, read-only
echo     /update       update the WebView2 Runtime only
echo     /silent       no prompts, no pauses, plain text
echo     /plain        no colors
echo.
echo   Exit codes: 0 ok, 1 failed or not compliant, 2 winget missing,
echo   3 update failed or unverified, 4 no admin rights, 5 bad usage,
echo   10 update available ^(/check^)
goto END

:END
endlocal & exit /b %RC%

:: ======================================================================
:: ACTIONS
:: ======================================================================
:act_apply
call :reset
call :title "Apply Edge isolation"
if defined MENUMODE (
    call :note "Sets two Edge policies and switches off Edge auto-start entries."
    call :note "Update services, tasks and WebView2 are not touched. Restore can undo this."
    echo.
    choice /c YN /n /m "  Proceed? [Y/N] "
    if errorlevel 2 (
        set "NOWAIT=1"
        exit /b 0
    )
)
call :do_apply
exit /b 0

:act_status
call :reset
call :do_status
exit /b 0

:act_check
call :reset
call :title "WebView2 Runtime update check"
call :head "WebView2 Runtime"
call :do_check
exit /b 0

:act_update
call :reset
call :title "Update WebView2 Runtime"
if defined MENUMODE (
    call :note "Updates only the WebView2 Runtime, through winget. The Edge browser is not updated."
    echo.
    choice /c YN /n /m "  Update now? [Y/N] "
    if errorlevel 2 (
        set "NOWAIT=1"
        exit /b 0
    )
)
call :head "WebView2 Runtime"
call :do_update
exit /b 0

:act_restore
call :reset
call :title "Restore settings changed by this tool"
if defined MENUMODE (
    call :note "Puts back only what this tool recorded when it applied isolation."
    echo.
    choice /c YN /n /m "  Restore now? [Y/N] "
    if errorlevel 2 (
        set "NOWAIT=1"
        exit /b 0
    )
)
call :head "Recorded changes"
call :do_restore
exit /b 0

:: ======================================================================
:: APPLY
:: ======================================================================
:do_apply
set "MODE=apply"
call :read_both
call :head "Edge browser policies"
if "%EDGE_V%"=="not found" call :info "Edge browser not found in the registry, settings are applied anyway"
call :inspect_policies
call :head "Startup entries"
call :inspect_startup
call :head "Edge processes"
call :proc_apply
call :info "Edge update services and tasks left unchanged, shared with WebView2"
set /a CHG_RUN=CHG
set /a NC=0
set "QUIET=1"
set "MODE=audit"
call :inspect_policies
call :inspect_startup
set "QUIET="
if %FAILS% GTR 0 (
    call :result fail "Failed operations: %FAILS%, settings not compliant: %NC%"
    call :setrc 1
    exit /b 0
)
if %NC% GTR 0 (
    call :result warn "Settings not compliant: %NC%, see above"
    call :setrc 1
    exit /b 0
)
if %CHG_RUN% GTR 0 (
    call :result ok "Isolation applied and verified, changes made: %CHG_RUN%. Restart Edge if it is open"
) else (
    call :result ok "Already compliant, nothing changed"
)
exit /b 0

:: policy_item <name>   mode apply: set if absent / status, audit: report
:policy_item
call :reg_get "%P_EDGE%" %~1 PV
if not defined PV goto pi_absent
if /I "%RG_T%"=="REG_DWORD" if "%PV%"=="0x0" goto pi_ok
call :warn "%~1 = %PV% of type %RG_T% set by an existing policy, not changed"
set /a NC+=1
exit /b 0

:pi_ok
call :ok "%~1 = 0, policy configured"
exit /b 0

:pi_absent
if /I not "%MODE%"=="apply" goto pi_missing
call :polkey_note
call :st_put "%ST_M%" "Policy.%~1" created
if errorlevel 1 (
    call :fail "%~1 not changed, original state could not be recorded"
    exit /b 0
)
reg add "%P_EDGE%" /v %~1 /t REG_DWORD /d 0 /f >nul 2>&1
call :reg_get "%P_EDGE%" %~1 PV
if /I "%RG_T%"=="REG_DWORD" if "%PV%"=="0x0" (
    call :done "%~1 set to 0"
    exit /b 0
)
call :st_del "%ST_M%" "Policy.%~1"
call :fail "%~1 could not be set"
exit /b 0

:pi_missing
call :warn "%~1 not configured, Edge default applies"
set /a NC+=1
exit /b 0

:inspect_policies
for %%N in (%POLICIES%) do call :policy_item %%N
exit /b 0

:: polkey_note   remember that this tool is about to create the policy key,
:: so Restore may remove it again when it is empty
:polkey_note
reg query "%P_EDGE%" >nul 2>&1
if not errorlevel 1 exit /b 0
call :st_put "%ST_M%" "PolicyKey.Edge" created
exit /b 0

:: Startup entries: Run value MicrosoftEdgeAutoLaunch* is considered
:: compliant when its StartupApproved flag says disabled.
:inspect_startup
set "SU_ANY="
call :scope U "%RUN_U%" "%APPR_U%"
call :scope M "%RUN_M%" "%APPR_M%"
call :scope M32 "%RUN_M32%" "%APPR_M32%"
if not defined SU_ANY call :ok "No Edge auto-launch entry in the Run keys"
exit /b 0

:scope
if /I "%~1"=="U" if not defined HKCU_OK (
    call :skip "Per-user startup entries skipped, elevated account differs from yours"
    exit /b 0
)
set "SCOPE=%~1"
set "SCOPE_APPR=%~3"
call :each_run "%~2" startup_item
exit /b 0

:startup_item
set "SU_ANY=1"
set "SI_N=%~2"
call :reg_get "%SCOPE_APPR%" "%SI_N%" AD
set "SI_ORIG=absent"
if defined AD set "SI_ORIG=%AD%"
call :is_off "%AD%"
if not errorlevel 1 goto si_off
if /I not "%MODE%"=="apply" goto si_on
set "SKEY=%ST_M%"
if /I "%SCOPE%"=="U" set "SKEY=%ST_U%"
call :st_put "%SKEY%" "Appr.%SCOPE%.%SI_N%" "%SI_ORIG%"
if errorlevel 1 (
    call :fail "%SI_N% not changed, original state could not be recorded"
    exit /b 0
)
reg add "%SCOPE_APPR%" /v "%SI_N%" /t REG_BINARY /d %APPR_OFF% /f >nul 2>&1
call :reg_get "%SCOPE_APPR%" "%SI_N%" AD
call :is_off "%AD%"
if not errorlevel 1 (
    call :done "%SI_N% switched off in Startup settings"
    exit /b 0
)
call :st_del "%SKEY%" "Appr.%SCOPE%.%SI_N%"
call :fail "%SI_N% could not be switched off"
exit /b 0

:si_off
call :ok "%SI_N% is disabled in Startup settings"
exit /b 0

:si_on
call :warn "%SI_N% starts at sign-in"
set /a NC+=1
exit /b 0

:: ----- Edge browser processes (main browser processes only) -----
:: edge_procs sets EP_OK, EP_TOTAL, EP_ROOT, EP_WIN, EP_BG, EP_WV2.
:: A process counts as Edge browser only when its executable is
:: ...\Microsoft\Edge\Application\msedge.exe. WebView2 uses
:: msedgewebview2.exe from a different folder and is only counted.
:edge_procs
set "EP_OK="
set "EP_TOTAL=0"
set "EP_ROOT=0"
set "EP_WIN=0"
set "EP_WV2=0"
for /f "usebackq tokens=1,2,3,4 delims=|" %%A in (`powershell.exe -NoProfile -NonInteractive -Command "$a=@(Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'msedge.exe' -and $_.ExecutablePath -like '*\Microsoft\Edge\Application\msedge.exe' }); $r=@($a | Where-Object { $_.CommandLine -notlike '*--type=*' }); $w=@($r | Where-Object { (Get-Process -Id $_.ProcessId -ErrorAction SilentlyContinue).MainWindowHandle -ne 0 }); $v=@(Get-Process -Name msedgewebview2 -ErrorAction SilentlyContinue); '' + $a.Count + '|' + $r.Count + '|' + $w.Count + '|' + $v.Count" 2^>nul`) do (
    set "EP_TOTAL=%%A"
    set "EP_ROOT=%%B"
    set "EP_WIN=%%C"
    set "EP_WV2=%%D"
    set "EP_OK=1"
)
set /a EP_BG=EP_ROOT-EP_WIN
exit /b 0

:: close_edge_bg   ends main Edge browser processes that have NO window,
:: together with their own child processes. Windowed Edge is never touched.
:close_edge_bg
powershell.exe -NoProfile -NonInteractive -Command "$a=@(Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'msedge.exe' -and $_.ExecutablePath -like '*\Microsoft\Edge\Application\msedge.exe' -and $_.CommandLine -notlike '*--type=*' }); foreach ($p in $a) { $g=Get-Process -Id $p.ProcessId -ErrorAction SilentlyContinue; if ($g -and $g.MainWindowHandle -eq 0) { $i=[string]$p.ProcessId; & taskkill.exe /PID $i /T /F | Out-Null } }" >nul 2>&1
exit /b 0

:proc_report
call :edge_procs
if not defined EP_OK (
    call :info "Edge processes: unavailable, PowerShell could not be queried"
    set /a UNV+=1
    exit /b 0
)
if %EP_TOTAL% EQU 0 (
    call :ok "No Edge browser process is running"
) else (
    call :info "Edge browser processes: %EP_TOTAL% total, %EP_WIN% with a window, %EP_BG% in background"
)
call :info "WebView2 processes: %EP_WV2%, not Edge browser, never touched"
exit /b 0

:proc_apply
call :edge_procs
if not defined EP_OK (
    call :skip "Edge process check unavailable, restart Edge to apply the policies"
    exit /b 0
)
if %EP_TOTAL% EQU 0 (
    call :ok "No Edge browser process is running"
    exit /b 0
)
if %EP_WIN% GTR 0 call :info "Edge has open windows, left running, policies apply after Edge restarts"
if %EP_BG% LEQ 0 exit /b 0
if defined SILENT (
    call :info "Background Edge processes: %EP_BG%, they end when Edge restarts or you sign out"
    exit /b 0
)
echo.
choice /c YN /n /m "    Close background Edge processes now? [Y/N] "
if errorlevel 2 (
    call :info "Left running, they end when Edge restarts or you sign out"
    exit /b 0
)
call :close_edge_bg
call :edge_procs
if %EP_BG% LEQ 0 (
    call :ok "Background Edge processes closed"
) else (
    call :warn "Background Edge processes still running: %EP_BG%"
)
exit /b 0

:: ======================================================================
:: STATUS  (read-only)
:: ======================================================================
:do_status
set "MODE=status"
call :title "Edge isolation status"
call :head "Edge browser policies"
call :inspect_policies
call :head "Startup entries"
call :inspect_startup
call :head "Edge processes"
call :proc_report
call :head "Shared update components, not modified by this tool"
call :infra_report
call :head "WebView2 Runtime, preserved"
call :wv2_report
if %NC% EQU 0 (
    call :result ok "Compliant: Edge browser isolation is in place"
) else (
    call :result warn "Items not compliant: %NC%, run Apply"
    call :setrc 1
)
exit /b 0

:infra_report
for %%S in (%UPDATE_SVCS%) do call :svc_info %%S
set "TK="
for /f "usebackq tokens=1,3 delims=," %%A in (`schtasks /query /fo csv /nh 2^>nul ^| find /I "MicrosoftEdgeUpdate"`) do call :task_line "%%~A" "%%~B"
if not defined TK call :info "No Edge Update scheduled task found"
exit /b 0

:svc_info
call :read_start %~1
if not defined ST (
    call :info "%~1: not installed"
    exit /b 0
)
call :start_name %ST%
set "RUNSTATE=stopped"
sc query %~1 2>nul | find "RUNNING" >nul
if not errorlevel 1 set "RUNSTATE=running"
if "%ST%"=="0x4" (
    call :warn "%~1: Disabled, not by this tool, Edge and WebView2 servicing may be affected"
) else (
    call :info "%~1: %SNAME%, %RUNSTATE%, left unchanged"
)
exit /b 0

:task_line
set "TK=1"
if /I "%~2"=="Disabled" (
    call :warn "Task %~1: Disabled, not by this tool, Edge and WebView2 servicing may be affected"
) else (
    call :info "Task %~1: %~2, left unchanged"
)
exit /b 0

:wv2_report
call :read_both
if "%WV2_V%"=="not found" (
    call :warn "WebView2 Runtime not found in the registry"
    set /a UNV+=1
) else (
    call :ok "WebView2 Runtime %WV2_V% installed, never changed by this tool"
)
call :info "Edge browser version: %EDGE_V%"
exit /b 0

:: ======================================================================
:: RESTORE  (uses only the state recorded by Apply)
:: ======================================================================
:do_restore
set "RS_ANY="
call :restore_hive "%ST_M%"
if defined HKCU_OK (
    call :restore_hive "%ST_U%"
) else (
    call :skip "Per-user records skipped, elevated account differs from yours"
)
if not defined RS_ANY call :info "Nothing recorded, this tool has no change to undo"
call :info "Changes made by older versions of this tool were never recorded and are not touched"
if %FAILS% GTR 0 call :setrc 1
exit /b 0

:restore_hive
for /f "tokens=1,3" %%N in ('reg query "%~1" 2^>nul ^| find "REG_SZ"') do call :restore_one "%~1" "%%N" "%%O"
call :restore_polkey "%~1"
call :st_cleanup "%~1"
exit /b 0

:: restore_polkey <state key>   runs after the values are restored
:restore_polkey
call :reg_get "%~1" "PolicyKey.Edge" PK
if not defined PK exit /b 0
call :key_empty "%P_EDGE%"
if errorlevel 1 goto rk_clear
reg delete "%P_EDGE%" /f >nul 2>&1
call :key_empty "%P_EDGE%"
if not errorlevel 1 (
    call :fail "Edge policy key could not be removed"
    exit /b 0
)
call :done "Edge policy key removed, this tool created it and it is empty"
:rk_clear
call :st_del "%~1" "PolicyKey.Edge"
exit /b 0

:: key_empty <key>   0 only when the key exists and holds no values or subkeys
:key_empty
reg query "%~1" >nul 2>&1
if errorlevel 1 exit /b 1
set /a KE=0
for /f "delims=" %%L in ('reg query "%~1" 2^>nul') do set /a KE+=1
if %KE% LEQ 1 exit /b 0
exit /b 1

:restore_one
set "RS_ANY=1"
set "R_KIND="
for /f "tokens=1,2,* delims=." %%a in ("%~2") do (
    set "R_KIND=%%a"
    set "R_P2=%%b"
    set "R_P3=%%c"
)
if /I "%R_KIND%"=="Policy" call :restore_policy "%R_P2%" "%~1"
if /I "%R_KIND%"=="Appr" call :restore_appr "%R_P2%" "%R_P3%" "%~1" "%~3"
exit /b 0

:: restore_policy <name> <state key>
:restore_policy
call :reg_get "%P_EDGE%" %~1 PV
if not defined PV goto rp_gone
if not "%PV%"=="0x0" goto rp_changed
reg delete "%P_EDGE%" /v %~1 /f >nul 2>&1
call :reg_get "%P_EDGE%" %~1 PV
if defined PV (
    call :fail "%~1 could not be removed"
    exit /b 0
)
call :done "%~1 removed, policy back to not configured"
goto rp_clear
:rp_gone
call :info "%~1 was already removed"
goto rp_clear
:rp_changed
call :skip "%~1 is now %PV%, changed after this tool set it, left as is"
:rp_clear
call :st_del "%~2" "Policy.%~1"
exit /b 0

:: restore_appr <scope> <name> <state key> <original data or absent>
:restore_appr
set "RA_KEY=%APPR_M%"
if /I "%~1"=="U" set "RA_KEY=%APPR_U%"
if /I "%~1"=="M32" set "RA_KEY=%APPR_M32%"
call :reg_get "%RA_KEY%" "%~2" AD
if not defined AD goto ra_gone
if /I not "%AD%"=="%APPR_OFF%" goto ra_changed
if /I "%~4"=="absent" (
    reg delete "%RA_KEY%" /v "%~2" /f >nul 2>&1
) else (
    reg add "%RA_KEY%" /v "%~2" /t REG_BINARY /d %~4 /f >nul 2>&1
)
call :reg_get "%RA_KEY%" "%~2" AD
set "RA_OK="
if /I "%~4"=="absent" (
    if not defined AD set "RA_OK=1"
) else (
    if /I "%AD%"=="%~4" set "RA_OK=1"
)
if not defined RA_OK (
    call :fail "%~2 could not be restored"
    exit /b 0
)
call :done "%~2 restored to its original Startup setting"
goto ra_clear
:ra_gone
call :info "%~2 Startup record no longer exists"
goto ra_clear
:ra_changed
call :skip "%~2 was changed after this tool disabled it, left as is"
:ra_clear
call :st_del "%~3" "Appr.%~1.%~2"
exit /b 0

:: ======================================================================
:: WEBVIEW2 UPDATE (winget). The Edge browser is never updated here.
:: ======================================================================
:do_check
call :need_winget
if errorlevel 1 exit /b 0
call :read_both
if "%WV2_V%"=="not found" (
    call :skip "WebView2 Runtime is not installed, nothing to check"
    exit /b 0
)
call :wg_exec "upgrade --source winget --accept-source-agreements"
if defined WG_HIT (
    call :warn "WebView2 Runtime update available, installed %WV2_V%, use Update"
    call :setrc 10
    exit /b 0
)
if not defined WG_EC set "WG_EC=unknown"
call :in_list "%WG_EC%" "0 -1978335212 -1978335189"
if errorlevel 1 (
    call :warn "Update status could not be determined, winget code %WG_EC%"
    call :setrc 3
) else (
    call :ok "No WebView2 Runtime update listed, installed %WV2_V%"
)
exit /b 0

:do_update
call :need_winget
if errorlevel 1 exit /b 0
call :read_both
if "%WV2_V%"=="not found" (
    call :skip "WebView2 Runtime is not installed, nothing to update"
    exit /b 0
)
set "WV2_B=%WV2_V%"
call :info "Updating WebView2 Runtime %WV2_B% with winget"
call :wg_exec "upgrade --id %WV2_ID% --exact --source winget --silent --accept-source-agreements --accept-package-agreements"
call :read_both
if not defined WG_EC (
    call :fail "winget did not report a result"
    call :setrc 3
    exit /b 0
)
call :in_list "%WG_EC%" "0 -1978334967 -1978334966"
if not errorlevel 1 goto up_success
call :in_list "%WG_EC%" "-1978335189 -1978335153"
if not errorlevel 1 goto up_current
if "%WG_EC%"=="-1978335212" (
    call :fail "winget does not list WebView2 Runtime as installed, update it another way"
    call :setrc 3
    exit /b 0
)
if "%WG_EC%"=="-1978335090" (
    call :fail "winget cannot upgrade in place, install technology differs, reinstall manually"
    call :setrc 3
    exit /b 0
)
call :fail "winget failed, code %WG_EC%, run: winget upgrade --id %WV2_ID%"
call :setrc 3
exit /b 0

:up_success
if "%WG_EC%"=="-1978334967" call :info "winget says a restart is needed to finish"
if "%WG_EC%"=="-1978334966" call :info "winget says a restart is needed to finish"
if /I "%WV2_V%"=="%WV2_B%" (
    call :warn "winget reported success but the version is unchanged, %WV2_V%, not verified"
    call :setrc 3
    exit /b 0
)
call :ok "WebView2 Runtime updated %WV2_B% to %WV2_V%, verified in registry"
set /a NC=0
set "QUIET=1"
set "MODE=audit"
call :inspect_policies
call :inspect_startup
set "QUIET="
if %NC% EQU 0 (
    call :info "Edge isolation unaffected, no need to run Apply again"
) else (
    call :warn "Isolation not fully in place: %NC% items, run Apply"
)
exit /b 0

:up_current
if /I "%WV2_V%"=="%WV2_B%" (
    call :ok "WebView2 Runtime is up to date, %WV2_V%"
) else (
    call :ok "WebView2 Runtime now %WV2_V%, was %WV2_B%"
)
exit /b 0

:need_winget
winget --version >nul 2>&1
if not errorlevel 1 exit /b 0
call :fail "winget not found or not working, install App Installer from the Microsoft Store"
call :setrc 2
exit /b 1

:: wg_exec "<winget arguments>"   sets WG_EC (exit code) and WG_HIT (a line
:: mentioning WebView2 was listed). Raw winget output is not shown.
:wg_exec
set "WG_EC="
set "WG_HIT="
for /f "delims=" %%L in ('cmd /v:on /c "winget %~1 2>&1 & echo EC:!errorlevel!" ^| findstr /I /C:"EdgeWebView2" /C:"EC:"') do call :wg_line "%%L"
exit /b 0

:wg_line
set "WL=%~1"
if /I "%WL:~0,3%"=="EC:" (
    call :wg_ec "%WL:~3%"
) else (
    set "WG_HIT=1"
)
exit /b 0

:: wg_ec "<text after EC:>"   first word only, so stray spaces cannot matter
:wg_ec
for /f "tokens=1" %%E in ("%~1") do set "WG_EC=%%E"
exit /b 0

:: in_list <value> "<space separated list>"   returns 0 when found
:in_list
set "IL_V=%~1"
for %%X in (%~2) do if "%%X"=="%IL_V%" exit /b 0
exit /b 1

:: ======================================================================
:: SHARED HELPERS
:: ======================================================================
:reset
set /a CHG=0
set /a FAILS=0
set /a NC=0
set /a UNV=0
set "RC=0"
set "QUIET="
set "MODE="
exit /b 0

:parse_arg
set "A=%~1"
if /I "%A%"=="/silent" (
    set "SILENT=1"
) else if /I "%A%"=="/plain" (
    set "PLAIN=1"
) else if /I "%A%"=="/elevated" (
    set "ELEV=1"
) else if /I "%A:~0,5%"=="/sid:" (
    set "SID_ORIG=%A:~5%"
) else (
    set "ACTION=%A%"
)
exit /b 0

:setrc
if "%RC%"=="0" set "RC=%~1"
exit /b 0

:: get_sid <variable>   SID of the current account, empty if unavailable
:get_sid
set "%~1="
for /f "tokens=2 delims=," %%S in ('whoami /user /fo csv /nh 2^>nul') do set "%~1=%%~S"
exit /b 0

:: reg_get <key> <value name> <out variable>   data in the variable, type in RG_T
:reg_get
set "%~3="
set "RG_T="
for /f "tokens=2,3" %%A in ('reg query "%~1" /v "%~2" 2^>nul ^| find /I "%~2"') do (
    set "RG_T=%%A"
    set "%~3=%%B"
)
exit /b 0

:: each_run <Run key> <handler>   calls :handler "<key>" "<name>"
:each_run
for /f "tokens=1" %%N in ('reg query "%~1" 2^>nul ^| find /I "MicrosoftEdgeAutoLaunch"') do call :%~2 "%~1" "%%N"
exit /b 0

:: is_off <hex data>   0 when the StartupApproved flag says disabled (03/07)
:is_off
set "D=%~1"
if not defined D exit /b 1
if "%D:~0,2%"=="03" exit /b 0
if "%D:~0,2%"=="07" exit /b 0
exit /b 1

:: recorded state: st_put <key> <name> <data> / st_del <key> <name>
:st_put
reg add "%~1" /v "%~2" /t REG_SZ /d "%~3" /f >nul 2>&1
exit /b %errorlevel%

:st_del
reg delete "%~1" /v "%~2" /f >nul 2>&1
exit /b 0

:: st_cleanup <key>   removes the state key once it holds no values
:st_cleanup
reg query "%~1" >nul 2>&1
if errorlevel 1 exit /b 0
reg query "%~1" 2>nul | find "REG_SZ" >nul
if not errorlevel 1 exit /b 0
reg delete "%~1" /f >nul 2>&1
exit /b 0

:read_start
call :reg_get "%SVC_ROOT%\%~1" Start ST
exit /b 0

:start_name
set "SNAME=code %~1"
if "%~1"=="0x2" set "SNAME=Automatic"
if "%~1"=="0x3" set "SNAME=Manual"
if "%~1"=="0x4" set "SNAME=Disabled"
exit /b 0

:: read_both   EDGE_V and WV2_V from the Edge Update registration
:read_both
call :read_ver EDGE_V %GUID_EDGE%
call :read_ver WV2_V %GUID_WV2%
if not defined EDGE_V set "EDGE_V=not found"
if not defined WV2_V set "WV2_V=not found"
exit /b 0

:read_ver
set "%~1="
call :ver_try %~1 "HKLM\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\%~2"
if not defined %~1 call :ver_try %~1 "HKLM\SOFTWARE\Microsoft\EdgeUpdate\Clients\%~2"
if not defined %~1 call :ver_try %~1 "HKCU\SOFTWARE\Microsoft\EdgeUpdate\Clients\%~2"
exit /b 0

:ver_try
call :reg_get %2 pv PV_TMP
if not defined PV_TMP exit /b 0
if "%PV_TMP%"=="0.0.0.0" exit /b 0
set "%~1=%PV_TMP%"
exit /b 0

:: ----------------------------- CONSOLE UI -----------------------------
:: Colors are cosmetic only: no command, result or exit code depends on
:: them. Plain text is used for /silent, /plain and when NO_COLOR is set.
:: When redirecting output to a file, add /plain.
:ui_init
set "ESC="
set "C_CY="
set "C_W="
set "C_GN="
set "C_YL="
set "C_RD="
set "C_GY="
set "C_R="
if defined SILENT exit /b 0
if defined PLAIN exit /b 0
if defined NO_COLOR exit /b 0
set "OSV="
set "OSB="
for /f "delims=" %%V in ('ver') do set "OSV=%%V"
if not defined OSV exit /b 0
set "OSV=%OSV:[= %"
set "OSV=%OSV:]= %"
for %%T in (%OSV%) do call :ui_build "%%~T"
if not defined OSB exit /b 0
if %OSB% LSS 18362 exit /b 0
for /f %%E in ('echo prompt $E ^| cmd') do set "ESC=%%E"
if not defined ESC exit /b 0
set "C_CY=%ESC%[96m"
set "C_W=%ESC%[97m"
set "C_GN=%ESC%[92m"
set "C_YL=%ESC%[93m"
set "C_RD=%ESC%[91m"
set "C_GY=%ESC%[90m"
set "C_R=%ESC%[0m"
exit /b 0

:ui_build
for /f "tokens=1-3 delims=." %%a in ("%~1") do if "%%a.%%b"=="10.0" set "OSB=%%c"
exit /b 0

:: panel <action label>   one screen per action in menu mode
:panel
set "NOWAIT="
call :clear
call :%~1
if /I not "%~1"=="act_status" if /I not "%~1"=="act_check" set "STATE_DIRTY=1"
if not defined NOWAIT call :wait_key "Press any key to return to the menu..."
exit /b 0

:: clear   clears the screen once per screen change, only in the interactive menu
:clear
if not defined MENUMODE exit /b 0
if defined PLAIN exit /b 0
cls
exit /b 0

:: wait_key "<text>"   the only pause: lets you read a result screen
:wait_key
if defined SILENT exit /b 0
echo.
<nul set /p "=  %C_GY%%~1%C_R%"
pause >nul
echo.
exit /b 0

:: menu_state   one line from a quick registry-only check, no PowerShell
:menu_state
if defined STATE_TXT if not defined STATE_DIRTY goto ms_show
set /a NC=0
set "QUIET=1"
set "MODE=audit"
call :inspect_policies
call :inspect_startup
set "QUIET="
set "STATE_DIRTY="
if %NC% EQU 0 (
    set "STATE_TXT=%C_GN%applied%C_R%"
) else (
    set "STATE_TXT=%C_YL%not fully applied, items: %NC%%C_R%"
)
:ms_show
echo   %C_GY%Isolation:%C_R%  %STATE_TXT%
exit /b 0

:title
if defined SILENT exit /b 0
if defined QUIET exit /b 0
echo.
echo   %C_CY%%~1%C_R%
echo   %C_GY%--------------------------------------------------------%C_R%
exit /b 0

:head
if defined SILENT exit /b 0
if defined QUIET exit /b 0
echo.
echo   %C_CY%%~1%C_R%
exit /b 0

:note
if defined SILENT exit /b 0
if not defined QUIET echo   %C_GY%%~1%C_R%
exit /b 0

:: result <ok|warn|fail> "<text>"   closing line of a screen, set apart by a blank line
:result
if defined QUIET exit /b 0
set "RCOL=%C_GN%"
if /I "%~1"=="warn" set "RCOL=%C_YL%"
if /I "%~1"=="fail" set "RCOL=%C_RD%"
if not defined SILENT echo.
echo   %RCOL%%~2%C_R%
exit /b 0

:ok
if not defined QUIET echo     %C_GN%[ ok ]%C_R% %C_W%%~1%C_R%
exit /b 0

:done
set /a CHG+=1
if not defined QUIET echo     %C_GN%[done]%C_R% %C_W%%~1%C_R%
exit /b 0

:skip
if not defined QUIET echo     %C_YL%[skip]%C_R% %C_W%%~1%C_R%
exit /b 0

:warn
if not defined QUIET echo     %C_YL%[warn]%C_R% %C_W%%~1%C_R%
exit /b 0

:fail
set /a FAILS+=1
if not defined QUIET echo     %C_RD%[FAIL]%C_R% %C_W%%~1%C_R%
exit /b 0

:info
if not defined QUIET echo     %C_GY%[info]%C_R% %C_GY%%~1%C_R%
exit /b 0
