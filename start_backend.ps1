Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendRoot = Join-Path $projectRoot "backend"
$venvRoot = Join-Path $backendRoot ".venv"

function Get-PythonCommand {
    $pyLauncher = Get-Command py -ErrorAction SilentlyContinue
    if ($pyLauncher) {
        try {
            & py -3.11 -c "import sys; print(sys.version)" *> $null
            if ($LASTEXITCODE -eq 0) {
                return @("py", "-3.11")
            }
        } catch {
        }
    }

    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if (-not $pythonCommand) {
        throw "Python was not found. Install Python 3.11, then rerun .\start_backend.ps1."
    }

    $versionText = & python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
    if ($versionText -notmatch "^3\.(11|12)$") {
        throw "This project should run with Python 3.11 or 3.12. Current terminal Python is $versionText. Install Python 3.11, then rerun .\start_backend.ps1."
    }

    return @("python")
}

function Ensure-Venv {
    param(
        [string[]]$PythonCommand
    )

    $venvPython = Join-Path $venvRoot "Scripts\python.exe"

    if (-not (Test-Path $venvPython)) {
        Write-Host "Creating backend virtual environment..."
        $venvArgs = @()
        if ($PythonCommand.Length -gt 1) {
            $venvArgs += $PythonCommand[1..($PythonCommand.Length - 1)]
        }
        $venvArgs += @("-m", "venv", $venvRoot)
        & $PythonCommand[0] @venvArgs
    }

    return $venvPython
}

function Ensure-Dependencies {
    param(
        [string]$PythonExe
    )

    $hasFastApi = $false
    try {
        & $PythonExe -c "import fastapi, uvicorn" *> $null
        $hasFastApi = $LASTEXITCODE -eq 0
    } catch {
        $hasFastApi = $false
    }

    if (-not $hasFastApi) {
        Write-Host "Installing backend dependencies..."
        & $PythonExe -m pip install --upgrade pip
        & $PythonExe -m pip install -r (Join-Path $backendRoot "requirements.txt")
    }
}

$pythonCommand = Get-PythonCommand
$venvPython = Ensure-Venv -PythonCommand $pythonCommand
Ensure-Dependencies -PythonExe $venvPython

Write-Host "Starting PhishGuard backend on http://127.0.0.1:8000"
Set-Location $backendRoot
& $venvPython -m uvicorn app.main:app --host 0.0.0.0 --port 8000
