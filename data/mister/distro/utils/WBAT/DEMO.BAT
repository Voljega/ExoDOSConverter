@echo off
        rem     enough environmental space (100 bytes)?
    call echeck.bat xxxxx

        rem     load palette, font
    wbat pal ! font ! cls ! fill 7,4 (16,74) (black on +brown)

        rem     start box using default source file: DEMO.TXT
        set Wtexthi=blue on +brown
    wbat text 2,4 :start ! text 24,4 :copyright
        set Wtexthi=
    wbat box 20,56 start,cancel
        if errorlevel 2 goto exit

        rem     zpos controls current bar position in main menu
        set zpos=

:main menu =============================================================

    wbat cls (+black on +brown) ! text 24,4 :copyright
    call w.bat box 5 :main #%zpos% +1
        rem     keep mpos: bar position=errorlevel
        set zpos=%?%

        goto %wbat%

:Tour
    call D-TOUR.BAT
    goto main

:Setup
    call D-SETUP.BAT
    goto main

:Layouts
    call D-LAYOUT.BAT
    goto main

:Commands
    call D-COMM.BAT
    goto main

:Control
    call D-CONTRL.BAT
    goto main

:Handling
    call D-HANDLE.BAT
    goto main

:exit
for %%a in (wbat zpos) do set %%a=
set ?=
wbat cls ! box "Reset font and palette?" yes,no
if not errorlevel 2 mode co80
cls
:end
