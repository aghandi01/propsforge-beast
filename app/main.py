
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import os, pathlib
from datetime import datetime
from app.core.orchestrator import BeastOrchestrator

app=FastAPI(title="BEAST Debug Fix")
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_methods=["*"],allow_headers=["*"])
orch=BeastOrchestrator()
fp=pathlib.Path(__file__).parent/"frontend"/"index.html"

@app.get("/",response_class=HTMLResponse)
def root(): return fp.read_text() if fp.exists() else "<h1>BEAST Debug</h1>"

@app.get("/health")
def health():
    return {
        "status":"debug_fix",
        "sports":["NBA","NFL","MLB","NHL","CFB","WNBA"],
        "agents":12,
        "env": {
            "ODDS_API_KEY_set": bool(os.getenv("ODDS_API_KEY") and len(os.getenv("ODDS_API_KEY","").strip())>10),
            "ODDS_API_KEY_len": len(os.getenv("ODDS_API_KEY","")) if os.getenv("ODDS_API_KEY") else 0,
            "BALLDONTLIE_API_KEY_set": bool(os.getenv("BALLDONTLIE_API_KEY")),
        },
        "time":datetime.utcnow().isoformat()
    }

@app.get("/api/v1/live-status")
async def live_status(sport: str = Query("NBA")):
    r=await orch.run(sport)
    return {
        "sport":sport.upper(),
        "prizepicks_live":r["live_breakdown"]["prizepicks_live"],
        "odds_api_live":r["live_breakdown"]["odds_api_live"],
        "odds_key_configured": bool(os.getenv("ODDS_API_KEY") and len(os.getenv("ODDS_API_KEY","").strip())>10),
        "odds_key_len": len(os.getenv("ODDS_API_KEY","")) if os.getenv("ODDS_API_KEY") else 0,
        "balldontlie_enabled": bool(os.getenv("BALLDONTLIE_API_KEY")),
        "agents":r["agents"],
        "live":True,
        "debug":"Check Railway logs for PP and ODDS messages"
    }

@app.post("/api/v1/generate-slips-live")
async def gen(payload: dict = None, sport: str = Query(None)):
    payload=payload or {}
    s=payload.get("sport") or sport or "NBA"
    r=await orch.run(s)
    return {"sport":s.upper(),"generated_at":datetime.utcnow().isoformat(),"live":True,"live_breakdown":r["live_breakdown"],"slips":r["slips"]}

@app.get("/api/v1/verify")
async def verify():
    out={}
    for sp in ["NBA","NFL","MLB","NHL","CFB","WNBA"]:
        rr=await orch.run(sp)
        out[sp]=rr["live_breakdown"]["prizepicks_live"]
    return {
        "sports":out,
        "env":{
            "ODDS_API_KEY_set": bool(os.getenv("ODDS_API_KEY")),
            "ODDS_API_KEY_len": len(os.getenv("ODDS_API_KEY","")) if os.getenv("ODDS_API_KEY") else 0,
        },
        "timestamp":datetime.utcnow().isoformat()
    }
