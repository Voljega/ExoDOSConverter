@echo off

set mpos=0

:HANDLING

    wbat pal ! cls ! text 2,50 (blue on +green) :handling-title

    call w.bat box (+black on +white) :handling-menu #%mpos% +1
        set mpos=%?%
        if %wbat%==END goto END

    wbat cls ! text 2,4 :handle-%wbat% ! box 21,60 ok
        goto Handling

:END
for %%a in (mpos wbat) do set %%a=
wbat cls
