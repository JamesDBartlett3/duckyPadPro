# Test-DuckyScriptCompilation.ps1
# Validates duckyScript compilation by checking .txt to .dsb conversions

param(
  [Parameter(Mandatory=$false)]
  [string]$ProfilePath
)

function Test-CompilationPair {
  param(
    [string]$TxtFile,
    [string]$DsbFile
  )
  
  $issues = @()
  
  # Check if .txt file exists
  if (-not (Test-Path $TxtFile)) {
    $issues += "Missing source .txt file"
    return @{ Valid = $false; Issues = $issues }
  }
  
  # Check if .dsb file exists
  if (-not (Test-Path $DsbFile)) {
    $issues += "Missing compiled .dsb file"
    return @{ Valid = $false; Issues = $issues }
  }
  
  # Check .dsb file size (should be > 0 and divisible by 3 for 3-byte instructions)
  $dsbSize = (Get-Item $DsbFile).Length
  
  if ($dsbSize -eq 0) {
    $issues += "Empty .dsb file (0 bytes)"
  }
  
  # Basic sanity check: minimum valid bytecode size
  # At minimum, we'd expect HALT instruction (3 bytes)
  if ($dsbSize -lt 3) {
    $issues += "Invalid .dsb size ($dsbSize bytes, minimum 3 expected)"
  }
  
  # Check if sizes are reasonable
  $txtSize = (Get-Item $TxtFile).Length
  if ($txtSize -gt 0 -and $dsbSize -eq 0) {
    $issues += "Non-empty .txt compiled to empty .dsb"
  }
  
  # Check .dsb is newer than .txt (or same age)
  $txtModified = (Get-Item $TxtFile).LastWriteTime
  $dsbModified = (Get-Item $DsbFile).LastWriteTime
  
  if ($dsbModified -lt $txtModified) {
    $issues += ".dsb is older than .txt (needs recompilation)"
  }
  
  return @{
    Valid = ($issues.Count -eq 0)
    Issues = $issues
    TxtSize = $txtSize
    DsbSize = $dsbSize
    TxtModified = $txtModified
    DsbModified = $dsbModified
  }
}

function Test-ProfileCompilation {
  param([string]$Path)
  
  Write-Host "`nValidating compilations in: $Path" -ForegroundColor Cyan
  
  $txtFiles = Get-ChildItem -Path $Path -Recurse -Filter "*.txt" -File | 
    Where-Object { $_.Name -match '^key\d+(-release)?\.txt$' }
  
  if ($txtFiles.Count -eq 0) {
    Write-Host "No duckyScript .txt files found" -ForegroundColor Yellow
    return @{ Total = 0; Valid = 0; Invalid = 0; Missing = 0 }
  }
  
  $stats = @{
    Total = 0
    Valid = 0
    Invalid = 0
    Missing = 0
    Details = @()
  }
  
  foreach ($txtFile in $txtFiles) {
    $stats.Total++
    
    $dsbFile = Join-Path $txtFile.DirectoryName "$($txtFile.BaseName).dsb"
    $result = Test-CompilationPair -TxtFile $txtFile.FullName -DsbFile $dsbFile
    
    $relativePathTxt = $txtFile.FullName.Replace($Path, "").TrimStart('\', '/')
    
    if ($result.Valid) {
      $stats.Valid++
      Write-Host "  ✓ $relativePathTxt" -ForegroundColor Green
      if ($result.DsbSize) {
        Write-Host "    ($($result.TxtSize) bytes → $($result.DsbSize) bytes)" -ForegroundColor Gray
      }
    } else {
      if ($result.Issues -contains "Missing compiled .dsb file") {
        $stats.Missing++
        Write-Host "  ⚠ $relativePathTxt" -ForegroundColor Yellow
      } else {
        $stats.Invalid++
        Write-Host "  ✗ $relativePathTxt" -ForegroundColor Red
      }
      
      foreach ($issue in $result.Issues) {
        Write-Host "    - $issue" -ForegroundColor $(if ($result.Issues -contains "Missing compiled .dsb file") { "Yellow" } else { "Red" })
      }
    }
    
    $stats.Details += @{
      TxtFile = $txtFile.FullName
      DsbFile = $dsbFile
      Result = $result
    }
  }
  
  return $stats
}

# Main execution
Write-Host "`n=== duckyScript Compilation Validator ===" -ForegroundColor Cyan

# Determine validation scope
if ($ProfilePath) {
  if (-not (Test-Path $ProfilePath)) {
    Write-Host "Error: Profile path not found: $ProfilePath" -ForegroundColor Red
    exit 1
  }
  
  $stats = Test-ProfileCompilation -Path $ProfilePath
} else {
  # Validate all profiles
  $profilesRoot = Join-Path (Split-Path $PSScriptRoot -Parent | Split-Path -Parent) "profiles"
  
  if (-not (Test-Path $profilesRoot)) {
    Write-Host "Error: Profiles directory not found: $profilesRoot" -ForegroundColor Red
    exit 1
  }
  
  $stats = Test-ProfileCompilation -Path $profilesRoot
}

# Summary
Write-Host "`n=== Validation Summary ===" -ForegroundColor Cyan
Write-Host "Total .txt files: $($stats.Total)" -ForegroundColor White
Write-Host "Valid pairs:      $($stats.Valid)" -ForegroundColor Green
Write-Host "Missing .dsb:     $($stats.Missing)" -ForegroundColor Yellow
Write-Host "Invalid/Issues:   $($stats.Invalid)" -ForegroundColor $(if ($stats.Invalid -gt 0) { "Red" } else { "Green" })

if ($stats.Missing -gt 0) {
  Write-Host "`n💡 Tip: Run Invoke-DuckyScriptCompiler.ps1 to compile missing files" -ForegroundColor Cyan
}

if ($stats.Invalid -gt 0) {
  Write-Host "`n⚠ Some compilations have issues. Review errors above." -ForegroundColor Yellow
  exit 1
}

if ($stats.Missing -eq 0 -and $stats.Invalid -eq 0) {
  Write-Host "`n✓ All compilations are valid!" -ForegroundColor Green
} else {
  exit 1
}
