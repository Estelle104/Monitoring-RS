# app/services/firewall_service.py

import subprocess
import threading
import logging
from app.crud.machine import get_machine_by_mac
import re

logger = logging.getLogger(__name__)
DHCP_CONF = "/etc/dhcp/dhcpd.conf"


class FirewallService:

    def is_authorized(self, mac: str) -> bool:
        """Vérifie si la machine est dans la base de données"""
        machine = get_machine_by_mac(lower_mac := mac.lower())
        return machine is not None

    def _run(self, cmd: list, check=False) -> subprocess.CompletedProcess:
        """Exécute une commande shell avec gestion d'erreur"""
        try:
            return subprocess.run(cmd, capture_output=True, text=True, check=check)
        except subprocess.CalledProcessError as e:
            logger.warning(f"[FIREWALL] Commande échouée : {' '.join(cmd)} → {e}")
            raise
        except Exception as e:
            logger.error(f"[FIREWALL] Erreur inattendue : {e}")
            raise

    def block_machine(self, mac: str):
        """
        Bloque TOTALEMENT une machine :
        - DROP sur INPUT, OUTPUT, FORWARD
        - Bloque aussi les réponses ARP (via ebtables si disponible)
        """
        mac = mac.upper()

        # Bloquer via iptables sur toutes les chaînes
        for chain in ["INPUT", "OUTPUT", "FORWARD"]:
            self._run([
                "sudo", "iptables", "-I", chain, "1",
                "-m", "mac", "--mac-source", mac, "-j", "DROP"
            ])

        # Bloquer aussi avec ebtables (niveau 2 - Ethernet)
        # Empêche même la résolution ARP
        for chain in ["INPUT", "OUTPUT", "FORWARD"]:
            self._run([
                "sudo", "ebtables", "-I", chain, "1",
                "-s", mac, "-j", "DROP"
            ])
            self._run([
                "sudo", "ebtables", "-I", chain, "1",
                "-d", mac, "-j", "DROP"
            ])

        logger.info(f"[FIREWALL] ⛔ Bloqué totalement : {mac}")
        print(f"[FIREWALL] ⛔ Bloqué totalement : {mac}")

    def allow_machine(self, mac: str):
        """Retire toutes les règles de blocage pour une machine autorisée"""
        mac = mac.upper()

        # Retirer les règles iptables
        for chain in ["INPUT", "OUTPUT", "FORWARD"]:
            # Boucle pour supprimer toutes les occurrences éventuelles
            while True:
                result = self._run([
                    "sudo", "iptables", "-D", chain,
                    "-m", "mac", "--mac-source", mac, "-j", "DROP"
                ])
                if result.returncode != 0:
                    break  # Plus de règle à supprimer

        # Retirer les règles ebtables
        for chain in ["INPUT", "OUTPUT", "FORWARD"]:
            for direction in ["-s", "-d"]:
                while True:
                    result = self._run([
                        "sudo", "ebtables", "-D", chain,
                        direction, mac, "-j", "DROP"
                    ])
                    if result.returncode != 0:
                        break

        logger.info(f"[FIREWALL] ✅ Autorisé : {mac}")
        print(f"[FIREWALL] ✅ Autorisé : {mac}")

    def _get_ip_from_mac(self, mac: str) -> str | None:
        """Retrouve l'IP associée à une adresse MAC via la table ARP"""
        result = self._run(["arp", "-n"])
        for line in result.stdout.splitlines():
            if mac.lower() in line.lower():
                parts = line.split()
                if parts:
                    return parts[0]
        return None

    def _flush_arp(self, mac: str):
        """Supprime l'entrée ARP de la machine et vide son cache"""
        ip = self._get_ip_from_mac(mac)
        if not ip:
            logger.warning(f"[FIREWALL] IP introuvable pour MAC {mac}, ARP non vidé")
            return

        # Supprimer l'entrée ARP sur toutes les interfaces réseau possibles
        for iface in self._get_network_interfaces():
            self._run(["sudo", "ip", "neigh", "del", ip, "dev", iface])

        logger.info(f"[FIREWALL] 🧹 ARP vidé pour {mac} (IP: {ip})")
        print(f"[FIREWALL] 🧹 ARP vidé pour {mac} (IP: {ip})")

    def _get_network_interfaces(self) -> list[str]:
        """Retourne la liste des interfaces réseau actives"""
        result = self._run(["ip", "-o", "link", "show"])
        interfaces = []
        for line in result.stdout.splitlines():
            parts = line.split(":")
            if len(parts) >= 2:
                iface = parts[1].strip().split("@")[0]
                if iface != "lo":  # Exclure loopback
                    interfaces.append(iface)
        return interfaces if interfaces else ["eth0"]  # Fallback

    def expel_machine(self, mac: str):
        """
        Expulsion complète d'une machine non autorisée :
        1. Blocage total (iptables + ebtables)
        2. Vidage de l'entrée ARP
        3. Révocation DHCP si possible
        """
        mac = mac.upper()
        print(f"[FIREWALL] 🚫 Expulsion de : {mac}")

        # 1. Blocage total
        self.block_machine(mac)

        # 2. Vider l'entrée ARP pour forcer une déconnexion
        self._flush_arp(mac)

        # 3. Révoquer le bail DHCP si dhcp server disponible
        self._revoke_dhcp_lease(mac)

        logger.info(f"[FIREWALL] 🚫 Machine expulsée : {mac}")
        print(f"[FIREWALL] 🚫 Expulsion terminée : {mac}")

    def _revoke_dhcp_lease(self, mac: str):
        """Tente de révoquer le bail DHCP (fonctionne avec dnsmasq ou isc-dhcp)"""
        ip = self._get_ip_from_mac(mac)
        if not ip:
            return

        # Pour dnsmasq
        self._run(["sudo", "dhcp_release", "eth0", ip, mac])

        # Pour isc-dhcp-server
        self._run([
            "sudo", "omshell", "-p", "7911"
        ])  # Simplifié - à adapter selon votre setup

        logger.info(f"[FIREWALL] 🔒 Bail DHCP révoqué pour {mac}")

    def expel_after_timeout(self, mac: str, timeout: int):
        """Expulsion différée sans bloquer le thread principal"""
        mac = mac.upper()
        print(f"[FIREWALL] ⏳ Expulsion programmée dans {timeout}s pour {mac}")

        timer = threading.Timer(timeout, self.expel_machine, args=[mac])
        timer.daemon = True
        timer.start()

    def handle_new_device(self, mac: str) -> bool:
        """
        Point d'entrée principal lors de la détection d'un nouvel appareil.
        - Tous les appareils sont autorisés à la connexion (nouveau ou connu)
        """
        mac = mac.upper()

        self.allow_machine(mac)
        logger.info(f"[FIREWALL] ✅ Appareil autorisé : {mac}")
        print(f"[FIREWALL] ✅ Appareil autorisé : {mac}")
        return True


    def ajouter_machine_interdite(self, mac_address):
        """
        Ajoute un bloc host pour refuser une machine par son adresse MAC.
        """

        bloc = f"""
    host machine_interdite_{mac_address.replace(":", "")} {{
        hardware ethernet {mac_address};
        deny booting;
    }}
    """

        try:
            with open(DHCP_CONF, "a") as f:
                f.write(bloc)

            # Redémarrer le service DHCP
            subprocess.run(["sudo", "systemctl", "restart", "isc-dhcp-server"], check=True)

            print(f"Machine {mac_address} ajoutée à la liste interdite.")
            return True

        except Exception as e:
            print(f"Erreur : {e}")
            return False


    def supprimer_machine_interdite(self, mac_address):
        """
        Supprime le bloc host correspondant à la MAC donnée.
        """

        try:
            with open(DHCP_CONF, "r") as f:
                contenu = f.read()

            pattern = rf"""
    host machine_interdite_{mac_address.replace(":", "")}\s*\{{.*?hardware ethernet {mac_address};.*?deny booting;.*?\}}
    """

            nouveau_contenu = re.sub(pattern, "", contenu, flags=re.DOTALL)

            with open(DHCP_CONF, "w") as f:
                f.write(nouveau_contenu)

            subprocess.run(["sudo", "systemctl", "restart", "isc-dhcp-server"], check=True)

            print(f"Machine {mac_address} supprimée de la liste interdite.")
            return True

        except Exception as e:
            print(f"Erreur : {e}")
            return False
