from vcd_ops_mws import *
from xml.dom.minidom import parse, parseString
import time

secret = get_secret(os.getenv("VCD_USER"), os.getenv("VCD_PASS"))
delay = 60
t, o = vmware_token(secret)
vms = list_vms(t)

print("Stopping all virtual machines")
document = parseString(vms)
root = document.documentElement
for el in root.getElementsByTagName("VMRecord"):
    vm_name = el.attributes.items()[0][1] 
    if vm_name != "guacamole":
        task_id = shutdown_vm(t,el.attributes.items()[2][1])
        if not task_id:
            print(f"Failed to stop {vm_name}")
            continue
            
        status = get_task(t, task_id)
        while status == "queued" or status == "running":
            status = get_task(t, task_id)
            if status == "success":
                print(f"{vm_name} stopped")
            elif status == "error":
                task_id2 = stop_vm(t,el.attributes.items()[2][1])
                status = get_task(t, task_id2)
                while status == "queued" or status == "running":
                    status = get_task(t, task_id2)
                    if status == "success":
                        print(f"{vm_name} stopped")
                    elif status == "error":
                        print("{vm_name} failed to stop")
                    time.sleep(1)
                    print(".", end="")
            time.sleep(1)
            print(".", end="", flush=True)

print("")
print("You can now close this window")

destroy_session(t)
