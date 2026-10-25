
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import os, pathlib
from datetime import datetime
from app.core.orchestrator import BeastOrchestrator
app=FastAPI(title="BEAST 6-Sport Final")
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_methods=["*"],allow_headers=["*"])
orch=BeastOrchestrator()
fp=pathlib.Path(__file__).parent/"frontend"/"index.html"
@app.get("/",response_class=HTMLResponse)
def root(): return fp.read_text() if fp.exists() else "<h1>BEAST</h1>"
@app.get("/m",response_class=HTMLResponse)
def mobile(): return fp.read_text() if fp.exists() else "<h1>BEAST Mobile</h1>"
@app.get("/health")
def health(): return {"status":"beast_mode","sports":["NBA","NFL","MLB","NHL","CFB","WNBA"],"agents":12,"live":True,"time":datetime.utcnow().isoformat()}
@app.get("/api/v1/live-status")
async def live_status(sport: str = Query("NBA")):
    r=await orch.run(sport)
    return {"sport":sport.upper(),"prizepicks_live":r["live_breakdown"]["prizepicks_live"],"odds_api_live":r["live_breakdown"]["odds_api_live"],"agents":r["agents"],"live":True}
@app.post("/api/v1/generate-slips-live")
@app.post("/api/v1/generate-slips")
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
    return {"sports":out,"timestamp":datetime.utcnow().isoformat()}
