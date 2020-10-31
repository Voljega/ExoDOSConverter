@echo off

set mpos=0

:CONTROL

    wbat pal ! cls ! text 2,50 (blue on +green) :control-title

    call w.bat box (+black on +white) :control-menu #%mpos% +1
        set mpos=%?%
        goto %wbat%

:General  --------------------------------------------------------------

    wbat cls ! text  2,4 :control-general ! box 22,55 ok
    goto Control

:Errorlevels -----------------------------------------------------------

    wbat cls ! text  2,4 :errorlevel ! box 21,65 ok
    goto Control

:Variables  ------------------------------------------------------------

    wbat cls ! text  2,4 :variable

:c-var
    call w.bat menu 20,60 :var-menu
    if errorlevel 100 goto Control

    wbat cls ! text  2,4 :var-%wbat%
    goto c-var

:Handling ESC  ---------------------------------------------------------

    wbat cls ! text  2,4 :ESC-handling ! box 21,65 continue
    wbat cls ! text  2,4 :ESC-handling2 ! box 21,65 ok
    goto Control

:List     --------------------------------------------------------------

    wbat cls ! text  2,4 :list-handling ! box 22,55 continue
    wbat cls ! text  2,4 :list-variable ! box 22,55 ok
    goto Control

:Batch Labels  ---------------------------------------------------------

    wbat cls ! text  2,4 :labels ! box 21,65 continue
    wbat cls ! text  2,4 :label-prefix ! box 21,65 return
    goto Control

:END
for %%a in (mpos wbat wcb1 wcb2 wrb) do set %%a=
wbat cls
