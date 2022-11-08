import requests
import configparser
import time


def logging(msg):
    print('[info] (%s) %s' % (time.strftime(
        '%Y-%m-%d %H:%M:%S', time.localtime(time.time())), msg))

config = configparser.ConfigParser()
config.read('service.conf', encoding='utf-8')
_dnspod = config['dnspod']
_comPost = 'login_token=' + _dnspod['tokenid'] + ','+ _dnspod['token']+'&format=json'



def checkToken():
    api_url = 'https://dnsapi.cn/Info.Version'
    postdata = _comPost
    r = requests.post(api_url, data=postdata,verify=False).json()
    if r['status']['code'] == '1':
        return True
    else:
        logging(r['status']['message'])
        return False

def getDomainId():
    api_url = 'https://dnsapi.cn/Domain.List'
    postdata = {
        'login_token': _dnspod['tokenid'] + ',' + _dnspod['token'],
        'format': 'json'
    }
    # print(postdata)
    r = requests.post(api_url, data=postdata,verify=False).json()
    # print(r)
    if r['status']['code'] == '1':
        for i in r['domains']:
            # print(i)
            if i['name'] == _dnspod['domain']:
                return i['id']
    else:
        logging(r['status']['message'])
        return False

def getSubDomain():
    api_url = 'https://dnsapi.cn/Record.List'
    postdata = {
        'login_token': _dnspod['tokenid'] + ',' + _dnspod['token'],
        'format': 'json',
        'domain_id': str(getDomainId())
    }
    r = requests.post(api_url, data=postdata,verify=False).json()
    if r['status']['code'] == '1':
        for i in r['records']:
            if i['name'] == _dnspod['subdomain']:
                return i['id']
    else:
        return False

def updateRecord(ip):
    if _dnspod['enable'] != 'yes':
        return False
    apiUrl = 'https://dnsapi.cn/Record.Modify'
    # postdata = _comPost + '&domain_id=' + getDomainId() + '&record_id=' + getSubDomain() + '&sub_domain=' + _dnspod['subdomain'] + '&record_type=A&record_line=默认&value=' + ip
    postdata = {
        'login_token': _dnspod['tokenid'] + ',' + _dnspod['token'],
        'format': 'json',
        'domain_id': str(getDomainId()),
        'record_id': str(getSubDomain()),
        'sub_domain': _dnspod['subdomain'],
        'record_type': 'A',
        'record_line': '默认',
        'value': ip
    }
    r = requests.post(apiUrl, data=postdata,verify=False).json()
    if r['status']['code'] == '1':
        logging('dnspod 已将解析记录更新为 %s' % ip)
        return True
    else:
        logging('dnspod 更新解析记录失败')
        return False

def initrd():
    if _dnspod['enable'] == 'yes':
        if checkToken() == False:
            logging('dnspod token验证失败')
            exit()
        if getDomainId() == False:
            logging('dnspod 获取域名ID失败')
            exit()
        if getSubDomain() == False:
            logging('dnspod 获取子域名ID失败')
            exit()
        