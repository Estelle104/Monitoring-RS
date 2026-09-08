from app.crud.type_user import get_type_user_by_id, get_all_type_users, get_type_users_sans_quota
from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/type_user")
def list_type_users():
    """Récupérer tous les type_user"""
    rows = get_all_type_users()
    return {"status": "ok", "data": [dict(r) for r in rows]}


@router.get("/type_user/sans_quota")
def list_type_users_sans_quota():
    """Récupérer les type_user qui n'ont pas encore de quota associé"""
    rows = get_type_users_sans_quota()
    return {"status": "ok", "data": [dict(r) for r in rows]}


@router.get("/type_user/{type_user_id}")
def get_type_user(type_user_id: str):
    """Récupérer une type_user par son ID"""
    type_user = get_type_user_by_id(type_user_id)
    if not type_user:
        raise HTTPException(status_code=404, detail="type_user non trouvée")
    return {"status": "ok", "data": type_user}