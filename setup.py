#!/bin/python3

import argparse
import subprocess
import os


START_IP_ADDRESS = "10.0.2.101"
HOST_NAME = "n001"
MAX_VMS = 2
CURRENT_IP_ADDRESS = None


def get_next_ip(ip: str) -> str:
    """
    Generator ip addresses. Starts with ip 'x.x.x.x', ends with ip 'x.x.x.255'

    :param ip: start ip address
    :type ip: str

    :yield: next ip address
    :ytype: str
    """

    yield ip
    d1, d2, d3, d4 = ip.split(".")
    d4 = int(d4)
    while d4 < 255:
        d4 += 1
        yield ".".join(map(str, [d1, d2, d3, d4]))


def run(command: str) -> None:
    """
    Run input command in shell

    :param command: command to run
    :type command: str
    """
    subprocess.run(command.split())


def make_hosts(HOST_NAME) -> None:
    if not os.path.exists("_hosts"):
        run(f"cp /etc/hosts _hosts")
    run("cp _hosts hosts")

    with open("hosts", "a") as hosts:
        hosts.write(f"\n127.0.0.1 {HOST_NAME}\n")

        for i, next_ip in enumerate(get_next_ip(START_IP_ADDRESS)):
            vm_name = "n" + "0" * (3 - len(str(i + 1))) + str(i + 1)

            if vm_name == HOST_NAME:
                CURRENT_IP_ADDRESS = next_ip

            hosts.write(f"{next_ip}    {vm_name}\n")

            if i == MAX_VMS:
                break

        hosts.write("10.0.2.201    ccnode\n")

    run("chmod 644 hosts")
    run("mv hosts /etc/")
    return CURRENT_IP_ADDRESS


def make_netplan(vm_ip: str):
    with open("/etc/netplan/config.yaml", "w") as netplan:
        netplan.write(
            "".join(
                [
                    "network:\n",
                    "  version: 2\n",
                    "  renderer: NetworkManager\n",
                    "  ethernets:\n",
                    "    enp0s8:\n",
                    "      dhcp4: no\n",
                    f"      addresses: [{vm_ip}/24]",
                ]
            )
        )
    run("chmod 644 /etc/netplan/config.yaml")


def set_host_name(HOST_NAME):
    run(f"echo {HOST_NAME} > /etc/hostname")


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
    parser.add_argument("--name", help="host_name")
    parser.add_argument("--start-ip", help="IP-адрес")
    parser.add_argument("--vms", help="VMs", type=int)
    args = parser.parse_args()
    HOST_NAME = args.name if args.name else HOST_NAME
    START_IP_ADDRESS = args.start_ip if args.start_ip else START_IP_ADDRESS
    MAX_VMS = args.vms if args.vms else MAX_VMS
    make_setup()
