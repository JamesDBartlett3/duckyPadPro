param(
  [switch]$Overwrite,
  [switch]$Force
)

function Get-ReadmePath {
  param($Directory)
  
  $name = $Directory.Name
  $fullname = $Directory.FullName
  return @{
    Name = $name
    FullName = $fullname
    Path = Join-Path $fullname "readme-$($name).md"
  }
}

# Collect all directories first
$directories = Get-ChildItem -Recurse -Directory

# If Overwrite is specified without Force, check for existing files and prompt
if ($Overwrite -and -not $Force) {
  $filesToOverwrite = @()
  
  foreach ($dir in $directories) {
    $dirInfo = Get-ReadmePath $dir
    
    if (Test-Path $dirInfo.Path) {
      $filesToOverwrite += $dirInfo.Path
    }
  }
  
  if ($filesToOverwrite.Count -gt 0) {
    Write-Host "The following files will be overwritten:" -ForegroundColor Yellow
    foreach ($file in $filesToOverwrite) {
      Write-Host "  $file"
    }
    Write-Host ""
    
    $response = Read-Host "Continue? (Y/n)"
    if ($response -ine 'Y' -and $response -ne '') {
      Write-Host "Operation cancelled." -ForegroundColor Red
      return
    }
  }
}

# Process directories
foreach ($dir in $directories) {
  $dirInfo = Get-ReadmePath $dir
  $name = $dirInfo.Name
  $fullname = $dirInfo.FullName
  $readme_path = $dirInfo.Path
  
  # Get subdirectories
  $subdirs = Get-ChildItem -Path $fullname -Directory
  
  if ($subdirs.Count -gt 0) {
    # Parent directory: check if file is empty or whitespace-only
    $fileExists = Test-Path $readme_path
    $fileIsEmpty = -not $fileExists -or [string]::IsNullOrWhiteSpace((Get-Content -Path $readme_path -Raw -ErrorAction SilentlyContinue))
    $shouldWrite = (-not $fileExists) -or $Overwrite -or $fileIsEmpty
    
    if ($shouldWrite) {
      # Create table of contents
      $content = "# $($name)`n`n"
      foreach ($subdir in $subdirs) {
        $subdir_name = $subdir.Name
        $content += "## [$($subdir_name)]($($subdir_name)/readme-$($subdir_name).md)`n`n"
      }
      $content | Out-File -FilePath $readme_path -NoNewline
    }
  } else {
    # Leaf directory: create simple heading
    if (-not (Test-Path $readme_path) -or $Overwrite) { 
      "# $($name)" | Out-File -FilePath $readme_path
    }
  }
}