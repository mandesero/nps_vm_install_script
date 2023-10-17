import subprocess
import os

from setup import HOST_NAME, START_IP_ADDRESS, MAX_VMS


def get_next_ip(ip: str) -> str:
    """
    Generator ip addresses. Starts with ip 'x.x.x.x', ends with ip 'x.x.x.255'

    :param ip: start ip address
    :type ip: str

    :yield: next ip address
    :ytype: str
    """

    yield ip
    d1, d2, d3, d4 = ip.split('.')
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
            vm_name = 'n' + '0' * (3 - len(str(i + 1))) + str(i + 1)

            if vm_name == HOST_NAME:
                CURRENT_IP_ADDRESS = next_ip

            hosts.write(f"{vm_name} {next_ip}\n")

            if i == MAX_VMS:
                break

    run("chmod 644 hosts")
    run("mv hosts /etc/")
    return CURRENT_IP_ADDRESS


def make_netplan(vm_ip: str):
    with open("/etc/netplan/config.yaml", "w") as netplan:
        netplan.write(
            "".join(
                [
                    'network:\n',
                    '  version: 2\n',
                    '  renderer: NetworkManager\n',
                    '  ethernets:\n',
                    '    enp0s8:\n',
                    '      dhcp4: no\n',
                    f'      addresses: [{vm_ip}/24]'
                ]
            )
        )
    run("chmod 644 /etc/netplan/config.yaml")

def set_host_name(HOST_NAME):
    run(f"echo {HOST_NAME} > /etc/hostname")
