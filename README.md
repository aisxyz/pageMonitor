# pageMonitor
本程序可用来对指定网站进行监测，实现的功能如下：
1、监测目标网站下的文件是否发生修改，也可从界面只勾选部分页面。
2、发生修改就从备份中恢复（也可配置不自动恢复）。
3、发生修改时会向配置的邮箱发送告警邮件。

# 环境依赖：
1、python 3（本人使用python 3.5）。
2、mongodb 数据库，自行百度安装。
3、python第三方库flask，安装命令：pip3 install flask 。

# 运行方式：
1、先运行mongodb数据库（如果采用默认安装，应该运行mongod命令即可）。
2、运行websiteMonitor/webConsole.py，方式：python webConsole.py 。
3、在浏览器中打开：127.0.0.1:5000 。
4、初始登录账号和密码：root / root123 。
5、登录后到界面右上角“设置”里选择“监测配置”，进行相关配置，其中
	监测网站路径、备份路径和邮箱接收者三项必填。

另外，在 core 目录下有个 monitor.py 和 monitor2.py，前者使用的是轮询的方式进行监测，后者使用更高级的文件嵌入方式，但只能在 linux 系统下使用，因为它依赖 linux 系统的 inotify 内核特性，而且还要自行安装 inotifywait 命令。若要使用后者，请自行调整代码。

下面是部分截图
# 登录界面
![image](https://github.com/wangmingzhitu/pageMonitor/raw/master/snapshoot/登录界面.png)
# 监测界面
![image](https://github.com/wangmingzhitu/pageMonitor/raw/master/snapshoot/监测界面.png)
# 监测配置
![image](https://github.com/wangmingzhitu/pageMonitor/raw/master/snapshoot/监测配置.png)
