<#
打包项目
需要在项目根目录下执行 .\cmd\pack.ps1
#>

# 删除已生成的dist文件夹
$distPath = 'pack/dist'
if (Test-Path $distPath) {
    Remove-Item -Recurse -Force $distPath
}

# 项目打包
$root = Get-Location
Set-Location $root
$env:PLAYWRIGHT_BROWSERS_PATH = "0"
playwright install chromium
$dataPath = -Join ($root, "/env/Lib/site-packages/playwright/driver;playwright/driver")
pyinstaller -F -n wechat --add-data $dataPath -i "../wechat.ico" --specpath pack/build --distpath pack/dist --workpath pack/build --clean main.py

# 初始化文件
Copy-Item 'conf' -Recurse 'pack/dist/conf'
New-Item -ItemType Directory 'pack/dist/auth'
New-Item -ItemType Directory 'pack/dist/logs'
Copy-Item 'README.pdf' 'pack/dist/使用说明.pdf'
