#!/bin/python3

import argparse
import subprocess
from fnmatch import fnmatch


def run(command: str) -> None:
    """
    Run input command in shell

    :param command: command to run
    :type command: str
    """
    subprocess.run(command.split())


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


def is_correct_ip(ip):
    try:
        return all(d in range(0, 256) for d in map(int, ip.split(".")))
    except:
        return False


def set_host_name():
    run(f"echo {VM_NAME} > /etc/hostname")


def make_hosts() -> None:
    with open("/etc/hosts", "w") as hosts:
        hosts.write(
            "127.0.0.1 localhost\n"
            + "127.0.1.1 nps-server\n"
            + "::1     ip6-localhost ip6-loopback\n"
            + "fe00::0 ip6-localnet\n"
            + "ff00::0 ip6-mcastprefix\n"
            + "ff02::1 ip6-allnodes\n"
            + "ff02::2 ip6-allrouters\n\n"
        )

        hosts.write(f"\n127.0.0.1 {VM_NAME}\n")

        for i, next_ip in enumerate(get_next_ip(START_IP)):
            if i == VMS:
                break

            vm_name = "n" + "0" * (3 - len(str(i + 1))) + str(i + 1)
            hosts.write(f"{next_ip} {vm_name}\n")

        hosts.write("10.0.2.201 ccnode\n")


def configure_net():
    run("sudo ip link set enp0s8 up")
    run(f"sudo ip addr add dev enp0s8 {VM_IP}/24")


def main():
    set_host_name()
    make_hosts()
    configure_net()

    run("apt-get update")
    run("apt-get upgrade -y")

    run("apt-get install neovim -y")
    run("apt-get install tcpdump -y")
    run("apt-get install netcat -y")
    run("apt-get install mininet -y")

    run("apt-get install python3-pip -y")
    run("pip install mininet")
    run("pip install scapy")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", type=str)
    parser.add_argument("--start", type=str)
    parser.add_argument("--vms", type=int)
    parser.add_argument("--net", type=str, default="no")
    args = parser.parse_args()

    if any(val is None for _, val in args._get_kwargs()):
        raise RuntimeError(
            "Не указаны все параметры (--name <name> --start <ip> --vms <number of clusters>)."
        )

    VM_NAME = args.name
    if not fnmatch(VM_NAME, "n[0-9][0-9][0-9]"):
        raise RuntimeError(
            "Неправильно указано имя машины (Правильное имя: n???, где ? - цифра)."
        )

    START_IP = args.start
    if not is_correct_ip(START_IP):
        raise RuntimeError("Неправильно указан ip адресс первой машины.")

    VMS = args.vms
    VM_IP = list(get_next_ip(START_IP))[int(VM_NAME[-3:]) - 1]

    if args.net.lower() == "yes":
        configure_net()
        exit(0)
    main()
