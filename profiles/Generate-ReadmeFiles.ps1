Get-ChildItem -Recurse -Directory | 
  ForEach-Object {
    $name = $_.Name 
    $readme_path = "$($_.FullName)/readme-$($name).md"
    if (-not (Test-Path $readme_path)) { 
      "# $($name)" | Out-File -FilePath $readme_path
    } 
  }