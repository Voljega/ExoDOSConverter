@echo off

set mpos=0

:TOUR-MENU =============================================================

    wbat pal ! cls
    wbat text 4,26 :tour-info

    call w.bat menu 1,2 :tour-menu #%mpos% +1
        set mpos=%?%
        goto %wbat%

:Quick -----------------------------------------------------------------

    wbat cls ! text  2,4 :quick-box ! box OK
    wbat       text 12,4 :quick-pos ! box 20,60 continue
:q3
    wbat cls ! text  2,4 :quick-choice ! box 21,40 continue,back,tour menu
    if errorlevel 3 goto TOUR-MENU
    if errorlevel 2 goto Quick

    wbat cls ! text  2,4 :quick-prompt
    wbat box 19,55 (blue on +brown) "Continue Tour?" ok,back
    if errorlevel 2 goto q3
    goto TOUR-Menu

:Box Layout ------------------------------------------------------------

    wbat cls ! text 2,4 :box-layout ! box 21,49 continue,return
    if errorlevel 2 goto TOUR-MENU

    wbat cls ! text 2,4 :box-example ! text 7,45 (black on +brown) :box-exm
    wbat box 6,4 :box-exm #6
    wbat box 21,35 continue

    wbat cls ! text 2,4 :box-lref ! box 21,52 continue,return
    if errorlevel 2 goto TOUR-MENU

    wbat cls ! text 2,4 :box-other ! box 21,60 return
    goto TOUR-MENU

:Buttons ---------------------------------------------------------------

    wbat cls ! text 2,4 :buttons
    set ?=
:b-rpt
    call w.bat menu 21,62 :button-menu #%?%
    if errorlevel 100 goto TOUR-MENU

    wbat cls ! text 2,4 :buttons-%wbat%
    goto b-rpt

:Input -----------------------------------------------------------------

    wbat cls ! text 2,4 :input  ! box 21,49 continue,return
    if errorlevel 2 goto TOUR-MENU

    wbat cls ! text 2,4 :input-var ! box 21,60 ok
    goto TOUR-MENU

:Checkboxes ------------------------------------------------------------

    wbat cls ! text 2,4 :checkbox
    call w.bat box 16,50 :checkbox-example #3

    wbat cls ! text 2,4 :checkbox-var ! box 21,55 ok
    goto TOUR-MENU

:Radio buttons ---------------------------------------------------------

    wbat cls ! text 2,4 :radio
    call w.bat box 16,50 :radio-example #4

    wbat cls ! text 2,4 :radio-var ! box 21,55 ok
    goto TOUR-MENU

:List box --------------------------------------------------------------

    wbat cls ! text 2,4 :listbox ! box 21,49 continue,return
    if errorlevel 2 goto TOUR-MENU

    wbat cls ! text 2,4 :list-example
:l-again
    dir *.* /b/a-d/one  > %temp%\temp.txt
    call w.bat list 3,60 @%temp%\temp.txt

    wbat box 8,53 "Your selection was:^** %wbat% **" again,continue
    if not errorlevel 2 goto l-again

    wbat cls ! text 2,4 :list-keys ! box 20,65 ok
    if errorlevel 100 goto TOUR-MENU

    wbat cls ! text 2,4 :list-browse ! box 20,55 example,return
    if errorlevel 2 goto TOUR-MENU
    wbat cls ! list @wbat.ini
    goto TOUR-MENU

:Text ------------------------------------------------------------------

    wbat cls ! text 2,4 :text ! box 21,49 continue,return
    if errorlevel 2 goto TOUR-MENU

    wbat cls ! text 2,4 :text-area
    wbat text 8,16 (blue on bright brown) :text-example
    wbat box 21,49 continue,return
    if errorlevel 2 goto TOUR-MENU

    wbat cls ! text 2,4 :text-attrib ! box 21,49 continue,return
    if errorlevel 2 goto TOUR-MENU

    wbat cls ! text 2,4 :text-quick
    wbat text 11,30 (+white on red) " Pls. ignore this message! "
    wbat box 21,55 return
    goto TOUR-MENU

:Fill ------------------------------------------------------------------

    wbat cls ! text 2,4 :fill ! box 8,40 demo,syntax,return
    if errorlevel 3 goto TOUR-MENU
    if not errorlevel 2 goto fill-demo

    wbat cls ! text 2,4 :fill-syntax ! box 22,65 back
    goto fill

:fill-demo
    wbat cls
    wbat fill  3,4 (21,72) (+black on +brown) " "
    wbat fill 1,50 (13,18) (+black on green) " "
    wbat fill  1,6  (25,1) (+white on blue) "э"
    wbat fill  1,78 (25,1) (red on +green) "WBAT*" +1
    wbat fill  5,12 (4,62) (+cyan on red) "Wbat * " +2
    wbat fill 16,12 (4,62) (+cyan on red) "Wbat * "
    wbat fill  7,17 (7,28) (+black on +white) "ед"
    wbat fill 13,32 (9,28) (+magenta on blue) "ю©зы" +2
    wbat fill 18,22 (7,18) (+red on +black)

    wbat box 22,65 back
    goto fill

:Cursor ----------------------------------------------------------------

    wbat cls ! text 2,4 :cursor ! box 21,60 ok
    goto TOUR-MENU

:Screen ----------------------------------------------------------------

    wbat cls ! text 2,4 :screen ! box 21,60 ok
    goto TOUR-MENU

:Palette & Fonts -------------------------------------------------------

    wbat cls ! text 2,4 :palfont ! box 21,60 palette,font,return
    if errorlevel 3 goto TOUR-MENU
    if errorlevel 2 goto Fonts

    wbat cls ! text 2,4 :palette ! box 21,50 PAL.INI,back
    if errorlevel 2 goto Palette
    wbat cls ! text 1,6 (+black on +brown) @pal.ini
    wbat fill 3,7 (17,20) (red on +brown) ! box 16,70 ok
    goto Palette

:Fonts
    wbat cls ! text 2,4 :font ! box 21,60 back
    goto Palette

:Ansi?  ----------------------------------------------------------------

    wbat cls ! ansi?
    if errorlevel 1 wbat text 2,4 :no_ansi ! wbat box 20,60 details,return
    if errorlevel 2 goto TOUR-MENU
    wbat text 2,4 :ansi ! wbat box 21,66 ok
    goto TOUR-MENU

:STDOUT ----------------------------------------------------------------

    wbat cls ! text 2,4 :stdout ! box 21,60 ok
    goto TOUR-MENU

:Errorlevel ------------------------------------------------------------

    wbat cls ! text 2,4 :elevel ! box 21,60 ok
    goto TOUR-MENU

:END
for %%a in (wabt wcb1 wcb2 wrb) do set %%a=
set ?=
wbat cls
