import requests
import os
import re
import random
import configparser
import time
import frpc_worker
import threading
import uuid
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pyautogui



def logging(msg):
    print('[info] (%s) %s' % (time.strftime(
        '%Y-%m-%d %H:%M:%S', time.localtime(time.time())), msg))


logging('加载service.conf配置文件')
config = configparser.ConfigParser()
config.read('service.conf', encoding='utf-8')
_config = config['config']


# 有公网ip的实验机器
tenLab = {
    "centos6": [
        'https://cloud.tencent.com/lab/courseDetail/10030',
        'https://cloud.tencent.com/lab/courseDetail/10001',
        'https://cloud.tencent.com/lab/courseDetail/10003',
        'https://cloud.tencent.com/lab/courseDetail/10002',
        'https://cloud.tencent.com/lab/courseDetail/10026'

    ],
    "centos7": [
        'https://cloud.tencent.com/lab/courseDetail/10045',
        'https://cloud.tencent.com/lab/courseDetail/915869039067641',
        'https://cloud.tencent.com/lab/courseDetail/10171',
        'https://cloud.tencent.com/lab/courseDetail/10303',
        'https://cloud.tencent.com/lab/courseDetail/10344',
        'https://cloud.tencent.com/lab/courseDetail/929392973578745',
        'https://cloud.tencent.com/lab/courseDetail/10071',
        'https://cloud.tencent.com/lab/courseDetail/10100',
        'https://cloud.tencent.com/lab/courseDetail/10219',
        'https://cloud.tencent.com/lab/courseDetail/10445',
        'https://cloud.tencent.com/lab/courseDetail/10084',
        'https://cloud.tencent.com/lab/courseDetail/10409',
        'https://cloud.tencent.com/lab/courseDetail/928975678341625',
        'https://cloud.tencent.com/lab/courseDetail/815743319409145',
        'https://cloud.tencent.com/lab/courseDetail/10072',
        'https://cloud.tencent.com/lab/courseDetail/1180814860354041'
        'https://cloud.tencent.com/lab/courseDetail/754986762895865',
        'https://cloud.tencent.com/lab/courseDetail/10454',
        'https://cloud.tencent.com/lab/courseDetail/877691410579961',
        'https://cloud.tencent.com/lab/courseDetail/1029121634468345'
    ]
}
def newTanzhen():
    uuid4 = str(uuid.uuid4())
    url = 'https://ip.iculture.cc/index.php?action=probe_add'
    postdata = {
        'add_key': uuid4,
        'add_probe_page': '404',
        'add_ip_location_function': 'on',
        'add_email_notification_function': 'on',
        'add_email': 'example@test.com',
        'add_qqshare_title': str(uuid.uuid4()),
        'add_qqshare_pics': 'https://www.iculture.cc/icon/GGbond.jpg',
        'add_qqshare_summary': '123',
        'add_qqshare_desc': '123',
    }
    r = requests.post(url, data=postdata)
    if '生成成功' in r.text:
        return uuid4
    return False

def queryTanzhen(uuid4):
    url = 'https://ip.iculture.cc/probe_query.php?action=probe_query'
    postdata = {
        'query_key': uuid4,
    }
    r = requests.post(url, data=postdata)
    ip = re.findall(r'"ip":"(.*?)"', r.text)
    if ip:
        return ip[0]
    return False

length = len(tenLab['centos6']) + len(tenLab['centos7'])
logging('已加载列表' + str(length))
# 基于mapping.conf生成frpc.ini配置文件
logging('开始生成frpc.ini配置文件')
frps_template = '''[common]
server_addr = myipaddr
server_port = ''' + _config['backend_port'] + '''
token = ''' + _config['backend_token'] + '''
'''
frps_mapping_template = '''
[(random)]
type = tcp
local_ip = (local_ip)
local_port = (local_port)
remote_port = (remote_port)
'''
if os.path.exists('mapping.conf'):
    with open('mapping.conf', 'r') as f:
        for line in f.readlines():
            data = line.split('->')
            if len(data) != 2:
                continue
            local_bind = data[0].strip()
            local = local_bind.split(':')
            if len(local) != 2:
                continue
            local_ip = local[0].strip()
            if not re.match(r'^((25[0-5]|2[0-4]\d|[01]?\d\d?)($|(?!\.$)\.)){4}$', local_ip):
                continue
            local_port = local[1].strip()
            if int(local_port) < 1 or int(local_port) > 65535:
                continue

            remote_port = data[1].strip()
            if int(remote_port) < 1 or int(remote_port) > 65535:
                continue

            mapping_config = frps_mapping_template.replace('(local_ip)', local_ip).replace('(local_port)', local_port).replace(
                '(remote_port)', remote_port).replace('(random)', 'remote_' + str(remote_port))
            frps_template += "\n" + mapping_config

        frpc_config = frps_template
        with open('frpc.ini', 'w') as f:
            f.write(frps_template)
