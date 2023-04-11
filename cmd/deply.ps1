<#
将打包后的文件，复制到当前文件夹下各子文件夹内
#>

$file = 'wechat.exe'
$dirs = Get-ChildItem -Directory -Name

foreach ($dir in $dirs) {
    Copy-Item -Path $file -Destination $dir
}

Remove-Item $file

Write-Host '复制完成，2秒后自动退出'
sleep 2
