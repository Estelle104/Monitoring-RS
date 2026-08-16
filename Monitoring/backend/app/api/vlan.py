# app/api/vlan_api.py
from fastapi import APIRouter, HTTPException, Body
from fastapi import Request
import json
from pydantic import BaseModel
from typing import Optional
from app.crud.vlan import get_all_vlans, get_vlan_by_id, get_vlan_by_idSalle, create_vlan, create_salle_vlan_link, update_vlan, delete_vlan
from app.crud.salle import get_all_salles, get_salle_by_id
from app.crud.port import get_all_ports, get_ports_by_vlan, create_port, update_port, delete_port
# from app.crud.salle_vlan import (
#     get_all_salle_vlans, get_salle_vlans_by_vlan,
#     create_salle_vlan, update_salle_vlan, delete_salle_vlan
# )
from app.services.config_plage import definir_vlan, creer_vlan_ip
from app.services.config_dhcp import generer_config_dhcp
from app.services.config_serveur_switch import create_vlan_switch_A, get_switch_ports, get_free_interfaces
# from app.services.internet import interface_down, interface_up
router = APIRouter()


# ─── Schemas ────────────────────────────────────────
class VlanCreate(BaseModel):
    vlan: int
    ip: str
    id_salle: str
    interface: Optional[str] = None
    switch_port: Optional[str] = None  # Port du switch (ex: gi1/0/4, Fa0/5)
    switch_port2: Optional[str] = None  # Port du switch (ex: gi1/0/4, Fa0/5)
    nb_pc: Optional[int] = 50
    switch_ip: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None

class VlanUpdate(BaseModel):
    vlan: Optional[int] = None
    ip: Optional[str] = None
    interface: Optional[str] = None
    switch_port: Optional[str] = None
    switch_ip: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None

class SwitchPortsRequest(BaseModel):
    switch_ip: str
    username: Optional[str] = "cisco"
    password: Optional[str] = "cisco1234!"

class PortCreate(BaseModel):
    numero_port: int
    id_vlan: Optional[str] = None

class PortUpdate(BaseModel):
    numero_port: Optional[int] = None
    id_vlan: Optional[str] = None

class SalleVlanCreate(BaseModel):
    id_salle: str
    id_vlan: str
    limit_debit: Optional[int] = None
    limit_nb_machine: Optional[int] = None
    limit_bande_passante: Optional[int] = None

class SalleVlanUpdate(BaseModel):
    limit_debit: Optional[int] = None
    limit_nb_machine: Optional[int] = None
    limit_bande_passante: Optional[int] = None

class BandwidthLimitRequest(BaseModel):
    vlan_id: int           # Numéro du VLAN (ex: 3333)
    interface: str         # Interface physique (ex: eno1)
    download_kbps: int     # Limite download en Kbit/s (ex: 10000 = 10 Mbit/s)
    upload_kbps: int       # Limite upload en Kbit/s (ex: 5000 = 5 Mbit/s)


class InterfaceAction(BaseModel):
    interface: str
# ─── INTERFACES RÉSEAU (réelles de la machine) ─────

