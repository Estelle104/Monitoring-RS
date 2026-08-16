# from scapy.all import ARP, Ether, srp

# def scan_network(network):
#     """
#     Retourne la liste des machines sur le réseau avec MAC et IP
#     """
#     arp = ARP(pdst=network)
#     ether = Ether(dst="ff:ff:ff:ff:ff:ff")
#     packet = ether / arp

#     result = srp(packet, timeout=2, verbose=0)[0]

#     clients = []
#     for sent, received in result:
#         clients.append({"ip": received.psrc, "mac": received.hwsrc})

#     return clients

import subprocess
import re

def scan_network(interface, network):
    """
    Retourne la liste des machines sur le réseau avec MAC et IP
    en utilisant arp-scan
    """
    result = subprocess.run(
        ["sudo", "arp-scan", f"--interface={interface}", network],
        capture_output=True,
        text=True
    )

    clients = []
    for line in result.stdout.splitlines():
        match = re.match(r'(\d+\.\d+\.\d+\.\d+)\s+([\w:]+)\s+(.*)', line)
        if match:
            clients.append({
                "ip": match.group(1),
                "mac": match.group(2),
                "vendor": match.group(3)
            })

    return clients


# # Utilisation
# if __name__ == "__main__":
#     machines = scan_network("wlo1", "172.30.1.0/24")
#     for m in machines:
#         print(f"IP: {m['ip']}  |  MAC: {m['mac']}  |  Fabricant: {m['vendor']}")
