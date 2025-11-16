# Invoke-DuckyScriptCompiler.ps1
# Compiles duckyScript .txt files to .dsb bytecode
# Automatically fetches the latest make_bytecode.py from duckyPad-Pro-Configurator

param(
  [Parameter(Mandatory=$false)]
  [string]$ProfilePath
)

# Configuration
$repo = "duckyPad/duckyPad-Configurator"
$compilerFileName = "make_bytecode.py"
$vendorDir = Join-Path $PSScriptRoot "vendor"
$compilerPath = Join-Path $vendorDir $compilerFileName

function Get-LatestCompiler {
  # Ensure vendor directory exists
  if (-not (Test-Path $vendorDir)) {
    New-Item -Path $vendorDir -ItemType Directory -Force | Out-Null
  }
  
  # Check if compiler already exists
  if (Test-Path $compilerPath) {
    Write-Host "✓ Using existing $compilerFileName" -ForegroundColor Green
    return $true
  }
  
  Write-Host "Fetching latest make_bytecode.py from GitHub..." -ForegroundColor Cyan
  
  try {
    # Get latest release from GitHub API
    $releaseUrl = "https://api.github.com/repos/$repo/releases/latest"
    $release = Invoke-RestMethod -Uri $releaseUrl -Headers @{ "User-Agent" = "PowerShell" }
    
    $zipUrl = $release.zipball_url
    $tempZip = Join-Path $env:TEMP "duckypad-configurator.zip"
    $tempExtract = Join-Path $env:TEMP "duckypad-configurator-extract"
    
    # Download and extract
    Write-Host "Downloading release $($release.tag_name)..." -ForegroundColor Cyan
    Invoke-WebRequest -Uri $zipUrl -OutFile $tempZip
    
    # Clean up old extraction
    if (Test-Path $tempExtract) {
      Remove-Item -Path $tempExtract -Recurse -Force
    }
    
    # Extract archive
    Expand-Archive -Path $tempZip -DestinationPath $tempExtract -Force
    
    # Find the source directory containing Python files
    $sourceDir = Get-ChildItem -Path $tempExtract -Recurse -Directory | 
      Where-Object { (Get-ChildItem -Path $_.FullName -Filter "make_bytecode.py" -File).Count -gt 0 } |
      Select-Object -First 1
    
    if (-not $sourceDir) {
      throw "Could not find source directory with make_bytecode.py"
    }
    
    # Copy all Python files from source directory to vendor folder
    $pythonFiles = Get-ChildItem -Path $sourceDir.FullName -Filter "*.py" -File
    $copiedFiles = 0
    
    foreach ($file in $pythonFiles) {
      $destPath = Join-Path $vendorDir $file.Name
      Copy-Item -Path $file.FullName -Destination $destPath -Force
      $copiedFiles++
    }
    
    if ($copiedFiles -gt 0) {
      Write-Host "✓ Successfully downloaded $copiedFiles Python files (version $($release.tag_name))" -ForegroundColor Green
    } else {
      throw "No Python files found in release archive"
    }
    
    # Cleanup
    Remove-Item -Path $tempZip -Force -ErrorAction SilentlyContinue
    Remove-Item -Path $tempExtract -Recurse -Force -ErrorAction SilentlyContinue
    
    return $true
  }
  catch {
    Write-Host "✗ Failed to fetch latest compiler: $_" -ForegroundColor Red
    return $false
  }
}

function Test-PythonAvailable {
  try {
    $pythonVersion = & python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
      Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
      return $true
    }
  }
  catch {
    Write-Host "✗ Python not found. Please install Python 3." -ForegroundColor Red
    return $false
  }
  return $false
}

function Invoke-Compilation {
  param(
    [string]$InputFile,
    [string]$OutputFile
  )
  
  try {
    $result = & python $compilerPath $InputFile $OutputFile 2>&1
    
    if ($LASTEXITCODE -eq 0) {
      $fileSize = (Get-Item $OutputFile).Length
      Write-Host "  ✓ Compiled: $(Split-Path $InputFile -Leaf) → $(Split-Path $OutputFile -Leaf) ($fileSize bytes)" -ForegroundColor Green
      return $true
    } else {
      Write-Host "  ✗ Compilation failed: $(Split-Path $InputFile -Leaf)" -ForegroundColor Red
      Write-Host "    Error: $result" -ForegroundColor Red
      return $false
    }
  }
  catch {
    Write-Host "  ✗ Exception during compilation: $_" -ForegroundColor Red
    return $false
  }
}

function Invoke-ProfileCompilation {
  param([string]$Path)
  
  # Find all .txt files matching duckyScript naming patterns (key*.txt or key*-release.txt)
  $scriptFiles = Get-ChildItem -Path $Path -Recurse -Filter "*.txt" -File | 
    Where-Object { $_.Name -match '^key\d+(-release)?\.txt$' }
  
  if ($scriptFiles.Count -eq 0) {
    Write-Host "No duckyScript .txt files found in $Path" -ForegroundColor Yellow
    return @{ Total = 0; Success = 0; Failed = 0 }
  }
  
  Write-Host "`nCompiling $($scriptFiles.Count) duckyScript files in: $Path" -ForegroundColor Cyan
  
  $stats = @{ Total = 0; Success = 0; Failed = 0 }
  
  foreach ($txtFile in $scriptFiles) {
    $stats.Total++
    
    # Output .dsb file in same directory as .txt file
    $dsbFile = Join-Path $txtFile.DirectoryName "$($txtFile.BaseName).dsb"
    
    if (Invoke-Compilation -InputFile $txtFile.FullName -OutputFile $dsbFile) {
      $stats.Success++
    } else {
      $stats.Failed++
    }
  }
  
  return $stats
}

# Main execution
Write-Host "`n=== duckyScript Bytecode Compiler ===" -ForegroundColor Cyan
Write-Host "Repository: $repo`n" -ForegroundColor Gray

# Check for Python
if (-not (Test-PythonAvailable)) {
  exit 1
}

# Fetch latest compiler
if (-not (Get-LatestCompiler)) {
  Write-Host "`nFailed to fetch compiler. Exiting." -ForegroundColor Red
  exit 1
}

# Determine compilation scope
if ($ProfilePath) {
  # Compile specific profile
  if (-not (Test-Path $ProfilePath)) {
    Write-Host "Error: Profile path not found: $ProfilePath" -ForegroundColor Red
    exit 1
  }
  
  $stats = Invoke-ProfileCompilation -Path $ProfilePath
} else {
  # Compile all profiles
  $profilesRoot = Join-Path (Split-Path $PSScriptRoot -Parent | Split-Path -Parent) "profiles"
  
  if (-not (Test-Path $profilesRoot)) {
    Write-Host "Error: Profiles directory not found: $profilesRoot" -ForegroundColor Red
    exit 1
  }
  
  Write-Host "Compiling all profiles in: $profilesRoot`n" -ForegroundColor Cyan
  
  $stats = Invoke-ProfileCompilation -Path $profilesRoot
}

# Summary
Write-Host "`n=== Compilation Summary ===" -ForegroundColor Cyan
Write-Host "Total files:      $($stats.Total)" -ForegroundColor White
Write-Host "Successfully compiled: $($stats.Success)" -ForegroundColor Green
Write-Host "Failed:           $($stats.Failed)" -ForegroundColor $(if ($stats.Failed -gt 0) { "Red" } else { "Green" })

if ($stats.Failed -gt 0) {
  exit 1
}

Write-Host "`n✓ Compilation complete!" -ForegroundColor Green
