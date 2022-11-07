# freepubip
利用腾讯云实验室白嫖动态公网ip

### 原理
利用腾讯云实验室https://cloud.tencent.com/lab/labslist# 的实验机器，一个实验可以使用一个小时的CVM机器，使用selenium自动申请不同的实验，然后自动的切换frp到新的实验机器。

### 环境要求
```
python >= 3.8
```

## 如何部署？

```
pip install requests selenium pyautogui -i https://pypi.tuna.tsinghua.edu.cn/simple
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


