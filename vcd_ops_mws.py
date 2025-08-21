#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
import base64
import json
import urllib3
from requests import Request, Session
import subprocess
import time
import os
from xml.dom.minidom import parse, parseString
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
vcd_server = "https://iaas-gb.cloud.mts.ru/api/"


headers = {
    'User-Agent': 'Python 3.12',
    'Accept': 'application/*;version=38.1',
}

def get_secret(user, passwd):
    usrpw = user + "@Kaspersky_Lab_GB:" + passwd
    return base64.b64encode(usrpw.encode("utf-8")).decode("utf-8")

def to_mime_base64(string):
    inputBytes = bytes(string, "UTF-8")
    return base64.encodebytes(inputBytes)

def _get_org(headers_dict):
    links = headers_dict['Link']
    found = False
    for l in links.split(','):
        for ll in l.split(';'):
            if 'cloudapi/1.0.0/orgs' in ll:
                found = True
            if found and 'title' in ll:
                t, urn = ll.split("=")
                urn_stripped = urn.replace('"','')
                return urn_stripped.split(":")[3]

def vmware_token(auth):
    url = "https://iaas-gb.cloud.mts.ru/cloudapi/1.0.0/sessions"
    headers_init = {
        'User-Agent': 'Python 3.11',
        'Accept': 'application/*;version=38.1',
        'Authorization': 'Basic {auth}'.format(auth=auth),
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    r = requests.post(url, headers=headers_init, data='', verify=False)
    token = r.headers['X-VMWARE-VCLOUD-ACCESS-TOKEN']
    org = _get_org(r.headers)
    return (token, org)

def destroy_session(vmw_token):
    url = "https://iaas-gb.cloud.mts.ru/cloudapi/1.0.0/sessions"
    headers['Authorization'] = 'Bearer {token}'.format(token=vmw_token)
    r = requests.delete(url, headers=headers, data='', verify=False)

def get_vcd_objects(vmw_token):
    url = vcd_server + "query"
    headers['Authorization'] = 'Bearer {token}'.format(token=vmw_token)
    payload = {'type': 'orgVdc'}
    response = requests.get(url=url, headers=headers, params=payload, verify=False)
    return response.text

def get_org_objects(vmw_token, org_id):
    url = vcd_server + "org/" + org_id
    headers['Authorization'] = 'Bearer {token}'.format(token=vmw_token)
    response = requests.get(url=url, headers=headers, verify=False)
    print(response.text)

def get_org_catalogs(vmw_token, org_id):
    url = vcd_server + "query?type=catalog"
    headers['Authorization'] = 'Bearer {token}'.format(token=vmw_token)
    response = requests.get(url=url, headers=headers, verify=False)
    return response.text

def get_org_vdc(vmw_token, org_id):
    url = vcd_server + "query?type=orgVdc"
    headers['Authorization'] = 'Bearer {token}'.format(token=vmw_token)
    response = requests.get(url=url, headers=headers, verify=False)
    return response.text

def vdc_admin_view(vmw_token, org_id):
    url = vcd_server + 'admin'
    headers['Authorization'] = 'Bearer {token}'.format(token=vmw_token)
    response = requests.get(url=url, headers=headers, verify=False)
    return response.text

def vdc_info(vmw_token, vdc_uid = '0d49abf4-96ae-4e37-96f7-e22832aff54e'):
    url = vcd_server + 'vdc/' + vdc_uid
    headers['Authorization'] = 'Bearer {token}'.format(token=vmw_token)
    response = requests.get(url=url, headers=headers, verify=False)
    return response.text

def get_vapp_networks(vmw_token):
    url = vcd_server + "query?type=vAppNetwork"
    headers['Authorization'] = 'Bearer {token}'.format(token=vmw_token)
    response = requests.get(url=url, headers=headers, verify=False)
    return response.text

def get_vapps(vmw_token, org_id):
    url = vcd_server + "query?type=vApps"
    headers['Authorization'] = 'Bearer {token}'.format(token=vmw_token)
    response = requests.get(url=url, headers=headers, verify=False)
    return response.text

def get_catalog_contents(vmw_token, catalog = ''):
    url = vcd_server + 'catalog/' + catalog
    headers['Authorization'] = 'Bearer {token}'.format(token=vmw_token)
    response = requests.get(url=url, headers=headers, verify=False)
    return response.text

def get_task(vmw_token, task_id):
    url = vcd_server + 'task/' + task_id
    headers['Authorization'] = 'Bearer {token}'.format(token=vmw_token)
    r = requests.get(url=url, headers=headers, verify=False)
    document = parseString(r.text)
    root = document.documentElement
    for el in root.attributes.items():
        if el[0] == "status":
            return el[1]

def get_vm(vmw_token, vm_id):
    url = vcd_server + 'vApp/' + vm_id
    headers['Authorization'] = 'Bearer {token}'.format(token=vmw_token)
    r = requests.get(url=url, headers=headers, verify=False)
    print(r.text)

def start_vm(vmw_token, vm_url):
    url = vm_url + "/power/action/powerOn"
    headers['Authorization'] = 'Bearer {token}'.format(token=vmw_token)
    r = requests.post(url, headers=headers, data='', verify=False)
    document = parseString(r.text)
    root = document.documentElement
    for el in root.attributes.items():
        if el[0] == "id":
            return el[1].split(":")[3]

def stop_vm(vmw_token, vm_url):
    url = vm_url + "/power/action/poweroff"
    headers['Authorization'] = 'Bearer {token}'.format(token=vmw_token)
    r = requests.post(url, headers=headers, data='', verify=False)
    document = parseString(r.text)
    root = document.documentElement
    for el in root.attributes.items():
        if el[0] == "id":
            return el[1].split(":")[3]

def shutdown_vm(vmw_token, vm_url):
    url = vm_url + "/power/action/shutdown"
    headers['Authorization'] = 'Bearer {token}'.format(token=vmw_token)
    r = requests.post(url, headers=headers, data='', verify=False)
    document = parseString(r.text)
    root = document.documentElement
    for el in root.attributes.items():
        if el[0] == "id":
            return el[1].split(":")[3]

def list_vms(vmw_token):
    url = vcd_server + "query?type=vm&fields=name,containerName&filter=isVAppTemplate==false"
    headers['Authorization'] = 'Bearer {token}'.format(token=vmw_token)
    response = requests.get(url=url, headers=headers, verify=False)
    return response.text

def ovf_upload_url(vmw_token, vdc, ovf_xml):
    url = vcd_server + 'vdc/' + vdc + '/action/instantiateOvf'
    headers['Authorization'] = 'Bearer {token}'.format(token=vmw_token)
    headers['Content-Type'] = 'application/vnd.vmware.vcloud.instantiateOvfParams+xml'
    with open(ovf_xml, 'rb') as xml:
        payload = xml.read()
    r = requests.post(url, headers=headers, data=payload, verify=False)
    if r.text:
        dic = {}
        document = parseString(r.text)
        root = document.documentElement
        for el in root.getElementsByTagName("Task"):
            for el in root.getElementsByTagName("Task"):
                dic['tasklink'] = el.attributes.items()[9][1]
        for el in root.getElementsByTagName("Link"):
            if (el.attributes.items()[0][1]) == 'upload:default':
                dic['ovflink'] = el.attributes.items()[1][1]
                dic['vapplink'] = root.attributes.items()[14][1]
                return dic

def instantiateOvf(vmw_token, org_id, ovf_xml):
    url = vcd_server + 'vdc/' + org_id + '/action/instantiateOvf'
    headers['Authorization'] = 'Bearer {token}'.format(token=vmw_token)
    headers['Content-Type'] = 'application/vnd.vmware.vcloud.instantiateOvfParams+xml'
    with open(ovf_xml) as xml:
        payload = xml.read()
    r = requests.post(url, headers=headers_init, data=payload, verify=False)

def upload_ovf(vmw_token, ovf_desc, ovf_url):
    headers['Content-Type'] = 'text/xml'
    with open(ovf_desc, 'rb') as xml:
        payload = xml.read()
    print(ovf_url)
    r = requests.put(ovf_url, headers=headers, data=payload, verify=False)
    print(r.text)
    print(r.status_code)

def upload_vmdk(vmw_token, vmdk, vmdk_url, vmdk_size):
    headers['Content-Type'] = 'text/xml'
    headers['Content-length'] = vmdk_size
    print(vmdk_url)
    with open(vmdk, 'rb') as f:
        r = requests.put(vmdk_url, headers=headers, data=f, verify=False)
    print(r.text)
    print(r.status_code)

def vmdk_link(vmw_token, vapplink):
    headers['Authorization'] = 'Bearer {token}'.format(token=vmw_token)
    response = requests.get(url=vapplink, headers=headers, verify=False)
    if response.text:
        print(response.text)
        dic = {}
        document = parseString(response.text)
        root = document.documentElement
        for el in root.getElementsByTagName("File"):
            if el.attributes.items()[2][1][-4:] == 'vmdk':
                dic['vmdk'] = el.attributes.items()[2][1]
                dic['size'] = el.attributes.items()[0][1]
        for el in root.getElementsByTagName("Link"):
            if dic['vmdk'] in el.attributes.items()[1][1]:
                dic['vmdklink'] = el.attributes.items()[1][1]
                return dic
