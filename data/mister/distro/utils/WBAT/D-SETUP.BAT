@echo off

set mpos=0

:SETUP

    wbat pal ! cls ! text 2,55 (blue on +green) :setup-title

    call w.bat box (+black on +white) :setup-menu #%mpos% +1
        set mpos=%?%
        goto %wbat%

:Installation ----------------------------------------------------------

    wbat cls ! text  2,4 :install1 ! box 21,60 continue
    wbat cls ! text  2,4 :install2 ! box 20,60 return
    goto SETUP

:INI file --------------------------------------------------------------

    wbat cls ! text  2,4 :inifile
:inire
    call w.bat menu 19,64 :ini-menu
    if errorlevel 100 goto SETUP
    if %wbat%==WBATINI goto inishow
    wbat cls
    wbat text  2,4 :ini-%wbat%
    goto inire
:inishow
    wbat list (black on +brown) @WBAT.INI
    goto inire


:Environment  ----------------------------------------------------------

    wbat cls ! text  2,4 :environment ! box 21,60 ok
    goto SETUP

:Project editing -------------------------------------------------------

    wbat cls ! text  2,4 :project-editing  ! box 20,60 ok
    goto SETUP

:END
for %%a in (mpos wbat wcb1 wcb2 wrb) do set %%a=
wbat cls
