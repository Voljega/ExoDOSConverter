@echo off
wbat pal ! fill (black on white) "ед"
set $f=black
set $b=white

:Start
wbat fill  5,6 (16,46) (%$f% on %$b%) " %$f% on %$b% *" +3

call w.bat menu 5,60 @%0:select
if errorlevel 100 goto END
if %wcb1%==1 set wbat=bright %wbat%
if %wrb%==1 set $b=%wbat%
if %wrb%==2 set $f=%wbat%
goto START

:select [x]
Change..
[.] background
[.] foreground

[!] bright

[ black    ]
[ bl&ue     ]
[ green    ]
[ cyan     ]
[ red      ]
[ magenta  ]
[ br&own    ]
[ white    ]
:
:end
for %%a in (wbat wcb1 wrb) do set %%a=
set ?=
wbat cls
