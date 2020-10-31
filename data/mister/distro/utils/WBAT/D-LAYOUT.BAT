@echo off

set mpos=0

:LAYOUT Design

    wbat pal ! cls ! text 2,50 (blue on +green) :layout-title

    call w.bat box (+black on +white) :layout-menu #%mpos% +1
        set mpos=%?%
        goto %wbat%

:General  --------------------------------------------------------------

    wbat cls ! text  2,4 :layout-general ! box 22,65 variables,back
    if errorlevel 2 goto Layout
    wbat cls ! text  2,4 :layout-variables ! box 21,65 ok
    goto Layout

:Box Style  ------------------------------------------------------------

    wbat cls ! text  2,4 :layout-style
:style
    call w.bat menu 20,60 :style-menu
    if errorlevel 100 goto Layout
    wbat cls ! text 2,4 :style-%wbat%
    goto style

:Control Elements ------------------------------------------------------

    wbat cls ! text  2,4 :layout-control
:elem
    call w.bat menu 20,60 :element-menu
    if errorlevel 100 goto Layout
    wbat cls ! text 2,4 :%wbat%
    goto elem

:Text attributes -------------------------------------------------------

    wbat cls ! text  2,4 :layout-text ! box 21,65 attributes, return
    if errorlevel 2 goto Layout
    wbat cls ! text  2,4 :text-attrib ! box 21,65 ok
    goto Layout

:Timer Display ---------------------------------------------------------

    wbat cls ! text  2,4 :layout-timer
    call w.bat box 14,25 :layout-tbox #1,15
    goto Layout


:Symbol summary --------------------------------------------------------

    wbat cls ! text  2,4 :layout-symbols ! box 21,65 ok
    goto Layout

:Color Test ------------------------------------------------------------

    call colors.bat
    goto Layout

:END
for %%a in (mpos wbat wcb1 wcb2 wrb) do set %%a=
wbat cls
