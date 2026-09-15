from datetime import date
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.crud.histo_quota import get_histo_quota_kpis, get_histo_quota_list

router = APIRouter()


# Récupère l'historique de consommation + filtre dynamique + pagination
@router.get("/histo-quota")
def list_histo_quota(
    etu: Optional[int] = Query(None, description="Numéro étudiant"),
    date_from: Optional[date] = Query(None, description="Date de début (YYYY-MM-DD)"),
    date_to: Optional[date] = Query(None, description="Date de fin (YYYY-MM-DD)"),
    consumption_op: Optional[str] = Query(None, description="Filtre consommation: sup ou inf"),
    consumption_value_go: Optional[float] = Query(None, description="Valeur de consommation en Go"),
    page: int = Query(1, ge=1, description="Page"),
    per_page: int = Query(20, ge=1, le=100, description="Nombre de lignes par page")
):
    """
    Liste l'historique de consommation.

    - Sans filtre etu: retourne les lignes brutes.
    - Avec filtre etu: retourne la consommation totale par étudiant.
    - Avec date_from/date_to: limite la période.
    """
    try:
        rows = get_histo_quota_list(
            etu=etu,
            date_from=date_from,
            date_to=date_to,
            consumption_op=consumption_op,
            consumption_value_go=consumption_value_go,
            page=page,
            per_page=per_page,
        )
        total_rows = rows[0]["total_rows"] if rows else 0
        return {
            "status": "ok",
            "mode": "aggregate" if etu is not None else "raw",
            "data": rows,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total_rows": total_rows,
                "total_pages": max((total_rows + per_page - 1) // per_page, 1) if total_rows else 1,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/histo-quota/kpis")
def histo_quota_kpis(
    reference_day: Optional[date] = Query(None, description="Jour de référence (YYYY-MM-DD). Par défaut: hier")
):
    """Retourne les KPI de consommation pour le jour précédent."""
    try:
        result = get_histo_quota_kpis(reference_day=reference_day)
        return {"status": "ok", "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
