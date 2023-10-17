#!/bin/python3

import argparse
from config import *
from tools import *


def make_setup() -> None:

    set_host_name(HOST_NAME)
    CURRENT_IP_ADDRESS = make_hosts(HOST_NAME)

    if CURRENT_IP_ADDRESS:
        make_netplan(CURRENT_IP_ADDRESS)
    else:
        raise RuntimeError

    run("apt-get update")
    run("apt-get upgrade -y")

    run("apt-get install neovim -y")
    run("apt-get install tcpdump -y")
    run("apt-get install netcat -y")
    run("apt-get install mininet -y")

    run("apt-get install python3-pip -y")
    run("pip install mininet")
    run("pip install scapy")

    run("systemctl enable --now systemd-resolved.service")
    run("systemctl enable --now systemd-networkd.service")
    run("sudo netplan apply")
    run("systemctl restart NetworkManager")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', help='host_name')
    parser.add_argument('--start-ip', help='IP-адрес')
    parser.add_argument('--vms', help='VMs')
    args = parser.parse_args()
    HOST_NAME = args.name if args.name else HOST_NAME
    START_IP_ADDRESS = args.start_ip if args.start_ip else START_IP_ADDRESS
    MAX_VMS = args.vms if args.vms else MAX_VMS
    make_setup()
