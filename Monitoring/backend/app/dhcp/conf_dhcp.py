import subprocess
import sys
# sys.path.insert(0, '/opt/lampp/htdocs/RESEAU/RohySafe/RohySafeFinale_24_04_2026/RohySafe_SansNAT/backend/app/services')

from app.services.config_plage import definir_vlan


def generer_config_dhcp(adresse_reseau, nb_pc, interface, vlan_id):
    """
    Génère et écrit la configuration DHCP en utilisant les paramètres du VLAN

    Args:
        adresse_reseau: Adresse réseau (ex: "192.168.10.0")
        nb_pc: Nombre de PC à supporter
        interface: Interface réseau (ex: "eno1")
        vlan_id: ID du VLAN (ex: 100)
    """

    print("\n" + "=" * 80)
    print(" GÉNÉRATION DE LA CONFIGURATION DHCP")
    print("=" * 80 + "\n")

    try:
        # Appeler definir_vlan pour obtenir les paramètres
        print("▶ Étape 1: Appel de definir_vlan...")
        vlan_config = definir_vlan(adresse_reseau, nb_pc, interface, vlan_id)

        if vlan_config is None:
            print("✗ Erreur: definir_vlan n'a pas retourné de configuration")
            return False

        print(f"✓ Configuration VLAN obtenue\n")

        # Extraire les paramètres nécessaires
        print("▶ Étape 2: Extraction des paramètres...")
        ip_routeur = vlan_config["ip"]
        adresse_reseau_finale = vlan_config["adresse_reseau"]
        masque = vlan_config["masque"]
        plage_debut = vlan_config["debut"]
        plage_fin = vlan_config["fin"]

        print(f"  • IP Routeur: {ip_routeur}")
        print(f"  • Adresse réseau: {adresse_reseau_finale}")
        print(f"  • Masque: {masque}")
        print(f"  • Plage DHCP: {plage_debut} - {plage_fin}\n")

        # Créer le contenu du fichier dhcpd.conf
        print("▶ Étape 3: Génération du fichier de configuration...")
        contenu_dhcp = f"""default-lease-time 600;
        max-lease-time 7200;
        authoritative;

        subnet {adresse_reseau_finale} netmask {masque} {{
            range {plage_debut} {plage_fin};
            option routers {ip_routeur};

            # Bloc pour vérifier la MAC avant d'attribuer l'IP
            on discover {{
                set authorized = binary-to-ascii(16, 8, ":", hardware);
                execute("/etc/dhcp/check-mac.sh", authorized);
                if (execute-result != 0) {{
                    discard;
                }}
            }}
        }}
        """

        print(f"✓ Fichier de configuration généré\n")

        # Afficher le contenu généré
        print("▶ Étape 4: Contenu du fichier dhcpd.conf:")
        print("-" * 80)
        print(contenu_dhcp)
        print("-" * 80 + "\n")

        # Écriture du fichier
        print("▶ Étape 5: Écriture du fichier de configuration...")

        fichier_temp = "/tmp/dhcpd.conf"
        contenu_existant = ""

        try:
            with open(fichier_temp, 'r') as f:
                contenu_existant = f.read()
        except FileNotFoundError:
            print(f"▶ Étape 5b: Fichier temporaire n'existe pas, création nouvelle\n")

        # Ajouter la nouvelle configuration
        contenu_final = contenu_existant + "\n" + contenu_dhcp

        with open(fichier_temp, 'a') as f:
            f.write("\n" + contenu_dhcp)

        print(f"✓ Configuration ajoutée au fichier temporaire: {fichier_temp}\n")

        # Afficher contenu complet
        print("▶ Étape 6: Contenu complet du fichier /tmp/dhcpd.conf:")
        print("-" * 80)

        with open(fichier_temp, 'r') as f:
            print(f.read())

        print("-" * 80 + "\n")

        # Copier vers fichier final
        print("▶ Étape 7: Copie vers /etc/dhcp/dhcpd.conf (avec sudo)...")

        try:
            subprocess.run(
                ["sudo", "cp", fichier_temp, "/etc/dhcp/dhcpd.conf"],
                check=True
            )

            print(f"✓ Fichier copié avec succès vers /etc/dhcp/dhcpd.conf\n")

            # Vérification
            print("▶ Étape 8: Vérification du fichier final...")

            try:
                result = subprocess.run(
                    ["sudo", "cat", "/etc/dhcp/dhcpd.conf"],
                    capture_output=True,
                    text=True,
                    check=True
                )

                print("Contenu de /etc/dhcp/dhcpd.conf:")
                print("-" * 80)
                print(result.stdout)
                print("-" * 80 + "\n")

            except subprocess.CalledProcessError:
                print(f"⚠ Impossible de lire /etc/dhcp/dhcpd.conf\n")

            # Redémarrage DHCP
            print("▶ Étape 9: Redémarrage du service DHCP...")

            try:
                subprocess.run(
                    ["sudo", "systemctl", "restart", "isc-dhcp-server"],
                    check=True
                )

                print(f"✓ Service DHCP redémarré avec succès\n")

            except subprocess.CalledProcessError:
                print(f"⚠ Attention: Impossible de redémarrer le service DHCP")
                print(f"  Essayez: sudo systemctl restart isc-dhcp-server\n")

            return True

        except subprocess.CalledProcessError as e:
            print(f"✗ Erreur lors de la copie du fichier: {e}\n")
            print("Essayez la commande manuellement:")
            print(f"  sudo cp {fichier_temp} /etc/dhcp/dhcpd.conf\n")
            return False

    except IOError as e:
        print(f"✗ Erreur lors de l'écriture du fichier: {e}\n")
        return False

    except Exception as e:
        print(f"✗ Erreur générale: {e}\n")
        import traceback
        traceback.print_exc()
        return False


# Exemple d'utilisation
if __name__ == "__main__":

    print("\nEXEMPLE 1: Génération avec definir_vlan")
    print("=" * 80)

    generer_config_dhcp(
        adresse_reseau="192.168.23.0",
        nb_pc=21,
        interface="eno1",
        vlan_id=12
    )