@router.get("/interfaces")
def list_interfaces():
    """Récupérer les interfaces réseau réelles de la machine"""
    import os, subprocess
    try:
        ifaces = os.listdir('/sys/class/net/')
        result = []
        for iface in sorted(ifaces):
            info = {'name': iface, 'state': 'down', 'ipv4': None, 'mac': None}
            try:
                with open(f'/sys/class/net/{iface}/operstate') as f:
                    info['state'] = f.read().strip()
            except Exception:
                pass
            try:
                with open(f'/sys/class/net/{iface}/address') as f:
                    info['mac'] = f.read().strip()
            except Exception:
                pass
            try:
                out = subprocess.check_output(
                    ['ip', '-4', 'addr', 'show', iface], text=True
                )
                for line in out.split('\n'):
                    if 'inet ' in line:
                        info['ipv4'] = line.strip().split()[1]
                        break
            except Exception:
                pass
            result.append(info)
        return {"status": "ok", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── PORTS DU SWITCH ────────────────────────────────

@router.post("/switch/ports")
def list_switch_ports(body: SwitchPortsRequest):
    """Récupérer les ports disponibles sur le switch Cisco"""
    try:
        ports = get_switch_ports(
            switch_ip=body.switch_ip,
            username=body.username or "cisco",
            password=body.password or "cisco1234!"
        )
        return {"status": "ok", "data": ports}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur connexion switch: {str(e)}")


@router.post("/switch/free-ports")
def list_free_switch_ports(body: SwitchPortsRequest):
    """Récupérer uniquement les ports libres (non connectés) du switch"""
    try:
        ports = get_free_interfaces(
            switch_ip=body.switch_ip,
            username=body.username or "cisco",
            password=body.password or "cisco1234!"
        )
        return {"status": "ok", "data": ports}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur connexion switch: {str(e)}")


# ─── VLAN ROUTES ────────────────────────────────────

@router.get("/vlans")
def list_vlans():
    """Récupérer tous les VLANs"""
    vlans = get_all_vlans()
    return {"status": "ok", "data": vlans}


@router.get("/vlans/{vlan_id}")
def get_vlan(vlan_id: str):
    """Récupérer un VLAN par son ID"""
    vlan = get_vlan_by_id(vlan_id)
    if not vlan:
        raise HTTPException(status_code=404, detail="VLAN non trouvé")
    return {"status": "ok", "data": vlan}

@router.get("/vlans/salle/{salle_id}")
def get_vlan_by_salle(salle_id: str):
    """Récupérer un VLAN par son ID de salle"""
    vlan = get_vlan_by_idSalle(salle_id)
    if not vlan:
        raise HTTPException(status_code=404, detail="VLAN non trouvé")
    return {"status": "ok", "data": vlan}


@router.post("/vlans")
def add_vlan(body: VlanCreate):
    """Créer un nouveau VLAN avec calcul automatique du masque"""
    try:
        # Calculer automatiquement le prefix à partir de l'IP et du nb_pc
        nb_pc = body.nb_pc or 50
        reseau = creer_vlan_ip(body.ip, nb_pc)
        prefix = reseau.prefixlen  # ex: 24, 27

        # Stocker ip/prefix dans la base (ex: 192.168.3.0/24)
        vlan_data = body.dict()
        vlan_data["ip"] = f"{body.ip}/{prefix}"

        vlan_id = create_vlan(vlan_data)
        create_salle_vlan_link({
            "id_salle": body.id_salle,
            "id_vlan": vlan_id,
            "limit_nb_machine": body.nb_pc
        })

        # Créer automatiquement 2 ports associés au VLAN
        create_port({"numero_port": 1, "id_vlan": vlan_id})
        create_port({"numero_port": 2, "id_vlan": vlan_id})

        if body.interface:
            vlan_config = generer_config_dhcp(body.ip, nb_pc, body.interface, body.vlan)
            # Utiliser le port du switch spécifié ou un par défaut
            switch_port = body.switch_port or "gi1/0/4"
            switch_port2 = body.switch_port2 or "gi1/0/5"
            create_vlan_switch_A(
                vlan_config=vlan_config,
                switch_ip=body.switch_ip or "173.16.1.4",
                username=body.username or "cisco",
                password=body.password or "cisco1234!",
                interface=switch_port
                # interface2=switch_port2
            )
        return {"status": "ok", "id": vlan_id, "message": "VLAN créé avec succès"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/vlans/{vlan_id}")
def modify_vlan(vlan_id: str, body: VlanUpdate):
    """Modifier un VLAN existant"""
    existing = get_vlan_by_id(vlan_id)
    if not existing:
        raise HTTPException(status_code=404, detail="VLAN non trouvé")
    try:
        data = body.dict(exclude_unset=True)
        # Fusionner avec les données existantes
        merged = {**existing, **data}
        update_vlan(vlan_id, merged)
        return {"status": "ok", "message": "VLAN modifié avec succès"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/vlans/{vlan_id}")
def remove_vlan(vlan_id: str):
    """Supprimer un VLAN"""
    existing = get_vlan_by_id(vlan_id)
    if not existing:
        raise HTTPException(status_code=404, detail="VLAN non trouvé")
    try:
        delete_vlan(vlan_id)
        return {"status": "ok", "message": "VLAN supprimé avec succès"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ─── LIMITATION DE DÉBIT PAR VLAN (tc) ─────────────

@router.post("/vlans/bandwidth-limit")
def set_bandwidth_limit(body: BandwidthLimitRequest):
    """
    Limite le débit sur la sous-interface VLAN via tc (traffic control).
    Ex: eno1.3333 → download max 10 Mbit/s, upload max 5 Mbit/s
    """
    import subprocess

    iface = f"{body.interface}.{body.vlan_id}"

    try:
        # Vérifier que l'interface existe
        result = subprocess.run(["ip", "link", "show", iface], capture_output=True, text=True)
        if result.returncode != 0:
            raise HTTPException(status_code=404, detail=f"Interface {iface} introuvable")

        # 1️⃣ Supprimer les anciennes règles tc (ignorer erreur si aucune)
        subprocess.run(["sudo", "tc", "qdisc", "del", "dev", iface, "root"], capture_output=True)
        subprocess.run(["sudo", "tc", "qdisc", "del", "dev", iface, "ingress"], capture_output=True)

        # 2️⃣ Limiter le download (trafic sortant de l'interface vers les clients)
        # Utilise HTB (Hierarchical Token Bucket)
        subprocess.run([
            "sudo", "tc", "qdisc", "add", "dev", iface, "root", "handle", "1:",
            "htb", "default", "10"
        ], check=True)

        subprocess.run([
            "sudo", "tc", "class", "add", "dev", iface, "parent", "1:",
            "classid", "1:10", "htb",
            "rate", f"{body.download_kbps}kbit",
            "ceil", f"{body.download_kbps}kbit"
        ], check=True)

        # 3️⃣ Limiter l'upload (trafic entrant — via ingress + police)
        subprocess.run([
            "sudo", "tc", "qdisc", "add", "dev", iface, "ingress"
        ], check=True)

        # Convertir kbps en bytes/s pour le policer (kbit/s * 1000 / 8)
        upload_bps = body.upload_kbps * 1000 // 8

        subprocess.run([
            "sudo", "tc", "filter", "add", "dev", iface, "parent", "ffff:",
            "protocol", "ip", "u32", "match", "u32", "0", "0",
            "police", "rate", f"{body.upload_kbps}kbit", "burst", f"{upload_bps}",
            "drop", "flowid", ":1"
        ], check=True)

        return {
            "status": "ok",
            "message": f"Débit limité sur {iface}",
            "interface": iface,
            "download_kbps": body.download_kbps,
            "upload_kbps": body.upload_kbps
        }

    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Erreur tc: {e.stderr or str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/vlans/bandwidth-limit/{vlan_num}/{interface}")
def remove_bandwidth_limit(vlan_num: int, interface: str):
    """Supprimer la limitation de débit sur une sous-interface VLAN"""
    import subprocess
    iface = f"{interface}.{vlan_num}"

    try:
        subprocess.run(["sudo", "tc", "qdisc", "del", "dev", iface, "root"], capture_output=True)
        subprocess.run(["sudo", "tc", "qdisc", "del", "dev", iface, "ingress"], capture_output=True)
        return {"status": "ok", "message": f"Limitation supprimée sur {iface}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── PORT ROUTES ────────────────────────────────────

@router.get("/ports")
def list_ports():
    """Récupérer tous les ports"""
    ports = get_all_ports()
    return {"status": "ok", "data": ports}


@router.get("/ports/vlan/{vlan_id}")
def list_ports_by_vlan(vlan_id: str):
    """Récupérer les ports d'un VLAN"""
    ports = get_ports_by_vlan(vlan_id)
    return {"status": "ok", "data": ports}


@router.post("/ports")
def add_port(body: PortCreate):
    """Créer un nouveau port"""
    try:
        port_id = create_port(body.dict())
        return {"status": "ok", "id": port_id, "message": "Port créé avec succès"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/ports/{port_id}")
def modify_port(port_id: str, body: PortUpdate):
    """Modifier un port existant"""
    try:
        update_port(port_id, body.dict(exclude_unset=True))
        return {"status": "ok", "message": "Port modifié avec succès"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/ports/{port_id}")
def remove_port(port_id: str):
    """Supprimer un port"""
    try:
        delete_port(port_id)
        return {"status": "ok", "message": "Port supprimé avec succès"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ─── SALLE_VLAN ROUTES ─────────────────────────────

# @router.get("/salle-vlans")
# def list_salle_vlans():
#     """Récupérer toutes les liaisons salle-vlan"""
#     sv = get_all_salle_vlans()
#     return {"status": "ok", "data": sv}


# @router.get("/salle-vlans/vlan/{vlan_id}")
# def list_salle_vlans_by_vlan(vlan_id: str):
#     """Récupérer les salles liées à un VLAN"""
#     sv = get_salle_vlans_by_vlan(vlan_id)
#     return {"status": "ok", "data": sv}


# @router.post("/salle-vlans")
# def add_salle_vlan(body: SalleVlanCreate):
#     """Créer une liaison salle-vlan"""
#     try:
#         create_salle_vlan(body.dict())
#         return {"status": "ok", "message": "Liaison salle-vlan créée avec succès"}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))


# @router.put("/salle-vlans/{id_salle}/{id_vlan}")
# def modify_salle_vlan(id_salle: str, id_vlan: str, body: SalleVlanUpdate):
#     """Modifier une liaison salle-vlan"""
#     try:
#         update_salle_vlan(id_salle, id_vlan, body.dict(exclude_unset=True))
#         return {"status": "ok", "message": "Liaison salle-vlan modifiée avec succès"}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))


# @router.delete("/salle-vlans/{id_salle}/{id_vlan}")
# def remove_salle_vlan(id_salle: str, id_vlan: str):
#     """Supprimer une liaison salle-vlan"""
#     try:
#         delete_salle_vlan(id_salle, id_vlan)
#         return {"status": "ok", "message": "Liaison salle-vlan supprimée avec succès"}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))



# @router.post("/internet/interface/down")
# async def disable_interface(request: Request, interface: Optional[str] = None):
#     """Désactiver une interface réseau.

#     Tente de lire le JSON body {"interface": "eno1"} si présent,
#     sinon utilise le paramètre `?interface=...`.
#     """
#     iface = None
#     try:
#         raw = await request.body()
#         print(f"[DEBUG] /internet/interface/down headers={dict(request.headers)}")
#         print(f"[DEBUG] /internet/interface/down raw={raw!r}")
#         if raw:
#             try:
#                 body = json.loads(raw.decode('utf-8')) if isinstance(raw, (bytes, bytearray)) else json.loads(raw)
#             except Exception as e:
#                 print(f"[DEBUG] JSON parse error: {e}")
#                 body = None
#             if isinstance(body, dict) and 'interface' in body:
#                 iface = str(body.get('interface'))
#     except Exception as e:
#         print(f"[DEBUG] Error reading body: {e}")
#         body = None

#     if not iface and interface:
#         iface = interface

#     if not iface:
#         raise HTTPException(status_code=422, detail="Paramètre 'interface' requis (body JSON ou query)")

#     interface_down(iface)
#     return {"status": "ok", "message": f"Interface {iface} désactivée"}


# @router.post("/internet/interface/up")
# async def enable_interface(request: Request, interface: Optional[str] = None):
#     """Activer une interface réseau.

#     Tente de lire le JSON body {"interface": "eno1"} si présent,
#     sinon utilise le paramètre `?interface=...`.
#     """
#     iface = None
#     try:
#         raw = await request.body()
#         print(f"[DEBUG] /internet/interface/up headers={dict(request.headers)}")
#         print(f"[DEBUG] /internet/interface/up raw={raw!r}")
#         if raw:
#             try:
#                 body = json.loads(raw.decode('utf-8')) if isinstance(raw, (bytes, bytearray)) else json.loads(raw)
#             except Exception as e:
#                 print(f"[DEBUG] JSON parse error: {e}")
#                 body = None
#             if isinstance(body, dict) and 'interface' in body:
#                 iface = str(body.get('interface'))
#     except Exception as e:
#         print(f"[DEBUG] Error reading body: {e}")
#         body = None

#     if not iface and interface:
#         iface = interface

#     if not iface:
#         raise HTTPException(status_code=422, detail="Paramètre 'interface' requis (body JSON ou query)")

#     interface_up(iface)
#     return {"status": "ok", "message": f"Interface {iface} activée"}