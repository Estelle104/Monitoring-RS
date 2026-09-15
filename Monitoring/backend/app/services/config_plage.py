import math
import ipaddress
import subprocess

# l'adresse réseau et du nb de PC -> sous-réseau IP du VLAN
def creer_vlan_ip(adresse_reseau, nb_pc):
    total_hosts = nb_pc + 2
    bits = math.ceil(math.log2(total_hosts))
    prefix = 32 - bits
    reseau = ipaddress.ip_network(f"{adresse_reseau}/{prefix}", strict=False)
    return reseau



def definir_vlan(adresse_reseau, nb_pc, interface, vlan_id):

    vlan_ip = creer_vlan_ip(adresse_reseau, nb_pc)
    
    print(f"VLAN IP       : {vlan_ip}")
    print(f"Adresse réseau: {vlan_ip.network_address}")
    print(f"Broadcast     : {vlan_ip.broadcast_address}")
    print(f"Masque        : {vlan_ip.netmask}")
    print(f"Interface     : {interface}")
    print(f"VLAN ID       : {vlan_id}")
    
    # Nom de l'interface VLAN
    interface_vlan = f"{interface}.{vlan_id}"

    try:
        # Charge le module Linux nécessaire pour gérer les VLAN.
        subprocess.run(["sudo", "modprobe", "8021q"], check=True)

        # Crée l'interface VLAN sur l'interface réseau principale
        subprocess.run(["sudo", "ip", "link", "add", "link", interface,
                        "name", interface_vlan, "type", "vlan", "id", str(vlan_id)],
                       check=True)

        # Attribue la première adresse IP disponible du réseau à l'interface VLAN
        subprocess.run(["sudo", "ip", "addr", "add", f"{vlan_ip.network_address+1}/{vlan_ip.prefixlen}",
                        "dev", interface_vlan], check=True)

        # Active l'interface VLAN
        subprocess.run(["sudo", "ip", "link", "set", "up", interface_vlan], check=True)

        print(f"VLAN {vlan_id} créé et interface {interface_vlan} activée avec IP {vlan_ip.network_address+1}/{vlan_ip.prefixlen}")

        return {
            "debut": str(vlan_ip.network_address + 3),
            "fin": str(vlan_ip.network_address + nb_pc + 3),
            "masque": str(vlan_ip.netmask),
            "vlan_id": vlan_id,
            "interface_vlan": interface_vlan,
            "adresse_reseau": str(vlan_ip.network_address),
            "broadcast": str(vlan_ip.broadcast_address),
            "ip": str(vlan_ip.network_address + 1),
            "ip_switch": str(vlan_ip.network_address + 2),
            "prefix": vlan_ip.prefixlen
        }

    except subprocess.CalledProcessError as e:
        print("Erreur lors de la création du VLAN :", e)


    

