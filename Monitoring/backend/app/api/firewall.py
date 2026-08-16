import uuid
from fastapi import APIRouter, Query
from pydantic import BaseModel
from app.services.firewall_service import FirewallService
from app.services.network_scan import scan_network
from app.crud.machine import create_machine, get_machine_by_mac, delete_machine_by_mac
from app.crud.etudiant import get_etudiant_info_by_macs
from app.crud.reset import reset_quota_all_machines, update_table_quota
from app.db.db import get_connection as get_db_connection
from fastapi import HTTPException


class AuthorizeRequest(BaseModel):
    mac: str
    hostname: str = ""


class BlockRequest(BaseModel):
    mac: str

class ExpulseRequest(BaseModel):
    mac: str

router = APIRouter()


@router.get("/firewall/scan")
def scan_and_check(
    network: str = Query(..., description="Réseau à scanner, ex: 192.168.3.0/24"),
    interface: str = Query("eno1", description="Interface réseau, ex: eno1.3333")
):
    machines = scan_network(interface, network)

    # Récupérer les infos étudiants pour toutes les MACs scannées
    all_macs = [m['mac'] for m in machines]
    etu_info = get_etudiant_info_by_macs(all_macs)

    result = []
    for m in machines:
        fw = FirewallService()
        authorized = fw.handle_new_device(m['mac'])
        mac_lower = m['mac'].lower()
        info = etu_info.get(mac_lower, {})
        # Ajouter une condition qui expulse apres le timeout
        result.append({
            "ip": m['ip'],
            "mac": m['mac'],
            "hostname": m.get('hostname', ''),
            "authorized": authorized,
            "etu": info.get('etu', ''),
            "nom": info.get('nom', '')
        })
    return result


@router.post("/firewall/check/{mac}")
def check_device(mac: str):
    """
    Vérifie si la machine est autorisée.
    Si non autorisée, elle sera bloquée automatiquement.
    """
    fw = FirewallService()
    authorized = fw.handle_new_device(mac)
    return {"authorized": authorized}


@router.post("/firewall/authorize")
def authorize_device(req: AuthorizeRequest):
    """
    Autorise une machine : l'ajoute dans la base de données
    et retire les règles de blocage firewall.
    """
    mac = req.mac.strip()
    hostname = req.hostname

    # Vérifier si déjà en base
    existing = get_machine_by_mac(mac)
    if existing:
        fw = FirewallService()
        fw.allow_machine(mac)
        return {"success": True, "message": "Machine déjà autorisée", "mac": mac}

    # Ajouter en base (PostgreSQL génère automatiquement l'id SERIAL)
    data = {
        "mac": mac,
        "hostname": hostname or None
    }
    create_machine(data)

    # Débloquer au niveau firewall
    fw = FirewallService()
    fw.allow_machine(mac)

    return {"success": True, "message": "Machine autorisée et ajoutée en base", "mac": mac}


@router.post("/firewall/block")
def block_device(req: BlockRequest):
    """
    Bloque une machine : la supprime de la base de données
    et ajoute les règles de blocage firewall.
    """
    mac = req.mac.strip()

    # Supprimer de la base
    deleted = delete_machine_by_mac(mac)

    # Bloquer au niveau firewall
    fw = FirewallService()
    fw.block_machine(mac)

    msg = "Machine supprimée et bloquée" if deleted else "Machine bloquée (n'était pas en base)"
    return {"success": True, "message": msg, "mac": mac}

@router.post("/firewall/expulserTotalement")
def expulser_totale_device(req: ExpulseRequest):
    """
    Expulse complètement une machine (supprime de la base et bloque firewall).
    """
    mac = req.mac.strip()
    fw = FirewallService()
    fw.ajouter_machine_interdite(mac)
    return {"success": True, "message": "Machine expulsée complètement", "mac": mac}


@router.post("/quota/reset-all")
def reset_all_quotas():
    """Réinitialise le quota de toutes les machines"""
    try:
        db_connection = get_db_connection()
        result = reset_quota_all_machines(db_connection)
        db_connection.close()
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=500, detail=result["message"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")


@router.post("/quota/update-table")
def update_quota_table():
    """Vide et re-remplit la table quota_machine à partir de machine JOIN quota"""
    try:
        db_connection = get_db_connection()
        result = update_table_quota(db_connection)
        db_connection.close()
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=500, detail=result["message"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")