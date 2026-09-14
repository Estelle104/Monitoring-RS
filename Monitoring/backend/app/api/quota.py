import math

from app.crud.quota import get_all_quota, create_quota, update_quota, delete_quota
from fastapi import APIRouter, Body, HTTPException


def format_bytes(value):
    number = float(value or 0)
    if not math.isfinite(number) or number <= 0:
        return "0 Bytes"

    units = ["Bytes", "Ko", "Mo", "Go", "To"]
    index = min(int(math.floor(math.log(number, 1024))), len(units) - 1)
    size = number / (1024 ** index)
    text = f"{size:.2f}".rstrip("0").rstrip(".")
    return f"{text} {units[index]}"


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


def get_quota_limit_saisie(data: dict):
    if "quota_value" in data and "quota_unit" in data:
        return calculate_quota_bytes(data["quota_value"], data["quota_unit"])

    if "quota_limite" not in data:
        raise HTTPException(status_code=422, detail="Les champs 'quota_value' et 'quota_unit' sont requis")

    raw_quota = data["quota_limite"]
    if isinstance(raw_quota, bool):
        raise ValueError
    if isinstance(raw_quota, float) and not raw_quota.is_integer():
        raise ValueError
    if isinstance(raw_quota, str) and not raw_quota.strip().isdigit():
        raise ValueError

    quota_limite = int(raw_quota)
    if quota_limite < 0:
        raise HTTPException(status_code=422, detail="La limite du quota doit être positive ou nulle")

    return quota_limite


def get_usage_status(percent):
    if percent >= 100:
        return {"label": "Limite atteinte", "className": "status-danger"}
    if percent >= 75:
        return {"label": "Très élevé", "className": "status-warn"}
    return {"label": "Normal", "className": "status-ok"}


router = APIRouter()


@router.get("/quota")
def list_quota():
    """Récupérer toutes les quota"""
    quota_list = get_all_quota()
    data = []
    total_bytes = 0

    for quota in quota_list:
        quota_limit = float(quota["quota_limite"] or 0)
        total_bytes += quota_limit
        data.append({
            **quota,
            "formatted_quota_limite": format_bytes(quota_limit),
            "status": get_usage_status(0)["label"],
        })

    return {
        "status": "ok",
        "data": data,
        "summary": {
            "total_bytes": total_bytes,
            "formatted_total_quota": format_bytes(total_bytes),
        },
    }


@router.post("/quota/create")
def create_new_quota(quota: dict = Body(...)):
    """Créer une nouvelle quota"""
    try:
        if "quota_limite" not in quota:
            quota["quota_limite"] = get_quota_limit_saisie(quota)
        quota_id_type_user = create_quota(quota)
        return {"status": "ok", "data": {"id_type_user": quota_id_type_user, "quota_limite": quota["quota_limite"]}}
    except HTTPException:
        raise
    except (TypeError, ValueError):
        raise HTTPException(status_code=422, detail="La valeur ou l'unité du quota est invalide")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/quota/{quota_id}")
def update_quota_route(quota_id: int, data: dict = Body(...)):
    """Mettre à jour uniquement la limite du quota."""
    try:
        quota_limite = get_quota_limit_saisie(data)
        updated = update_quota(quota_id, quota_limite)
        if not updated:
            raise HTTPException(status_code=404, detail="Quota non trouvé")

        return {
            "status": "ok",
            "message": "Quota mis à jour avec succès",
            "data": {
                "quota_limite": quota_limite,
                "formatted_quota_limite": format_bytes(quota_limite),
            },
        }
    except HTTPException:
        raise
    except (TypeError, ValueError):
        raise HTTPException(status_code=422, detail="La valeur ou l'unité du quota est invalide")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/quota/{quota_id}")
def delete_quota_route(quota_id: int):
    """Supprimer une quota"""
    try:
        deleted = delete_quota(quota_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Quota non trouvé")
        return {"status": "ok", "message": "Quota supprimé avec succès"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
