
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import os, pathlib
from datetime import datetime
from app.core.orchestrator import BeastOrchestrator

app=FastAPI(title="BEAST Working 6-Sport")
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_methods=["*"],allow_headers=["*"])
orch=BeastOrchestrator()
fp=pathlib.Path(__file__).parent/"frontend"/"index.html"

@app.get("/",response_class=HTMLResponse)
def root(): return fp.read_text() if fp.exists() else "<h1>BEAST</h1>"

@app.get("/health")
def health():
    return {"status":"working_6_sport","sports":["NBA","NFL","MLB","NHL","CFB","WNBA"],"agents":12,"time":datetime.utcnow().isoformat(),
            "env":{"ODDS_API_KEY_set":bool(os.getenv("ODDS_API_KEY")),"ODDS_API_KEY_len":len(os.getenv("ODDS_API_KEY") or "")}}

@app.get("/api/v1/live-status")
async def live_status(sport: str = Query("NBA")):
    r=await orch.run(sport)
    # Check if mock fallback was used
    is_mock = any(p.get("is_mock") for slip in r["slips"] for p in slip["picks"]) if r["slips"] else False
    return {
        "sport":sport.upper(),
        "prizepicks_live":r["live_breakdown"]["prizepicks_live"],
        "odds_api_live":r["live_breakdown"]["odds_api_live"],
        "odds_key_configured":bool(os.getenv("ODDS_API_KEY")),
        "odds_key_len":len(os.getenv("ODDS_API_KEY") or ""),
        "is_mock_fallback": is_mock,
        "note": "If prizepicks_live shows 200 with mock fallback, Railway IP is blocked by PrizePicks Cloudflare - buttons still work with sport-specific players" if is_mock else "Live PrizePicks",
        "agents":r["agents"],
        "live":True
    }

@app.post("/api/v1/generate-slips-live")
async def gen(payload: dict = None, sport: str = Query(None)):
    payload=payload or {}
    s=payload.get("sport") or sport or "NBA"
    r=await orch.run(s)
    is_mock = any(p.get("is_mock") for slip in r["slips"] for p in slip["picks"]) if r["slips"] else False
    return {"sport":s.upper(),"generated_at":datetime.utcnow().isoformat(),"live":True,"is_mock_fallback":is_mock,"live_breakdown":r["live_breakdown"],"slips":r["slips"]}

@app.get("/api/v1/verify")
async def verify():
    out={}
    for sp in ["NBA","NFL","MLB","NHL","CFB","WNBA"]:
        rr=await orch.run(sp)
        out[sp]={"count":rr["live_breakdown"]["prizepicks_live"],"mock":any(p.get("is_mock") for slip in rr["slips"] for p in slip["picks"]) if rr["slips"] else False}
    return {"sports":out,"env":{"ODDS_API_KEY_set":bool(os.getenv("ODDS_API_KEY")),"ODDS_API_KEY_len":len(os.getenv("ODDS_API_KEY") or "")},"timestamp":datetime.utcnow().isoformat()}
