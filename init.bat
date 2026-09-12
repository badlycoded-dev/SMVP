@echo off
set FOUND=

for %%F in (dep.txt deps.txt req.txt reqs.txt requirements.txt requirements-dev.txt) do (
    if exist "%%F" (
        set FOUND=%%F
        goto :install
    )
)

echo No dependencies file found.
goto :end

:install
echo Found %FOUND% - installing dependencies...
call "%~dp0venv\Scripts\activate.bat"
pip install -r "%FOUND%"
echo Dependencies installed.

:end