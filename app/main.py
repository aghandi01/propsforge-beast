
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import os, pathlib
from datetime import datetime
from app.core.orchestrator import BeastOrchestrator

app=FastAPI(title="BEAST Time Filter + Live Tracker")
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_methods=["*"],allow_headers=["*"])
orch=BeastOrchestrator()
fp=pathlib.Path(__file__).parent/"frontend"/"index.html"

@app.get("/",response_class=HTMLResponse)
def root(): return fp.read_text() if fp.exists() else "<h1>BEAST</h1>"

@app.get("/health")
def health():
    return {"status":"time_filter_live","sports":["NBA","NFL","MLB","NHL","CFB","WNBA"],"features":["today_filter","live_tracker","6_sports"],"time":datetime.utcnow().isoformat()}

@app.get("/api/v1/live-status")
async def live_status(sport: str = Query("NBA"), time_filter: str = Query("today")):
    r=await orch.run(sport, time_filter)
    return {
        "sport":sport.upper(),
        "time_filter":time_filter,
        "prizepicks_live":r["live_breakdown"]["prizepicks_live"],
        "today_filtered":r["live_breakdown"]["today_filtered"],
        "odds_api_live":r["live_breakdown"]["odds_api_live"],
        "odds_key_configured":bool(os.getenv("ODDS_API_KEY")),
        "agents":r["agents"],
        "live":True
    }

@app.get("/api/v1/games/live")
async def live_games(sport: str = Query("NBA")):
    games=await orch.get_live_games(sport)
    return {
        "sport":sport.upper(),
        "games":games,
        "live_count":len([g for g in games if g["is_live"]]),
        "total":len(games),
        "timestamp":datetime.utcnow().isoformat(),
        "note":"Live scores from balldontlie API - add BALLDONTLIE_API_KEY for real live scores"
    }

@app.post("/api/v1/generate-slips-live")
async def gen(payload: dict = None, sport: str = Query("NBA"), time_filter: str = Query("today")):
    payload=payload or {}
    s=payload.get("sport") or sport or "NBA"
    tf=payload.get("time_filter") or time_filter or "today"
    r=await orch.run(s, tf)
    return {"sport":s.upper(),"time_filter":tf,"generated_at":datetime.utcnow().isoformat(),"live":True,"live_breakdown":r["live_breakdown"],"slips":r["slips"]}

@app.get("/api/v1/verify")
async def verify():
    out={}
    for sp in ["NBA","NFL","MLB","NHL","CFB","WNBA"]:
        rr=await orch.run(sp, "today")
        out[sp]=rr["live_breakdown"]
    return {"sports":out,"timestamp":datetime.utcnow().isoformat()}
