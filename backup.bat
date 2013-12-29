for /f "tokens=1-5 delims=/ " %%d in ("%date%") do set filename=grabfile.%%g-%%f-%%e_%time:~0,2%-%time:~3,2%-%time:~6,2%.zip

"c:\Program Files\7-Zip\7z.exe" a "..\%filename%" *
