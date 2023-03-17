$root = Get-Location
Set-Location $root

Remove-Item -Force -Exclude .gitignore 'pack/build'
Remove-Item -Force -Exclude .gitignore 'pack/dist'
