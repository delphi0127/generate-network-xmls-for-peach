@rmdir /s/q minset
@minset -s samples\*.png -m minset bin\pngcheck.exe %%s
@rem minset -s samples\*.png -k -m minset "C:\Program Files (x86)\Mozilla Firefox\firefox.exe" %%s
