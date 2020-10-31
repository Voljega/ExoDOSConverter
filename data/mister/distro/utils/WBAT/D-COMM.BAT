@echo off

set mpos=0

:COMMAND

    wbat pal ! cls ! text 2,50 (blue on +green) :command-title

    call w.bat box   (+black on +white) :command-menu #%mpos% +1
        rem     keep mpos: bar position = errorlevel
        set mpos=%?%

        goto %wbat%

:Summary  --------------------------------------------------------------

    wbat cls ! text  2,4 :commands ! box 21,65 ok
    goto Command

:WBAT construct --------------------------------------------------------

    wbat cls ! text  2,4 :wbat-batch
:wvars
    call w.bat menu 20,60 :wbat-menu
    if errorlevel 100 goto Command

    wbat cls ! text  2,4 :wbat-%wbat%
    goto wvars

:Multiple command ------------------------------------------------------

    wbat cls ! text  2,4 :multiple ! box 21,65 ok
    goto Command

:Position  -------------------------------------------------------------

    wbat cls ! text  2,4 :position ! box 21,55 dimensions,return
    if errorlevel 2 goto Command
    wbat cls ! text  2,4 :dimensions ! box 21,65 return
    goto Command

:Colors    -------------------------------------------------------------

    wbat cls ! text  2,4 :colors ! box 21,60 expressions
    if errorlevel 2 goto Command
    wbat cls ! text  2,4 :color-expressions ! box 21,60 return
    goto Command

:Layout reference ------------------------------------------------------

    wbat cls ! text  2,4 :layref
:lmenu
    call w.bat menu 22,65 :layref-menu
    if errorlevel 100 goto Command

    wbat cls ! text  2,4 :layref-%wbat%
    goto lmenu

:Bar options  ----------------------------------------------------------

    wbat cls ! text  2,4 :bar-options ! box 21,65 time-out,return
    if errorlevel 2 goto Command
    wbat cls ! text  2,4 :time-out    ! box 21,65 ok
    goto Command

:END
for %%a in (wbat mpos wcb1 wcb2 wrb) do set %%a=
wbat cls
