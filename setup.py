#!/bin/python3

import sys

START_IP_ADDRESS = "10.0.2.101"
NAME = "n001"
MAX_VMS = None
# HOSTS_FILE_PATH = "/etc/hosts"
HOSTS_FILE_PATH = "out"

def make_hosts() -> None:
    """
    127.0.0.1	n001
    10.0.2.101	n001 
    10.0.2.102	n002
    10.0.2.201	ccnode
    """
    with open(HOSTS_FILE_PATH, "+a") as hosts:
        hosts.write(f"127.0.0.1 {NAME}\n")
        parts = START_IP_ADDRESS.split('.')
        for i in range(1, MAX_VMS + 1):
            vm_ip = '.'.join(parts)
            vm_name = 'n' + '0' * (3 - len(str(i))) + str(i)
            hosts.write(f"{vm_ip} {vm_name}\n")
            parts[-1] = str(int(parts[-1]) + 1)


def make_setup() -> None:
    parts = START_IP_ADDRESS.split('.')
    parts[-1] = str(int(parts[-1]) + int(NAME[-3:]))
    vm_ip = '.'.join(parts)
    make_hosts()
    


if __name__ == "__main__":
    match len(sys.argv):
        case 3:
            if sys.argv[1] == '--name':
                NAME = sys.argv[2]
            elif sys.argv[1] == "--start-ip":
                START_IP_ADDRESS = sys.argv[2]
        case 5:
            params = {
                sys.argv[1]: sys.argv[2],
                sys.argv[3]: sys.argv[4],
            }
            NAME = params['--name']
            START_IP_ADDRESS = params['--start-ip']
    MAX_VMS = 255 - int(START_IP_ADDRESS.split('.')[-1]) + 1
    make_setup()
