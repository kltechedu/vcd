from vcd_ops_mws import *
from xml.dom.minidom import parse, parseString
import time

secret = get_secret(os.getenv("VCD_USER"), os.getenv("VCD_PASS"))
delay = 60
t, o = vmware_token(secret)
vms = list_vms(t)

document = parseString(vms)
root = document.documentElement
vms_dict = {}
for el in root.getElementsByTagName("VMRecord"):
    if el.attributes.items()[0][1] != "guacamole":
        vms_dict[el.attributes.items()[0][1]] = el.attributes.items()[2][1]


if "router" in vms_dict.keys():
#    print("Starting router")
#    task_id = start_vm(t, vms_dict["router"])
#    if not task_id:
#        print("Failed to start router")
#    else:
#        status = get_task(t, task_id)
#        while status == "queued" or status == "running":
#            status = get_task(t, task_id)
#            if status == "success":
#                print("router started")
#            elif status == "error":
#                print("router failed to start")
#            time.sleep(1)
#            print(".", end="", flush=True)
    del vms_dict["router"]


if "dc" in vms_dict.keys():
    print("Starting dc")
    task_id = start_vm(t, vms_dict["dc"])
    if not task_id:
        print("Failed to start dc")
    else:
        status = get_task(t, task_id)
        while status == "queued" or status == "running":
            status = get_task(t, task_id)
            if status == "success":
                print("dc started")
            elif status == "error":
                print("dc failed to start")
            time.sleep(1)
            print(".", end="", flush=True)
        print("")
        print(f"Waiting {delay} sec to start other virtual machines")
        time.sleep(delay)
    del vms_dict["dc"]

for k in vms_dict.keys():
    task_id = start_vm(t, vms_dict[k])
    if not task_id:
        print(f"Failed to start {k}")
        continue
    status = get_task(t, task_id)
    while status == "queued" or status == "running":
        status = get_task(t, task_id)
        if status == "success":
            print(f"{k} started")
        elif status == "error":
            print(f"{k} failed to start")
        time.sleep(1)
        print(".", end="", flush=True)

print("")
print("You can now close this window")

destroy_session(t)
