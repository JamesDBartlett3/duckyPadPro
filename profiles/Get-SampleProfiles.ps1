# Get-SampleProfiles.ps1
# Downloads sample profiles from the duckyPad-Pro repository

param(
  [switch]$Force
)

# Configuration
$repo = "dekuNukem/duckyPad-Pro"
$sampleProfilesUrl = "https://github.com/$repo/raw/master/resources/sample_profiles/sample_profiles.zip"
$profilesRoot = $PSScriptRoot
$sampleProfilesDir = Join-Path $profilesRoot "sample_profiles"

function Get-SampleProfiles {
  # Check if sample_profiles already exists
  if ((Test-Path $sampleProfilesDir) -and -not $Force) {
    Write-Host "✓ Sample profiles already exist at: $sampleProfilesDir" -ForegroundColor Green
    Write-Host "  Use -Force to re-download" -ForegroundColor Gray
    return $true
  }
  
  Write-Host "Downloading sample profiles from GitHub..." -ForegroundColor Cyan
  Write-Host "Repository: $repo`n" -ForegroundColor Gray
  
  try {
    $tempZip = Join-Path $env:TEMP "sample_profiles.zip"
    
    # Download sample_profiles.zip
    Write-Host "Downloading sample_profiles.zip..." -ForegroundColor Cyan
    Invoke-WebRequest -Uri $sampleProfilesUrl -OutFile $tempZip
    
    # Remove existing sample_profiles if using -Force
    if (Test-Path $sampleProfilesDir) {
      Write-Host "Removing existing sample_profiles..." -ForegroundColor Yellow
      Remove-Item -Path $sampleProfilesDir -Recurse -Force
    }
    
    # Extract archive
    Write-Host "Extracting sample profiles..." -ForegroundColor Cyan
    $tempExtract = Join-Path $env:TEMP "sample_profiles_extract"
    
    # Clean up old extraction
    if (Test-Path $tempExtract) {
      Remove-Item -Path $tempExtract -Recurse -Force
    }
    
    # Extract zip directly to temp location
    Expand-Archive -Path $tempZip -DestinationPath $tempExtract -Force
    
    # Move the extracted content to sample_profiles folder
    Move-Item -Path $tempExtract -Destination $sampleProfilesDir -Force
    
    # Count extracted profiles
    if (Test-Path $sampleProfilesDir) {
      $profileCount = (Get-ChildItem -Path $sampleProfilesDir -Directory | Measure-Object).Count
      Write-Host "✓ Successfully downloaded $profileCount sample profiles" -ForegroundColor Green
      Write-Host "  Location: $sampleProfilesDir" -ForegroundColor Gray
    } else {
      Write-Host "✓ Sample profiles downloaded" -ForegroundColor Green
      Write-Host "  Location: $sampleProfilesDir" -ForegroundColor Gray
    }
    
    # Cleanup
    Remove-Item -Path $tempZip -Force -ErrorAction SilentlyContinue
    
    return $true
  }
  catch {
    Write-Host "✗ Failed to download sample profiles: $_" -ForegroundColor Red
    return $false
  }
}

# Main execution
Write-Host "`n=== duckyPad Pro Sample Profiles Downloader ===" -ForegroundColor Cyan

if (-not (Get-SampleProfiles)) {
  Write-Host "`nFailed to download sample profiles. Exiting." -ForegroundColor Red
  exit 1
}

Write-Host "`n✓ Sample profiles ready!" -ForegroundColor Green
Write-Host "  You can now reference these profiles when creating your own." -ForegroundColor Gray
