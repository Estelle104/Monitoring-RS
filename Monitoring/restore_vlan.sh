#!/bin/bash

# =========================================================
# Restauration automatique des VLANs
# =========================================================

# Vérification des droits root
if [ "$EUID" -ne 0 ]; then 
  echo "Veuillez lancer ce script en tant que root (sudo)."
  exit 1
fi

# Charger le module VLAN 802.1Q
modprobe 8021q

# Interface parente
INTERFACE="eno1"

# S'assurer que l'interface physique est UP
ip link set $INTERFACE up

# Petite attente pour la stabilisation
sleep 2

# =========================================================
# Liste des VLANs à créer (Format: "ID:IP/Masque")
# =========================================================
# J'ai corrigé les IPs selon la logique de tes IDs
VLANS=(
    "1001:192.168.1.1/24"
    "1002:192.168.2.1/24"
    "1005:192.168.5.1/24"
    "1006:192.168.6.1/24"
    "1007:192.168.7.1/24"
    "2001:192.168.11.1/24"
    "2002:192.168.12.1/24"
    "2003:192.168.10.1/24"
)

# =========================================================
# Boucle de création
# =========================================================

for entry in "${VLANS[@]}"; do
    # Séparation de l'ID et de l'IP
    VLAN_ID=${entry%%:*}
    IP_ADDR=${entry#*:}
    VLAN_INTERFACE="${INTERFACE}.${VLAN_ID}"

    echo "▶ Configuration VLAN ${VLAN_ID}..."

    # 1. Création de l'interface si elle n'existe pas
    if ! ip link show "${VLAN_INTERFACE}" > /dev/null 2>&1; then
        ip link add link ${INTERFACE} name ${VLAN_INTERFACE} type vlan id ${VLAN_ID}
        echo "  - Interface ${VLAN_INTERFACE} créée"
    else
        echo "  - ${VLAN_INTERFACE} existe déjà"
    fi

    # 2. Attribution de l'IP (on vide les anciennes pour éviter les doublons vus dans ton ip addr)
    ip addr flush dev ${VLAN_INTERFACE}
    ip addr add ${IP_ADDR} dev ${VLAN_INTERFACE}
    echo "  - IP ${IP_ADDR} assignée"

    # 3. Activation
    ip link set up ${VLAN_INTERFACE}
    echo "  - Interface activée"
done

# =========================================================
# Activation IP Forwarding (Routage entre VLANs)
# =========================================================
echo "▶ Activation du forwarding IPv4..."
sysctl -w net.ipv4.ip_forward=1 > /dev/null

# =========================================================
# Redémarrage du serveur DHCP
# =========================================================
echo "▶ Redémarrage de isc-dhcp-server..."
systemctl restart isc-dhcp-server

echo ""
echo "======================================="
echo " ✅ Tous les VLANs sont opérationnels"
echo "======================================="
