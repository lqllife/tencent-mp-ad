<#
将打包后的文件，复制到当前文件夹下各子文件夹内

目录结构如下：
├── 项目1文件夹
├── 项目2文件夹
├── 项目3文件夹
├── 项目n文件夹
├── wechat.exe
└── deply.ps1
#>

$file = 'wechat.exe'
$dirs = Get-ChildItem -Directory -Name

foreach ($dir in $dirs) {
    Copy-Item -Path $file -Destination $dir
}

Remove-Item $file

Write-Host '复制完成，2秒后自动退出'
sleep 2
