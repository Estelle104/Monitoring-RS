from app.crud.salle import get_all_salles, get_salle_by_id, create_salle
from fastapi import APIRouter, HTTPException, Body
# from fastapi import Request

router = APIRouter()
@router.get("/salles")
def list_salles():
    """Récupérer toutes les salles"""
    salles = get_all_salles()
    return {"status": "ok", "data": salles}


@router.get("/salles/{salle_id}")
def get_salle(salle_id: str):
    """Récupérer une salle par son ID"""
    salle = get_salle_by_id(salle_id)
    if not salle:
        raise HTTPException(status_code=404, detail="Salle non trouvée")
    return {"status": "ok", "data": salle}


@router.post("/salles/create")
def create_new_salle(salle: dict = Body(...)):
    """Créer une nouvelle salle"""
    if "salle" not in salle:
        raise HTTPException(status_code=400, detail="Le champ 'salle' est requis")
    
    salle_id = create_salle(salle)
    return {"status": "ok", "data": {"id": salle_id, "salle": salle["salle"]}}