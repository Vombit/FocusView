@echo off
uv run -m nuitka ^
    --standalone ^
    --onefile ^
    --enable-plugin=pyqt6 ^
    --include-data-dir=bin=bin ^
    --windows-icon-from-ico=bin/resources/images/logo.ico ^
    --output-file="Focus View.exe" ^
    ./main.py




@REM --windows-console-mode=disable ^