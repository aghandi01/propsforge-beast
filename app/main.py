
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from datetime import datetime
from app.core.orchestrator import BeastOrchestrator

app = FastAPI(title="PropsForge BEAST V3 - 12 Agent Live", version="3.0-pro")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

orch = BeastOrchestrator()

@app.get("/")
def root():
    return {"beast":"online","version":"12-agent live pro","docs":"/docs","health":"/health","live_status":"/api/v1/live-status","generate":"/api/v1/generate-slips-live"}

@app.get("/health")
def health():
    return {"status":"beast_mode","agents":12,"live":True,"time":datetime.utcnow().isoformat()}

@app.get("/api/v1/live-status")
async def live_status():
    result = await orch.run()
    return {
        "prizepicks_live": result["live_breakdown"]["prizepicks_live"],
        "odds_api_live": result["live_breakdown"]["odds_api_live"],
        "odds_key_configured": bool(os.getenv("ODDS_API_KEY")),
        "balldontlie_enabled": bool(os.getenv("BALLDONTLIE_API_KEY")),
        "agents": result["agents"],
        "live": True
    }

@app.post("/api/v1/generate-slips-live")
@app.post("/api/v1/generate-slips")
async def generate(payload: dict = None):
    payload = payload or {}
    sport = payload.get("sport","NBA")
    result = await orch.run(sport)
    return {
        "sport": sport,
        "generated_at": datetime.utcnow().isoformat(),
        "live": True,
        "live_breakdown": result["live_breakdown"],
        "agents_run": result["agents"],
        "slips": result["slips"],
        "message": "12-agent live beast - PrizePicks + FanDuel/DraftKings/Bet365 + Form + DvP"
    }

@app.get("/m")
def mobile():
    return {"open":"/docs for full UI - this beast is live 24/7 on Railway"}
