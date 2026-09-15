from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.crud.login import (
    get_all_logins, get_login_by_id, get_login_by_username,
    create_login, update_login, delete_login, check_login
)

router = APIRouter()


# ─── Schemas ────────────────────────────────────────
class LoginCreate(BaseModel):
    username: str
    pwd: str
    code: str
    role: str


class LoginUpdate(BaseModel):
    username: Optional[str] = None
    pwd: Optional[str] = None
    code: Optional[str] = None
    role: Optional[str] = None


class LoginCheck(BaseModel):
    username: str
    pwd: str


# ─── Routes ────────────────────────────────────────
@router.get("/logins")
def list_logins():
    """Récupérer tous les logins (sans les mots de passe)"""
    logins = get_all_logins()
    return {"status": "ok", "data": logins}


@router.get("/logins/{login_id}")
def get_login(login_id: int):
    """Récupérer un login par son ID"""
    login = get_login_by_id(login_id)
    if not login:
        raise HTTPException(status_code=404, detail="Login non trouvé")
    return {"status": "ok", "data": login}


@router.post("/logins/create")
def add_login(body: LoginCreate):
    """Créer un nouveau login"""
    try:
        # Vérifier que l'utilisateur n'existe pas déjà
        existing = get_login_by_username(body.username)
        if existing:
            raise HTTPException(status_code=400, detail="Cet utilisateur existe déjà")
        
        login_id = create_login({
            "username": body.username,
            "pwd": body.pwd,
            "code": body.code,
            "role": body.role
        })
        
        return {
            "status": "ok",
            "message": "Login créé avec succès",
            "data": {"id": login_id}
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/logins/{login_id}")
def edit_login(login_id: int, body: LoginUpdate):
    """Mettre à jour un login"""
    try:
        login = get_login_by_id(login_id)
        if not login:
            raise HTTPException(status_code=404, detail="Login non trouvé")
        
        update_data = {}
        if body.username:
            update_data["username"] = body.username
        if body.pwd:
            update_data["pwd"] = body.pwd
        if body.code:
            update_data["code"] = body.code
        if body.role:
            update_data["role"] = body.role
        
        if update_data:
            update_login(login_id, update_data)
        
        return {"status": "ok", "message": "Login mis à jour avec succès"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/logins/{login_id}")
def remove_login(login_id: int):
    """Supprimer un login"""
    try:
        login = get_login_by_id(login_id)
        if not login:
            raise HTTPException(status_code=404, detail="Login non trouvé")
        
        delete_login(login_id)
        return {"status": "ok", "message": "Login supprimé avec succès"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/logins/check")
def verify_login(body: LoginCheck):
    """Vérifier les identifiants de connexion"""
    try:
        result = check_login(body.username, body.pwd)
        if result["status"] == "error":
            raise HTTPException(status_code=401, detail=result["message"])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
