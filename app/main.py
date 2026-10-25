
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import os, pathlib
from datetime import datetime
from app.core.orchestrator import BeastOrchestrator

app = FastAPI(title="PropsForge BEAST V3 - Original Pro UI", version="3.0-pro")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
orch = BeastOrchestrator()
frontend_path = pathlib.Path(__file__).parent / "frontend" / "index.html"

@app.get("/", response_class=HTMLResponse)
def root():
    return frontend_path.read_text() if frontend_path.exists() else "<h1>BEAST Online</h1>"

@app.get("/m", response_class=HTMLResponse)
def mobile():
    return frontend_path.read_text() if frontend_path.exists() else "<h1>BEAST Mobile</h1>"

@app.get("/health")
def health():
    return {"status":"beast_mode","agents":12,"live":True,"ui":"original_pro","time":datetime.utcnow().isoformat()}

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

# Keep compat endpoints that original UI might call
@app.get("/api/v1/slips")
async def slips_compat():
    result = await orch.run()
    return {"slips": result["slips"]}

@app.post("/api/generate")
async def gen_compat(payload: dict = None):
    payload = payload or {}
    result = await orch.run(payload.get("sport","NBA"))
    return {"slips": result["slips"], "live_breakdown": result["live_breakdown"]}
