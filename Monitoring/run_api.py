#!/usr/bin/env python3
"""
Démarrage de l'API FastAPI
Lancez avec: python3 run_api.py
"""
import sys
import os

# Ajouter le backend au chemin
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
