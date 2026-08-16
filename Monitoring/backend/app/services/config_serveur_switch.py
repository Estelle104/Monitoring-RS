import paramiko
import time


def get_switch_ports(switch_ip="173.16.1.4",
                     username="cisco",
                     password="cisco1234!"):
    """Récupérer tous les ports disponibles du switch avec leur statut"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(switch_ip, username=username, password=password, timeout=10)

    stdin, stdout, stderr = ssh.exec_command("show interfaces status")
    output = stdout.read().decode()

    ssh.close()

    ports = []
    for line in output.splitlines():
        parts = line.split()
        if len(parts) >= 2:
            port_name = parts[0]
            # Filtrer les ports valides (Fa, Gi, etc.)
            if any(port_name.startswith(p) for p in ['Fa', 'Gi', 'Te', 'gi', 'fa']):
                status = "connected" if "connected" in line else "notconnect" if "notconnect" in line else "disabled"
                vlan_info = "trunk" if "trunk" in line.lower() else ""
                # Chercher le VLAN si disponible
                for part in parts:
                    if part.isdigit() and int(part) < 4095:
                        vlan_info = part
                        break
                ports.append({
                    "name": port_name,
                    "status": status,
                    "vlan": vlan_info,
                    "available": status == "notconnect"
                })

    return ports


def get_free_interfaces(switch_ip="173.16.1.4",
                        username="cisco",
                        password="cisco1234!"):
    """Récupérer les ports non connectés (libres) du switch"""
    ports = get_switch_ports(switch_ip, username, password)
    return [p["name"] for p in ports if p["available"]]


def allow_vlan_on_trunk(vlan_id, trunk_interface="gi1/0/1",
                       switch_ip="173.16.1.4",
                       username="cisco",
                       password="cisco1234!"):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(switch_ip, username=username, password=password)

    shell = ssh.invoke_shell()
    time.sleep(1)

    commands = [
        "enable",
        "configure terminal",
        f"interface {trunk_interface}",
        "switchport mode trunk",
        f"switchport trunk allowed vlan add {vlan_id}",
        "end",
        "write memory"
    ]

    for cmd in commands:
        shell.send(cmd + "\n")
        time.sleep(1)

    ssh.close()


def assign_port_to_vlan(interface, vlan_id,
                        switch_ip="173.16.1.4",
                        username="cisco",
                        password="cisco1234!"):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(switch_ip, username=username, password=password)

    shell = ssh.invoke_shell()
    time.sleep(1)

    commands = [
        "enable",
        "configure terminal",
        f"interface {interface}",
        "switchport mode access",
        f"switchport access vlan {vlan_id}",
        "no shutdown",
        "end",
        "write memory"
    ]

    for cmd in commands:
        shell.send(cmd + "\n")
        time.sleep(1)

    ssh.close()
    return 0

def get_port_pair(interface):
    """Retourne la paire haut+bas alignée physiquement (offset de 12)"""
    prefix = interface.rsplit("/", 1)[0]   # "gi1/0"
    port_num = int(interface.rsplit("/", 1)[1])

    if port_num <= 12:
        return [interface, f"{prefix}/{port_num + 12}"]
    else:
        return [f"{prefix}/{port_num -12 }", interface]


# def create_vlan_switch_A(vlan_config,
#                          switch_ip="173.16.1.4",
#                          username="cisco",
#                          password="cisco1234!",
#                          interface="gi1/0/4",
#                          interface2="gi1/0/5"
#                          ):

#     vlan_id = vlan_config["vlan_id"]
#     vlan_name = f"VLAN{vlan_id}"
#     ip_switch = vlan_config["ip_switch"]
#     masque = vlan_config["masque"]

#     print(f"🚀 Création VLAN {vlan_id}")

#     # 🔹 Création VLAN
#     ssh = paramiko.SSHClient()
#     ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#     ssh.connect(switch_ip, username=username, password=password)

#     shell = ssh.invoke_shell()
#     time.sleep(1)

#     commands = [
#         "enable",
#         "configure terminal",
#         f"vlan {vlan_id}",
#         f"name {vlan_name}",
#         "end",
#         "write memory"
#     ]

#     for cmd in commands:
#         shell.send(cmd + "\n")
#         time.sleep(1)

#     ssh.close()

#     print("✅ VLAN créé")

#     # 🔹 Allow sur trunk
#     allow_vlan_on_trunk(vlan_id, "gi1/0/1", switch_ip, username, password)
#     print("✅ VLAN autorisé sur trunk")

#     # 🔹 Port accessffffffff
#     a = assign_port_to_vlan(interface, vlan_id, switch_ip, username, password)
#     if a == 0:
#         assign_port_to_vlan(interface2, vlan_id, switch_ip, username, password)
#     print(f"✅ Port {interface} assigné")
#     print(f"✅ Port {interface2} assigné")

#     # 🔹 Interface VLAN IP
#     ssh = paramiko.SSHClient()
#     ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#     ssh.connect(switch_ip, username=username, password=password)

#     shell = ssh.invoke_shell()
#     time.sleep(1)

#     commands = [
#         "enable",
#         "configure terminal",
#         f"interface vlan {vlan_id}",
#         f"ip address {ip_switch} {masque}",
#         "no shutdown",
#         "end",
#         "write memory"
#     ]

#     for cmd in commands:
#         shell.send(cmd + "\n")
#         time.sleep(1)

#     ssh.close()

#     print("✅ Interface VLAN configurée")

#     return f"VLAN {vlan_id} prêt"


def create_vlan_switch_A(vlan_config,
                         switch_ip="173.16.1.4",
                         username="cisco",
                         password="cisco1234!",
                         interface="gi1/0/4"):

    vlan_id = vlan_config["vlan_id"]
    vlan_name = f"VLAN{vlan_id}"
    ip_switch = vlan_config["ip_switch"]
    masque = vlan_config["masque"]

    # 🔹 Calcul automatique de la paire
    interfaces = get_port_pair(interface)
    print(f"🚀 Création VLAN {vlan_id} sur ports {interfaces[0]} et {interfaces[1]}")

    # 🔹 Création VLAN
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(switch_ip, username=username, password=password)
    shell = ssh.invoke_shell()
    time.sleep(1)

    commands = [
        "enable",
        "configure terminal",
        f"vlan {vlan_id}",
        f"name {vlan_name}",
        "end",
        "write memory"
    ]
    for cmd in commands:
        shell.send(cmd + "\n")
        time.sleep(1)
    ssh.close()
    print("✅ VLAN créé")

    # 🔹 Allow sur trunk
    allow_vlan_on_trunk(vlan_id, "gi1/0/1", switch_ip, username, password)
    print("✅ VLAN autorisé sur trunk")

    # 🔹 Assigner les 2 ports alignés au VLAN
    for iface in interfaces:
        assign_port_to_vlan(iface, vlan_id, switch_ip, username, password)
        print(f"✅ Port {iface} assigné au VLAN {vlan_id}")

    # 🔹 Interface VLAN IP
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(switch_ip, username=username, password=password)
    shell = ssh.invoke_shell()
    time.sleep(1)

    commands = [
        "enable",
        "configure terminal",
        f"interface vlan {vlan_id}",
        f"ip address {ip_switch} {masque}",
        "no shutdown",
        "end",
        "write memory"
    ]
    for cmd in commands:
        shell.send(cmd + "\n")
        time.sleep(1)
    ssh.close()
    print("✅ Interface VLAN configurée")

    return f"VLAN {vlan_id} prêt sur {interfaces[0]} et {interfaces[1]}"