else:
    logging('mapping.conf映射文件不存在，请先创建')
    exit(1)

logging('frpc.ini配置文件生成完成')

# 生成frps.ini
logging('开始生成frps.ini配置文件')
frps_template = '''
[common]
bind_port = ''' + _config['backend_port'] + '''
token = ''' + _config['backend_token'] + '''
'''
with open('frps.ini', 'w') as f:
    f.write(frps_template)
logging('frps.ini配置文件生成完成')

logging('开始启动webdriver登录腾讯云')

option = webdriver.EdgeOptions()
option.add_experimental_option('excludeSwitches', ['enable-logging'])
driver = webdriver.Edge(_config['webdriver'], options=option)
driver.get(
    'https://cloud.tencent.com/login?s_url=https%3A%2F%2Fcloud.tencent.com%2Flab%2Flabslist%23')
while True:
    already = input('腾讯云登录成功后输入y继续：')
    if already == 'y':
        break

driver.get('https://cloud.tencent.com/lab/labslist')
if '登录' in driver.page_source:
    logging('未登录成功，请重新运行')
    exit(1)


def getLab(driver):
    label = False
    is_start = False
    centos = tenLab['centos6'] + tenLab['centos7']

    for lab in centos:
        driver.get(lab)
        time.sleep(0.5)
        realTitle = None
        for i in range(1, 10):
            try:
                title = driver.title
                realTitle = (title.split('-')[0]).strip()
            except Exception as e:
                logging('获取标题失败，正在重试')
                time.sleep(0.1)
                continue
        if realTitle == None:
            realTitle = '未知'

        logging('检测' + realTitle + '可用状态')
        page_source = driver.page_source

        if '正在试验' in page_source:
            logging('检测到正在的实验，继续进行')
            while True:
                try:
                    location = pyautogui.locateCenterOnScreen('black.png')
                    if location is not None:
                        pyautogui.click(location.x, location.y,
                                        button='left', interval=0.1, clicks=1)
                        continue_lab = driver.find_element(
                            By.XPATH, '//*[@id="root"]/div/div[2]/div[2]/div[2]/button[1]')
                        continue_lab.click()
                        label = lab
                        is_start = True
                        break
                except Exception as e:
                    logging('webdriver报告错误，继续进行')
                    continue
        if is_start:
            break

        if '名额已满' in page_source:
            logging('(' + realTitle + ') 无法使用，已跳过1')
            continue
        if '免费' not in page_source or '立即实验' not in page_source:
            logging('(' + realTitle + ') 无法使用，已跳过2')
            continue

        while True:
            try:
                start_lab = driver.find_element(
                    By.XPATH, '//*[@id="root"]/div/div/div/section/div/div/div/div[2]/div[1]/div/div/div[2]/button')
                start_lab.click()
                time.sleep(1)
                if '您今天已参与过该实验，当前实验资源紧张，请明日再来' in driver.page_source:
                    logging('(' + realTitle + ') 无法使用，已跳过3')
                    break

                label = lab
                is_start = True
                break
            except Exception as e:
                logging('webdriver报告错误，继续进行')
                continue

    if is_start == False:
        logging('没有可用的现有实验室，程序退出')
        return False

    driver.refresh()
    time.sleep(1)
    logging('已成功申请到可用资源')
    # 需要等待30秒初始化
    time.sleep(30)
    return label


lab_instance = getLab(driver)
if lab_instance == False:
    while True:
        logging('10秒后重新获取资源')
        time.sleep(10)
        lab_instance = getLab(driver)
        if lab_instance != False:
            break





