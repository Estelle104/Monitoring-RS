from app.crud.machine import get_all_machines, get_machines_sans_quota_machine
from fastapi import APIRouter

router = APIRouter()


@router.get("/machine")
def list_machines():
    """Récupérer toutes les machines"""
    rows = get_all_machines()
    return {"status": "ok", "data": [dict(r) for r in rows]}


@router.get("/machine/sans_quota_machine")
def list_machines_sans_quota_machine():
    """Récupérer les machines sans quota_machine"""
    rows = get_machines_sans_quota_machine()
    return {"status": "ok", "data": [dict(r) for r in rows]}
