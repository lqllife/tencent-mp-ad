## 软件使用说明

### 目录结构

```
├── auth # 此文件夹用于存放登录的文件，不可修改
│   └── auth.json # 登录后，文件会自动生成，删除后需要重新登录
├── conf # 配置项
│   ├── images # 存放图片的素材文件夹，文件名不要包含中文
│   ├── videos # 存放视频的素材文件夹，文件名不要包含中文
│   ├── config.ini # 程序的配置文件，需要先修改配置文件才能运行主程序
│   └── 腾讯广告已选择地域定向导出信息.txt # 导出的地域定向文件
├── logs # 日志，程序每次运行时日志都会记录在此文件夹，日志文件按天创建
│   ├── 2023-02-19.txt
│   ├── 2023-02-20.txt
│   └── ······.txt
└── wechat.exe # 主程序
```

### 使用说明

1. 解压后打开文件夹
2. 修改`conf/config.ini`，根据文件内说明修改内容并保存文件
3. 在文件夹中按住`shift`，同时鼠标右键，选择"在此处打开powershell窗口"，在打开的`powershell`窗口中输入`.\wechat.exe`并回车等待程序运行，程序运行期间不要关闭`powershell窗口`
4. 程序出现错误时，记得对`powershell窗口`截图保留
5. 如果安装了`Windows Terminal`，可以替换`powershell`执行3~4步操作

### 远程桌面连接

1. 按下 `win + s` 键搜索 `mstc`
2. 计算机：192.168.0.126
3. 账号、密码：wechat

### 版本说明

- v1.0 - 2023-02-20
  - 基本版本发布，支持多个公众号批量创建计划
- v1.1 - 2023-04-04
  - 增加视频素材提交
- v1.2 - 2023-04-06
  - 修改上传素材的方式，加快上传素材的速度
- v1.3 - 2023-04-10
  - 配置项增加年龄
- v1.3.1 - 2023-04-12
  - 程序运行中增加耗时的提醒
- v1.4 - 2023-04-12
  - 配置项增加一键起量的开关
- v1.4.1 - 2023-04-12
  - 提交计划时，增加素材不合规的判断
- v1.4.2 - 2023-04-12
  - 公众号出现多个结果时只选择第一个