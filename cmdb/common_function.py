# coding: UTF-8
import os,sys
import binascii
import time
import codecs
import subprocess
import re
from multiprocessing import Process,Pool
import xml.etree.ElementTree as ET
from selenium import webdriver

def create_iperf_client_and_return_bandwidth_out(s_ip,c_ip,port):
    recevier_result="get bandwidth failed"
    c_str = "iperf3 -c %s -p %s -i 1 -t 60 -B %s" %(s_ip,port,c_ip)
    print c_str
    try:
        subclient = subprocess.Popen(c_str,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
        #time.sleep(60)
        cmd_out = subclient.stdout.read()
        subclient.wait()
        print(cmd_out)
        cc=cmd_out.split("\n")
        recevier_result = re.findall(r'\d+.\d+ Mbits/sec',cc[-4:-3][0],flags=0)[0].split(' ')[0]
        subclient.kill()
    except:
        print("iperf3 failed")
    return recevier_result

class Portalfun:
    def __init__(self,func=None):
        self.f=func

    def str_convert_to_hex(self,str):
        e = 0   
        for i in str:
            d = ord(i)  
            e = e*256 + d
        return("%x" %e)
    
    def create_ssid_profile_xml_file(self,ssid,path):
        dirname=os.path.dirname(path)
        hex_ssid=self.str_convert_to_hex(ssid)
        ET.register_namespace('', "http://www.microsoft.com/networking/WLAN/profile/v1")
        tree = ET.parse(path)
        root = tree.getroot()
        for x in root.iter("{http://www.microsoft.com/networking/WLAN/profile/v1}name"):
            x.text=ssid
        for y in root.iter("{http://www.microsoft.com/networking/WLAN/profile/v1}hex"):
            y.text=hex_ssid
        ssid1= ssid.replace(':','-')
        tree.write(dirname+"\\"+ssid1+".xml", encoding='utf-8',xml_declaration=True)
        return dirname+"\\"+ssid1+".xml"

    def add_profile_and_connect_ssid(self,ssid,profilepath,interface):
        result= "connect_ssid_fail"
        b=0
        cmd_add="netsh wlan add profile filename=%s interface=%s" %(profilepath,interface)
        cmd_con="netsh wlan connect name=%s ssid=%s interface=%s" %(ssid,ssid,interface)
        os.popen(cmd_add)
        time.sleep(5)
        while result != True and b<5:
            res= os.popen(cmd_con).read()
            if res.decode('gbk').encode('utf-8') == "已成功完成连接请求。\n":
                result= True
            else:
                print "connect ssid failed %s" %(b)
                time.sleep(10)
                b=b+1
        return result
    
    def disconnect_ssid(self,interface):
        cmd_discon="netsh wlan disconnect interface=%s" %(interface)
        result= os.popen(cmd_discon)
        print result
        return result
    
    def open_portal_page_and_internet_check(self,username,password):
        url="http://money.163.com/"
        result=False
        browser = webdriver.Chrome()
        #browser = webdriver.Firefox()
        #browser = webdriver.Ie()
        #browser.get('http://www.baidu.com')
        #browser.get('http://10.6.161.252/no_proxy_sample/index.html')
        web1=False
        a=0
        while(web1 == False and a<5):
            try:
                browser.get("http://www.sina.com.cn")
                time.sleep(10)
                browser.find_element_by_id("username").send_keys(username)
                browser.find_element_by_id("password").send_keys(password)
                browser.find_element_by_name("Login").click()
                web1=True
                a=0
            except:
                web1=False
                a=a+1
        while(browser.current_url != url and a<5):
            time.sleep(5)
            a=a+1
            if a==5:
                print "%%%%%%%%%%%%%%%%%%%%%%%open checkpage timeout!%%%%%%%%%%%%%%%%%%%%%%%%%%%%%5"
        a=0
        handlenow=browser.current_window_handle
        newwindow='window.open("http://www.baidu.com")'
        while(result==False and a<3):
            try:
                browser.execute_script(newwindow)
                handles = browser.window_handles
                for i in handles:
                    if i != handlenow:
                        browser.switch_to_window(i)
                        #print browser.current_url
                        a=browser.find_element_by_id("su").click()
                        result = True
                        break
            except:
                result=False
                time.sleep(10)
                a=a+1
                print "%%%%%%%%%%%%%%%%%%%%%%%%%%not find element su%%%%%%%%%%%%%%%%%%%%%%%%"
        browser.close()
        browser.quit()
        return result

    def ping_server(self,dstserver):
        result = False
        a=0
        while result==False and a<2:
            cmd_ping = 'ping '+dstserver
            output= os.popen(cmd_ping).read()
            print output
            if 'TTL=' in output:
                result= True
            a=a+1
            time.sleep(5)
        return result

    def set_pc_acquire_ip_type_dhcp(self,interface):
        cmd="netsh interface ipv4 set address name=%s source=dhcp" %(interface)
        result=os.popen(cmd).read()
        return True

    def set_pc_static_ip_and_gateway(self,interface,ip,mask,gateway):
        cmd="netsh interface ipv4 set address name=%s source=static addr=%s mask=%s gateway=%s" %(interface,ip,mask,gateway)
        print cmd
        result=os.popen(cmd).read()
        return True

    def create_iperf_server(slef,s_ip,port):
        s_str = "iperf3 -s -p %s -i 1 -B %s" %(port,s_ip)
        print s_str
        subserver = subprocess.Popen(s_str,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
        time.sleep(3)
        return True

    def create_iperf_client_and_return_bandwidth(self,s_ip,c_ip,port):
        recevier_result="get bandwidth failed"
        c_str = "iperf3 -c %s -p %s -i 1 -t 60 -B %s" %(s_ip,port,c_ip)
        print c_str
        try:
            subclient = subprocess.Popen(c_str,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
            #time.sleep(60)
            cmd_out = subclient.stdout.read()
            subclient.wait()
            print(cmd_out)
            cc=cmd_out.split("\n")
            recevier_result = re.findall(r'\d+.\d+ Mbits/sec',cc[-4:-3][0],flags=0)[0].split(' ')[0]
            subclient.kill()
        except:
            print("iperf3 failed")
        return recevier_result

    def create_multi_iperf_client(self,dip1,sip1,p1,dip2,sip2,p2):
        result=[]
        myresult=[]
        if __name__=="cmdb.common_function":
            pool=Pool(processes=2)
            result.append(pool.apply_async(self.f,(dip1,sip1,p1,)))
            result.append(pool.apply_async(self.f,(dip2,sip2,p2,)))
            pool.close()
            pool.join()
            for i in result:
                myresult.append(i.get())
        return myresult

    def kill_alliperf3_task(self):
        findtask = "tasklist | findstr iperf3"
        killtask = "taskkill /pid "
        iperftask = os.popen(findtask).read()
        alliperf3=re.findall(r'iperf3.exe\s+\d+',iperftask,flags=0)
        for i in alliperf3:
            m=re.split(r'\s+',i)
            killtask = "taskkill /pid " + m[1] + " /F"
            os.popen(killtask)
        return True

    def open_page(self,domain,title):
        dst_d = "http://%s" %(domain)
        browser = webdriver.Chrome()
        result=False
        try:
            cmd_ping = 'ping '+domain
            output= os.popen(cmd_ping).read()
            browser.get(dst_d)
            time.sleep(10)
            if title==browser.title:
                result=True
            else:
                result=False
        finally:
            browser.close()
            browser.quit()
        return result

if  __name__ == '__main__':
    Portalfun()