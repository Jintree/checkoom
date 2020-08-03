# /usr/bin/python
#coding=utf-8
import json
import os
import sys
import commands
import requests
import time
reload(sys)
sys.setdefaultencoding('utf-8')

mtime1 = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def dingmessage(msg1):
# 请求的URL，WebHook地址
    webhook = "https://oapi.dingtalk.com/robot/send?access_token=eeee1a1337b74dcd544fe1639df657d4112b50be1114a0e4ecc3923b93ca265b&timestamp=1590545912412&sign=Epv%2FHBRDStNP8HN5GT43aGrNipyVTO308rNz0rUiw8w%3D"
#构建请求头部
    header = {
        "Content-Type": "application/json",
        "Charset": "UTF-8"
}
#构建请求数据
    tex = msg1
    message ={

        "msgtype": "text",
        "text": {
            "content": tex
        },
        "at": {

            "isAtAll": False
        }

    }
#对请求的数据进行json封装
    message_json = json.dumps(message)
#发送请求
    info = requests.post(url=webhook, data=message_json, headers=header)
#打印返回的结果
    #print(info.text)

def get_deploy_hostname():
    deployhostname = ''
    hostnamecmd = 'cat /etc/hostname'
    status, deployhostname = commands.getstatusoutput(hostnamecmd)
    return deployhostname

def get_jobserver_podname(keyword):
    getjobservernamecmd = "kubectl get pods|grep %s |awk '{print $1}'" % keyword
    status, jobservername = commands.getstatusoutput(getjobservernamecmd)
    return jobservername

def get_jobserver_podname1(keyword):
    getjobservernamecmd = "kubectl get pods|grep %s |grep -v spark-jobserver-etl|awk '{print $1}'" % keyword
    status, jobservername = commands.getstatusoutput(getjobservernamecmd)
    return jobservername

def restart_modulepod(hostname, podname):
    restartpodcmd = "kubectl delete pod %s -n default" % podname
    a = os.system(restartpodcmd)
    time.sleep(10)
    if a == 0:
        msg = "%s的pod名称为%s已重启，请知晓～" % (hostname, podname)
        print "%s restart at %s" % (podname, mtime1)
        #dingmessage(msg)
    else:
        print "%s restart failed at %s" % (podname, mtime1)

def discovery_updown_module(hostname, jobserverpodname):
    oomlogctcmd = 'kubectl logs --tail=35 %s|grep "OutOfMemoryError"|grep -v grep|wc -l' % jobserverpodname
    stoplogctcmd = 'kubectl logs --tail=35 %s|grep "Failed to allocate a page"|grep -v grep|wc -l' % jobserverpodname
    status, logctresult = commands.getstatusoutput(oomlogctcmd)
    status, stopctresult = commands.getstatusoutput(stoplogctcmd)
    if int(logctresult) == 0 and int(stopctresult) == 0:
         print "%s %s is ok" % (mtime1, hostname)
    else:
        msg = "检测到%s服务器的jobserver应用在%s出现oom或挂了，自动尝试进行重启pod操作" % (hostname, mtime1)
        #dingmessage(msg)
        restart_modulepod(hostname, jobserverpodname)

if __name__ =='__main__':
    hostname = get_deploy_hostname()
    jobserverkeyword = "spark-jobserver"
    jobserveretlkeyword = "spark-jobserver-etl"
    jobserverpodname = get_jobserver_podname1(jobserverkeyword)
    jobserveretlpodname = get_jobserver_podname(jobserveretlkeyword)
    if jobserverpodname != "":
        discovery_updown_module(hostname, jobserverpodname)
    elif jobserveretlpodname != "":
        discovery_updown_module(hostname, jobserveretlpodname)
    else:
        print "%s can't get jobserverpodname" % mtime1