def initInstance(driver):

    try:
        driver.swith_to_alert().accept()
    except Exception as e:
        logging('没有弹窗，继续进行')
    
    try:
        driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div[4]/div[2]/div[1]/div[1]/div[1]/div[2]/div/div/div/div[3]/div[2]/div/ul/li[2]/div/div[2]/a[1]/span').click()
    except Exception as e:
        logging('非特殊实验，继续进行')

    while True:
        try:
            console = driver.find_element(
                By.CLASS_NAME, 'xterm-helper-textarea')
            console.send_keys('cd /root')
            console.send_keys(Keys.ENTER)
            console.send_keys('rm -rf /root/frps.ini')
            console.send_keys(Keys.ENTER)
            # 杀死frps进程
            console.send_keys('killall frps')
            break
        except Exception as e:
            logging('发送命令失败，正在重试1')
            continue

    frps = frps_template.split('\n')
    for i in frps:
        while True:
            try:
                console.send_keys('echo ' + i + ' >> frps.ini')
                console.send_keys(Keys.ENTER)
                break
            except Exception as e:
                logging('发送命令失败，正在重试2')
                continue

    while True:
        try:
            tanZhen = False
            while True:
                tanZhen = newTanzhen()
                if tanZhen != False:
                    break
                time.sleep(10)
                logging('10秒后重新获取IP探针')

            console.send_keys('curl https://ip.iculture.cc/probe.php?key=' + tanZhen)
            console.send_keys(Keys.ENTER)
            time.sleep(5)


            install_cmd = 'cd /root && wget https://d.frps.cn/file/frp/v0.37.0/frp_0.37.0_linux_amd64.tar.gz && tar -zxvf frp_0.37.0_linux_amd64.tar.gz && cd frp_0.37.0_linux_amd64 && chmod +x frps && nohup ./frps -c /root/frps.ini &'
            console.send_keys(install_cmd)
            console.send_keys(Keys.ENTER)

            TanzhenIp = False
            while True:
                TanzhenIp = queryTanzhen(tanZhen)
                if TanzhenIp != False:
                    break

            

            return TanzhenIp

        except Exception as e:
            logging('发送命令失败，正在重试3')
            continue


def checkStatus(driver):
    while True:
        try:
            outtime = driver.find_element(
                By.CLASS_NAME, 'editor-timer-num').text
            return outtime
        except Exception as e:
            continue


def internal(driver):
    while True:
        time.sleep(1)
        outtime = checkStatus(driver)
        date = outtime.split(':')
        hour = int(date[0])
        minute = int(date[1])
        second = int(date[2])
        if hour == 0 and minute < int(_config['new_resource_minute']):
            logging('开始转移资源')
            while True:
                try:
                    driver.find_element(
                        By.XPATH, '//*[@id="root"]/div/div/div[4]/div[1]/div/div[2]/div[1]/button[2]/span').click()
                    break
                except Exception as e:
                    continue
            while True:
                try:
                    driver.find_element(
                        By.XPATH, '//*[@id="lab-tp-overlay-root"]/div/div[2]/div/footer/button[1]').click()
                    break
                except Exception as e:
                    continue

            return False
        logging('剩余时间：' + outtime)
        return True


# 对资源进行初始化
myIpaddr = initInstance(driver)
logging('动态IP：' + myIpaddr)
# 替换frpc
with open('frpc.ini', 'w') as f:
    f.write(frpc_config.replace('myipaddr', myIpaddr))
# 公网ip写到frps.ip
with open('frps.ip', 'w') as f:
    f.write(myIpaddr)

threading.Thread(target=frpc_worker.Listen,args=('frpc.exe','frpc.ini')).start()

while True:
    logging('检查状态')
    time.sleep(5)
    if internal(driver):
        continue
    logging('开始获取新资源')
    lab_instance = getLab(driver)
    if lab_instance == False:
        while True:
            logging('10秒后重新获取资源')
            time.sleep(10)
            lab_instance = getLab(driver)
            if lab_instance != False:
                break
    logging('开始初始化新资源')
    myIpaddr = initInstance(driver)
    logging('动态IP：' + myIpaddr)
    frpc_worker.createnewconfig(myIpaddr)
    with open('frps.ip', 'w') as f:
        f.write(myIpaddr)

    logging('初始化完成')
