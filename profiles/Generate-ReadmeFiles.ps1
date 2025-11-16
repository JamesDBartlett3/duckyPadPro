param(
  [switch]$Overwrite
)

Get-ChildItem -Recurse -Directory | 
  ForEach-Object {
    $name = $_.Name 
    $fullname = $_.FullName
    $readme_path = "$($fullname)/readme-$($name).md"
    
    # Get subdirectories
    $subdirs = Get-ChildItem -Path $fullname -Directory
    
    if ($subdirs.Count -gt 0) {
      # Parent directory: check if file is empty or whitespace-only
      $shouldWrite = $false
      if (-not (Test-Path $readme_path)) {
        $shouldWrite = $true
      } elseif ($Overwrite) {
        $shouldWrite = $true
      } else {
        $existingContent = Get-Content -Path $readme_path -Raw
        if ([string]::IsNullOrWhiteSpace($existingContent)) {
          $shouldWrite = $true
        }
      }
      
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