import os,sys
from django.shortcuts import HttpResponse
from django.shortcuts import render,render_to_response
from django.http import JsonResponse
from django.views.decorators import csrf
from django.views.decorators.csrf import csrf_exempt,csrf_protect
from selenium import webdriver
from multiprocessing import Process,Pool
import json
import simplejson
import common_function
from common_function import Portalfun
import time
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#browser = webdriver.Chrome()
# Create your views here.
@csrf_exempt
def index(request):
    print 'now  in index method'
    return HttpResponse("THIS IN CMDB")

def htmlpage(request):

    #render  return a html page
    return render(request,"cmdb-html.html")

@csrf_exempt
def portal_vlan_connect(request):
    result = '0'
    print 'now in function portal_vlan_connect'
    profilepath = os.path.join(BASE_DIR,'static\\base_open_profile.xml')
    if request.method == 'POST':
        received_json_data = json.loads(request.body)
        #received_json_data = simplejson.loads(request.raw_post_data)
        p=Portalfun()
        ssid_profilepath=p.create_ssid_profile_xml_file(received_json_data['ssid'],profilepath)
        time.sleep(2)
        connect_result=p.add_profile_and_connect_ssid(received_json_data['ssid'],ssid_profilepath,received_json_data['interface'])
        if connect_result !=True:
            result = connect_result
        else:
            time.sleep(2)
            p.set_pc_acquire_ip_type_dhcp(received_json_data['interface'])
            time.sleep(5)
            result = p.open_portal_page_and_internet_check(received_json_data['puser'],received_json_data['ppass'])
    return HttpResponse(result)

@csrf_exempt
def server_connect_ssid_and_set_ip(request):
    print "now in server_connect_ssid_and_set_ip"
    profilepath = os.path.join(BASE_DIR,'static\\base_open_profile.xml')
    result=False
    if request.method == 'POST':
        received_json_data = json.loads(request.body)
        p=Portalfun()
        ssid_profilepath=p.create_ssid_profile_xml_file(received_json_data['ssid'],profilepath)
        time.sleep(2)
        connect_result=p.add_profile_and_connect_ssid(received_json_data['ssid'],ssid_profilepath,received_json_data['interface'])        
        if connect_result==True :
            time.sleep(5)
            print "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
            print received_json_data['source']
            if received_json_data['source']=='dhcp':
                print "ddddddddddddhhhhhhhhhhhhhhhcccccccc"
                p.set_pc_acquire_ip_type_dhcp(received_json_data['interface'])
                result=True
            elif received_json_data['source']=='static':
                print "wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww"
                interface=received_json_data['interface']
                ip=received_json_data['staticip']
                mask=received_json_data['mask']
                gateway=received_json_data['gateway']
                p.set_pc_static_ip_and_gateway(interface,ip,mask,gateway)
                result=True
    return HttpResponse(result)

@csrf_exempt
def recover_interface_dhcp(request):
    print "recover_interface_dhcp"
    if request.method == 'POST':
        received_json_data = json.loads(request.body)
        p=Portalfun()
        p.set_pc_acquire_ip_type_dhcp(received_json_data['interface'])
        result=True
    return HttpResponse(result)

@csrf_exempt
def ping_dstserver(request):
    result='mm'
    if request.method == 'POST':
        received_json_data = json.loads(request.body)
        p=Portalfun()
        result = p.ping_server(received_json_data["dstserver"])
    return HttpResponse(result)

@csrf_exempt
def bandwidth_test_both_wireless(request):
    profilepath = os.path.join(BASE_DIR,'static\\base_open_profile.xml')
    bandwidth='bandwidth'
    received_json_data = json.loads(request.body)
    serverinterface = received_json_data["serverinterface"]
    clientinterface = received_json_data["clientinterface"]
    serverssid = received_json_data["serverssid"]
    clientssid = received_json_data["clientssid"]
    serverip="192.168.11.10"
    clientip="192.168.11.20"
    gateway="192.168.11.1"
    iperfport="1234"
    ps=Portalfun()
    sprofpath=ps.create_ssid_profile_xml_file(serverssid,profilepath)
    time.sleep(1)
    ps.add_profile_and_connect_ssid(serverssid,sprofpath,serverinterface)
    ps.set_pc_static_ip_and_gateway(serverinterface,serverip,"255.255.255.0",gateway)
    cprofpath=ps.create_ssid_profile_xml_file(clientssid,profilepath)
    time.sleep(1)
    ps.add_profile_and_connect_ssid(clientssid,cprofpath,clientinterface)
    ps.set_pc_static_ip_and_gateway(clientinterface,clientip,"255.255.255.0",gateway)
    time.sleep(1)
    ps.create_iperf_server(serverip,iperfport)
    time.sleep(2)
    bandwidth=ps.create_iperf_client_and_return_bandwidth(clientip,serverip,iperfport)
    ps.kill_alliperf3_task()
    ps.set_pc_acquire_ip_type_dhcp(serverinterface)
    ps.set_pc_acquire_ip_type_dhcp(clientinterface)
    return HttpResponse(bandwidth)

