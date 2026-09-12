$candidates = @("dep.txt", "deps.txt", "req.txt", "reqs.txt", "requirements.txt", "requirements-dev.txt")
$found = $candidates | Where-Object { Test-Path $_ } | Select-Object -First 1

if ($found) {
    Write-Host "Found $found - installing dependencies..."
    Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
    & "$PSScriptRoot\venv\Scripts\Activate.ps1"
    pip install -r $found
    Write-Host "Dependencies installed."
} else {
    Write-Host "No dependencies file found."
}