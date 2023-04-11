<#
用于删除打包产生的文件
需要在项目根目录下执行 .\cmd\clean.ps1
#>

$dirs = 'pack/dist', 'pack/build', '__pycache__'
foreach ($dir in $dirs) {
    if (Test-Path $dir) {
        Remove-Item -Recurse -Force $dir
    }
}
