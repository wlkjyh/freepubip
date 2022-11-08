import time,os,subprocess,hashlib,threading,configparser,re

config = configparser.ConfigParser()
config.read('service.conf', encoding='utf-8')
_config = config['config']

def createnewconfig(myIpaddr):

    frps_template = '''
[common]
server_addr = '''+myIpaddr+'''
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
        exit(1)
sub = None
def worker(frpc_file,frpc_ini):
    global sub
    if os.path.exists(frpc_file):
        if os.path.exists(frpc_ini):
            if os.path.exists('frpc.pid'):
                with open('frpc.pid','r') as f:
                    pid = f.read()
                if pid:
                    # os.system('kill -9 ' + pid)
                    if sub is not None:
                        sub.kill()
                    # sub.kill()
                    os.system('taskkill /f /pid ' + pid)

            sub = subprocess.Popen([frpc_file, '-c', frpc_ini],shell=True)
            pid = sub.pid
            with open('frpc.pid','w',encoding='utf-8') as f:
                f.write(str(pid))

            print('[info] (%s) %s' % (time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),'启动成功，进程号为' + str(pid)))
        else:
            print('[info] (%s) %s' % (time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),frpc_ini + '客户端配置文件不存在'))
            os._exit(0)
    else:
        print('[info] (%s) %s' % (time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),frpc_file + '客户端可执行程序不存在'))
        os._exit(0)

def Listen(frpc_file,frpc_ini):
    time.sleep(0.1)
    lastmd5 = ''
    while True:
        with open('mapping.conf','rb') as f:
            md5 = hashlib.md5(f.read()).hexdigest()

        with open('frps.ip','r') as f:
            myIpaddr = f.read()


        if lastmd5 != md5:
            print('[info] (%s) %s' % (time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),'配置文件发生变化，重新生成frpc.ini'))
            createnewconfig(myIpaddr)
            print('[info] (%s) %s' % (time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),' Reload frpc.ini and restart frpc service'))
            threading.Thread(target=worker,args=(frpc_file,frpc_ini)).start()
            lastmd5 = md5



        
