
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import os, pathlib
from datetime import datetime
from app.core.orchestrator import BeastOrchestrator

app = FastAPI(title="BEAST V3 Live", version="3.0-pro")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
orch = BeastOrchestrator()
frontend_path = pathlib.Path(__file__).parent / "frontend" / "index.html"

@app.get("/", response_class=HTMLResponse)
def root():
    if frontend_path.exists():
        return frontend_path.read_text()
    return "<h1>BEAST Online - /docs</h1>"

@app.get("/m", response_class=HTMLResponse)
def mobile():
    if frontend_path.exists():
        return frontend_path.read_text()
    return "<h1>BEAST Mobile</h1>"

@app.get("/health")
def health():
    return {"status":"beast_mode","agents":12,"live":True,"time":datetime.utcnow().isoformat()}

@app.get("/api/v1/live-status")
async def live_status():
    result = await orch.run()
    return {"prizepicks_live": result["live_breakdown"]["prizepicks_live"], "odds_api_live": result["live_breakdown"]["odds_api_live"], "odds_key_configured": bool(os.getenv("ODDS_API_KEY")), "balldontlie_enabled": bool(os.getenv("BALLDONTLIE_API_KEY")), "agents": result["agents"], "live": True}

@app.post("/api/v1/generate-slips-live")
@app.post("/api/v1/generate-slips")
async def generate(payload: dict = None):
    payload = payload or {}
    sport = payload.get("sport","NBA")
    result = await orch.run(sport)
    return {"sport": sport, "generated_at": datetime.utcnow().isoformat(), "live": True, "live_breakdown": result["live_breakdown"], "agents_run": result["agents"], "slips": result["slips"]}