@csrf_exempt
def bandwidth_test_local_wireless(request):
    profilepath = os.path.join(BASE_DIR,'static\\base_open_profile.xml')
    bandwidth={'flow1':'flow1','flow2':'flow2'}
    received_json_data = json.loads(request.body)
    winterface = received_json_data["winterface1"]
    ssid = received_json_data["ssid1"]
    iperfserver = received_json_data["iperfserver"]  #local or wireless
    wiredip = received_json_data["wiredip"]
    winterface2 = received_json_data["winterface2"]
    ssid2 = received_json_data["ssid2"]
    wlanip="192.168.99.8"
    gateway="192.168.99.1"
    port1="1234"
    port2="5678"
    ps=Portalfun()
    sprofpath=ps.create_ssid_profile_xml_file(ssid,profilepath)
    time.sleep(1)
    ps.add_profile_and_connect_ssid(ssid,sprofpath,winterface)
    ps.set_pc_static_ip_and_gateway(winterface,wlanip,"255.255.255.0",gateway)
    time.sleep(1)
    if winterface2 == "default":
        if iperfserver == "wired":
            ps.create_iperf_server(wiredip,port1)
            bandwidth['flow1']=ps.create_iperf_client_and_return_bandwidth(wlanip,wiredip,port1)
        else:
            ps.create_iperf_server(wlanip,port1)
            bandwidth['flow1']=ps.create_iperf_client_and_return_bandwidth(wiredip,wlanip,port1)
    else:
        if iperfserver == "wired":
            ps.create_iperf_server(wiredip,port1)
            ps.create_iperf_server(wiredip,port2)
            bandwidth['flow1']=ps.create_iperf_client_and_return_bandwidth(wlanip,wiredip,port1)
        else:
            ps.create_iperf_server(wlanip,port1)
            bandwidth['flow1']=ps.create_iperf_client_and_return_bandwidth(wiredip,wlanip,port1)

    ps.kill_alliperf3_task()
    ps.set_pc_acquire_ip_type_dhcp(winterface)
    return HttpResponse(bandwidth)

@csrf_exempt
def bandwidth_test_local_wireless_test(request):
    profilepath = os.path.join(BASE_DIR,'static\\base_open_profile.xml')
    bandwidth=[]
    flowresult={}
    received_json_data = json.loads(request.body)
    gateway="192.168.99.1"
    port="1234"
    ps=Portalfun(common_function.create_iperf_client_and_return_bandwidth_out)
    clients=[]
    servers=[]
    try:
        for i in received_json_data["dictdata"]:
            interface = i["interface"]
            ssid = i["ssid"]
            ip = i["ip"]
            iswired = i["iswired"]
            isserver = i["isserver"]
            if iswired==False:
                sprofpath=ps.create_ssid_profile_xml_file(ssid,profilepath)
                time.sleep(1)
                ps.add_profile_and_connect_ssid(ssid,sprofpath,interface)
                time.sleep(2)
                ps.set_pc_static_ip_and_gateway(interface,ip,"255.255.255.0",gateway)
                time.sleep(5)
        for i in received_json_data["dictdata"]:
            interface = i["interface"]
            ssid = i["ssid"]
            ip = i["ip"]
            iswired = i["iswired"]
            isserver = i["isserver"]
            flow = i["flow"]
            if isserver==True:
                ps.create_iperf_server(ip,port+flow)
                servers.append(i)
            else:
                clients.append(i)
        if len(clients) ==1:
            for i in received_json_data["dictdata"]:
                if i["isserver"]==True:
                    bandwidth.append(ps.create_iperf_client_and_return_bandwidth(i["ip"],clients[0]["ip"],port+clients[0]["flow"]))
            flowresult[clients[0]["flow"]]=bandwidth[0]
        else:
            if servers[0]["flow"] == clients[0]["flow"]:
                pass
            else:
                clients.reverse()
            bandwidth=ps.create_multi_iperf_client(servers[0]["ip"],clients[0]["ip"],port+clients[0]["flow"],servers[1]["ip"],clients[1]["ip"],port+clients[1]["flow"])
            flowresult[clients[0]["flow"]]=bandwidth[0]
            flowresult[clients[1]["flow"]]=bandwidth[1]
        ps.kill_alliperf3_task()
    finally:
        for i in received_json_data["dictdata"]:
            if i["interface"] != None:
                print "recover interface %s" %(i["interface"])
                ps.set_pc_acquire_ip_type_dhcp(i["interface"])
                ps.disconnect_ssid(i["interface"])
    return HttpResponse(simplejson.dumps(flowresult, ensure_ascii=False))

@csrf_exempt
def pc_open_page(request):
    result=False
    if request.method == 'POST':
        received_json_data = json.loads(request.body)
        ps=Portalfun()
        result=ps.open_page(received_json_data["domain"],received_json_data["title"])
    return HttpResponse(result)

@csrf_exempt
def search_post(request):
    ctx={}
    if request.method == 'POST':
        ctx['rlt'] = request.POST['q']
        print simplejson.loads(request.raw_post_data)
    return render(request,"post.html",ctx)



def autolog(request):
    #ctx={}
    #if request.method == 'POST':
    #    ctx['rlt'] = request.POST['q']
    #    print simplejson.loads(request.raw_post_data)
    return render(request,"hello.html")

def test(request):
    #ctx={}
    #if request.method == 'POST':
    #    ctx['rlt'] = request.POST['q']
    #    print simplejson.loads(request.raw_post_data)
    return render(request,"test.html")