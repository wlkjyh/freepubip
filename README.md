# freepubip
利用腾讯云实验室白嫖动态公网ip

### 原理
利用腾讯云实验室https://cloud.tencent.com/lab/labslist# 的实验机器，一个实验可以使用一个小时的CVM机器，使用selenium自动申请不同的实验，然后自动的切换frp到新的实验机器。

### 环境要求
```
python >= 3.8
edge >= 107.0.1418.35
```


## 如何部署？

```
pip install requests selenium pyautogui -i https://pypi.tuna.tsinghua.edu.cn/simple
```
```
下载frpc.exe到当前目录
下载与edge同版本的webdriver到当前目录下msedgedriver.exe
```

### 配置文件
服务主配置文件 service.conf
```
[config]
; frp 会话端口，会注入到环境中
backend_port = 65534
; frp token，会注入到环境中
backend_token = Qwer1234
; webdriver驱动程序位置
webdriver = msedgedriver.exe
; 最后多少分钟创建新资源
new_resource_minute = 5
```
映射文件mapping.conf
```
; 源地址:源端口->目的端口
127.0.0.1:3389->3380
```

### 如何启动?
```
python main.py
```

### 如何查看当前申请到的公网ip?
可以在frps.ip中查看，你可以监听这个文件的内容改变，实现自动域名解析

### 如何切换edge驱动程序？
```
编辑service.conf文件中的webdriver项，可以设置新的驱动程序位置
```
### 联系我
```
wlkjyy@vip.qq.com
```
