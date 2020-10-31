; Print free DOS ram in bytes and KB.
; For utility use, stores amount of free ram in paragraphs in the ICA
; as a word at location 40:F0:
;        40:F0  16bytes  Intra-Applications Communications Area (IBM Technical
;                        Reference incorrectly locates this at 50:F0-50:FF)

; trixter@oldskool.org, with dwtoa routine ideas from Ernst Jan Plug



.8086

        push    es
        mov     ax,40h
        mov     es,ax                   ;es=40:
        mov     ax,ds:word ptr [2]      ;Segment of the first byte beyond the
                                        ;memory allocated to the program (PSP)
        mov     dx,cs
        sub     ax,dx                   ;adjust for our own segment
                                        ;ax = dos free RAM in paragraphs
        mov     word ptr es:[0f0h],ax   ;Store into ICA at 40:f0
        pop     es
        mov     dx,16
        mul     dx                      ;dx:ax = dos free ram in bytes
        mov     di,offset strbuf
        push    ax
        push    dx                      ;save calc'd value for later
        mov     bx,10                   ;radix 10 printing (base 10)
        push    di
        call    dwordtostr
        pop     di                      ;restore string buffer pointer
        mov     dx,di
        mov     ah,09
        int     21h                     ;print string from our string buffer
        mov     dx,offset bfr
        int     21h

; restore original calc'd value to be converted to KB
        pop     dx
        pop     ax
        mov     cx,1024
        div     cx                      ;dx:ax = free DOS RAM in KB
        xor     dx,dx                   ;div result is 16-bit, so 0 this out
        push    di
        call    dwordtostr
        pop     dx
        mov     ah,09
        int     21h
        mov     dx,offset kfr
        int     21h
        ret

dwordtostr:
;Converts a dword into a DOS string.
;Input: DX:AX   dword to be converted.
;       ES:DI   pointer to where the string is stored
;       BL      radix (10 for decimal, 16 for hex, etc., up to 36)
;
;Output: ES:DI points just past the converted string.
;
;Destroys: AX, BH, CX, DX, SI.
        xor     bh, bh                  ;Clear bh so bx=radix
        cld                             ;Direction for stosb
        mov     si, ax
        mov     cx, dx                  ;Put dword in cx:si
        mov     al,'$'
        push    ax                      ;Store string terminator
mainloop:
        mov     ax, cx                  ;\
        xor     dx, dx                  ;|
        div     bx                      ;|
        xchg    ax, si                  ;| Perform the division
        div     bx                      ;|
        mov     cx, ax                  ;|
        xchg    cx, si                  ;/
        mov     al, dl                  ;Move dl into al and
        add     al, 30h                 ;convert to a digit.
;The following four lines (cmp al, 39h up to the is_decimal_digit
;label) can be left out if you don't want to use a radix over 10.
;        cmp     al, 39h
;        jbe     is_decimal_digit
;        add     al, 7
;is_decimal_digit:
        push    ax                      ;Store the digit
        mov     ax, cx                  ;Are we done yet?
        or      ax, si
        jnz     mainloop
storeloop:
        pop     ax                      ;pop digits from stack
        stosb                           ;write to string loc
        cmp     al, '$'                 ;end of string?
        jnz     storeloop
        stosb                           ;write string terminator
        ret

strbuf  db 8 DUP '$'
bfr     db ' bytes ($'
kfr     db ' KB) of low DOS RAM is available for running programs.',0ah,0dh,'$'
