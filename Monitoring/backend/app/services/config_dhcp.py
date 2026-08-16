import subprocess
import sys
import traceback
import re
sys.path.insert(0, '/opt/lampp/htdocs/RohySafeFinale_24_04_2026/Monitoring/backend/app/services')
from config_plage import definir_vlan


# =========================================================
# 🌐 Activer le forwarding IP
# =========================================================
def activer_ip_forwarding():
    print("▶ Activation du forwarding IP...")

    try:
        subprocess.run(
            ["sudo", "sysctl", "-w", "net.ipv4.ip_forward=1"],
            check=True
        )

        fichier = "/etc/sysctl.conf"
        ligne = "net.ipv4.ip_forward=1"

        try:
            with open(fichier, "r") as f:
                if ligne in f.read():
                    print("✓ Forwarding déjà actif")
                    return True
        except:
            pass

        with open("/tmp/sysctl.conf", "w") as f:
            f.write("\n" + ligne + "\n")

        subprocess.run(
            ["sudo", "bash", "-c", "cat /tmp/sysctl.conf >> /etc/sysctl.conf"],
            check=True
        )

        print("✓ Forwarding activé et persistant\n")
        return True

    except Exception as e:
        print("✗ Erreur forwarding:", e)
        return False


# =========================================================
# 🔢 Convertir masque en CIDR
# =========================================================
def masque_vers_cidr(masque):
    return sum(bin(int(x)).count('1') for x in masque.split('.'))


# =========================================================
# 🔧 Configurer interface DHCP
# =========================================================
def configurer_interface_dhcp(interface_vlan):

    print("▶ Configuration interface DHCP...")

    fichier = "/etc/default/isc-dhcp-server"
    interfaces = []

    try:
        with open(fichier, "r") as f:
            for line in f:
                if line.startswith("INTERFACESv4"):
                    contenu = line.split("=")[1].replace('"', '').strip()
                    if contenu:
                        interfaces = contenu.split()
    except:
        pass

    if interface_vlan not in interfaces:
        interfaces.append(interface_vlan)

    config = f'INTERFACESv4="{" ".join(interfaces)}"\nINTERFACESv6=""\n'

    with open("/tmp/isc-dhcp-server", "w") as f:
        f.write(config)

    subprocess.run(
        ["sudo", "cp", "/tmp/isc-dhcp-server", fichier],
        check=True
    )

    print(f"✓ Interfaces DHCP: {' '.join(interfaces)}\n")


# =========================================================
# 📡 Générer DHCP + VLAN (SANS NAT)
# =========================================================
def generer_config_dhcp(adresse_reseau, nb_pc, interface, vlan_id):

    print("\n" + "=" * 80)
    print(" CONFIGURATION DHCP + VLAN (MODE MONITORING)")
    print("=" * 80 + "\n")

    try:

        # 1️⃣ Forwarding
        activer_ip_forwarding()

        # 2️⃣ VLAN
        print("▶ Création VLAN...")
        vlan = definir_vlan(adresse_reseau, nb_pc, interface, vlan_id)

        if vlan is None:
            print("✗ Erreur VLAN")
            return False

        ip_routeur = vlan["ip"]
        reseau = vlan["adresse_reseau"]
        masque = vlan["masque"]
        debut = vlan["debut"]
        fin = vlan["fin"]

        print(f"Réseau: {reseau}")
        print(f"Plage: {debut} → {fin}")
        print(f"Gateway: {ip_routeur}\n")

        # 3️⃣ DHCP
        dhcp_conf = f"""
            subnet {reseau} netmask {masque} {{
            range {debut} {fin};
            option routers {ip_routeur};
            option domain-name-servers {ip_routeur};
            default-lease-time 600;
            max-lease-time 7200;
        }}
        """

        with open("/tmp/dhcpd.conf", "r") as f:
            contenu = f.read()

        pattern = rf"subnet\s+{re.escape(reseau)}\s+netmask\s+{re.escape(masque)}\s*\{{.*?\}}"
        contenu = re.sub(pattern, "", contenu, flags=re.DOTALL)

        with open("/tmp/dhcpd.conf", "w") as f:
            f.write(contenu.rstrip())
            f.write("\n\n")
            f.write(dhcp_conf.strip())
            f.write("\n")

        subprocess.run(
            ["sudo", "cp", "/tmp/dhcpd.conf", "/etc/dhcp/dhcpd.conf"],
            check=True
        )

        print("✓ DHCP configuré\n")

        # 4️⃣ Interface DHCP
        interface_vlan = f"{interface}.{vlan_id}"
        configurer_interface_dhcp(interface_vlan)

        # 5️⃣ Restart DHCP
        print("▶ Redémarrage DHCP...")
        subprocess.run(
            ["sudo", "systemctl", "restart", "isc-dhcp-server"],
            check=True
        )

        print("✓ DHCP actif")
        print("🚫 PAS de NAT ici (géré par portail captif)\n")

        return vlan

    except Exception as e:
        print("✗ ERREUR:", e)
        traceback.print_exc()
        return False


# =========================================================
# ▶ TEST
# =========================================================
if __name__ == "__main__":

    config = generer_config_dhcp(
        adresse_reseau="192.168.23.0",
        nb_pc=50,
        interface="eno1",
        vlan_id=100
    )

    print("CONFIG:", config)