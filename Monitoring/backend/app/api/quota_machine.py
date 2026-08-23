import math

from app.api.quota import format_bytes, get_usage_status
from app.crud.quota_machine import get_all_quota_machine, create_quota_machine, update_quota_machine, delete_quota_machine
from fastapi import APIRouter, Body, HTTPException

router = APIRouter()


def calculate_quota_bytes(value, unit):
    """Convertir une valeur + unité en octets."""
    if isinstance(value, bool):
        raise ValueError

    number = float(value)
    if not math.isfinite(number) or number < 0:
        raise ValueError

    normalized_unit = str(unit or "").strip().lower()
    unit_multipliers = {
        "bytes": 1,
        "byte": 1,
        "b": 1,
        "ko": 1024,
        "kb": 1024,
        "mo": 1024 ** 2,
        "mb": 1024 ** 2,
        "go": 1024 ** 3,
        "gb": 1024 ** 3,
        "to": 1024 ** 4,
        "tb": 1024 ** 4,
    }

    if normalized_unit not in unit_multipliers:
        raise ValueError

    return int(round(number * unit_multipliers[normalized_unit]))


def get_quota_consomme_from_payload(data: dict) -> int:
    """Extraire la valeur en octets depuis quota_value+quota_unit ou quota_consomme brut."""
    # Nouveau format : valeur + unité
    if "quota_value" in data and "quota_unit" in data:
        return calculate_quota_bytes(data["quota_value"], data["quota_unit"])

    # Ancien format rétrocompatible : octets bruts
    if "quota_consomme" not in data:
        raise HTTPException(
            status_code=422,
            detail="Les champs 'quota_value' et 'quota_unit' sont requis"
        )

    raw_quota = data["quota_consomme"]
    if isinstance(raw_quota, bool):
        raise ValueError
    if isinstance(raw_quota, float) and not raw_quota.is_integer():
        raise ValueError
    if isinstance(raw_quota, str) and not raw_quota.strip().isdigit():
        raise ValueError

    quota_consomme = int(raw_quota)
    if quota_consomme < 0:
        raise HTTPException(status_code=422, detail="Le quota consommé doit être positif ou nul")

    return quota_consomme


@router.get("/quota_machine")
def list_quota_machine():
    """Récupérer toutes les quota_machine avec les informations complètes."""
    quota_machine = get_all_quota_machine()
    data = []

    for item in quota_machine:
        quota_limit = float(item["quota_limite"] or 0)
        quota_consomme = float(item["quota_consomme"] or 0)
        percent = 0 if quota_limit <= 0 else min(100.0, (quota_consomme / quota_limit) * 100)
        status = get_usage_status(percent)

        data.append({
            **item,
            "formatted_quota_limite": format_bytes(quota_limit),
            "formatted_quota_consomme": format_bytes(quota_consomme),
            "usage_percent": round(percent, 2),
            "status": status["label"],
            "status_class": status["className"],
        })

    return {"status": "ok", "data": data}


@router.post("/quota_machine/create")
def create_new_quota_machine(quota_machine: dict = Body(...)):
    """Créer une nouvelle quota_machine"""
    try:
        quota_consomme = get_quota_consomme_from_payload(quota_machine)
        payload = {**quota_machine, "quota_consomme": quota_consomme}
        # Retirer les clés de saisie si présentes pour ne garder que quota_consomme
        payload.pop("quota_value", None)
        payload.pop("quota_unit", None)

        quota_machine_id_machine = create_quota_machine(payload)
        return {
            "status": "ok",
            "data": {
                "id_machine": quota_machine_id_machine,
                "quota_consomme": quota_consomme,
                "formatted_quota_consomme": format_bytes(quota_consomme),
            },
        }
    except HTTPException:
        raise
    except (TypeError, ValueError):
        raise HTTPException(status_code=422, detail="La valeur ou l'unité du quota consommé est invalide")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/quota_machine/{quota_machine_id}")
def update_quota_machine_endpoint(quota_machine_id: int, data: dict = Body(...)):
    """Mettre à jour uniquement la valeur de quota consommé."""
    try:
        quota_consomme = get_quota_consomme_from_payload(data)

        updated = update_quota_machine(quota_machine_id, quota_consomme)
        if not updated:
            raise HTTPException(status_code=404, detail="Quota machine non trouvé")

        return {
            "status": "ok",
            "message": "Quota machine mis à jour avec succès",
            "data": {
                "quota_consomme": quota_consomme,
                "formatted_quota_consomme": format_bytes(quota_consomme),
            },
        }
    except HTTPException:
        raise
    except (TypeError, ValueError):
        raise HTTPException(status_code=422, detail="La valeur ou l'unité du quota consommé est invalide")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/quota_machine/{quota_machine_id}")
def delete_quota_machine_endpoint(quota_machine_id: int):
    """Supprimer une quota_machine"""
    try:
        deleted = delete_quota_machine(quota_machine_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Quota machine non trouvé")
        return {"status": "ok", "message": "Quota machine supprimé avec succès"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
