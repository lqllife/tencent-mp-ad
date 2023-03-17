$root = Get-Location
Set-Location $root
Remove-Item -Force 'pack/dist'

$env:PLAYWRIGHT_BROWSERS_PATH = "0"
playwright install chromium
$dataPath = -Join($root, "/env/Lib/site-packages/playwright/driver;playwright/driver")
pyinstaller -F -n wechat --add-data $dataPath -i wechat.ico --specpath pack/build --distpath pack/dist --workpath pack/build --clean main.py

Copy-Item 'conf' -Recurse 'pack/dist/conf'
Remove-Item -Force 'pack/dist/conf/.gitignore'
New-Item -ItemType Directory 'pack/dist/auth'
New-Item -ItemType Directory 'pack/dist/logs'
Copy-Item 'README.pdf' 'pack/dist/使用说明.pdf'

#Remove-Item -Force 'pack/微信批量提素材v1.1'
#Copy-Item 'pack/dist' -Force -Recurse 'pack/微信批量提素材v1.1'
