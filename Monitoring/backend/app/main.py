from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import salle, vlan, firewall, login, rx, quota, type_user, machine
from app.services import network_rx
import asyncio

# Créer l'application FastAPI
app = FastAPI(
    title="Monitoring API",
    description="API pour le monitoring réseau et firewall",
    version="1.0.0"
)

# Configuration CORS pour accepter les requêtes du frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure les routes du firewall
app.include_router(firewall.router, tags=["Firewall"])

# Inclure les routes VLAN / Salle / Port
app.include_router(salle.router, prefix="/api", tags=["Salle"])
app.include_router(vlan.router, prefix="/api", tags=["VLAN"])
app.include_router(login.router, prefix="/api", tags=["Login"])

app.include_router(quota.router, prefix="/api", tags=["Quota"])
app.include_router(type_user.router, prefix="/api", tags=["Type user"])
app.include_router(machine.router, prefix="/api", tags=["Machine"])
# WebSocket route for netmetrics
app.include_router(rx.router)


@app.on_event("startup")
async def start_netpoller():
    # start background poller without blocking startup
    try:
        asyncio.create_task(network_rx.poll_source())
    except Exception:
        pass


# Route de santé
@app.get("/health")
def health():
    return {"status": "ok", "message": "API en ligne"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
