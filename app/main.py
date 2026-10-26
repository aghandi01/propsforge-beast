
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import os, pathlib
from datetime import datetime
from app.core.orchestrator import BeastOrchestrator

app=FastAPI(title="BEAST Live Props Tracker")
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_methods=["*"],allow_headers=["*"])
orch=BeastOrchestrator()
fp=pathlib.Path(__file__).parent/"frontend"/"index.html"

@app.get("/",response_class=HTMLResponse)
def root(): return fp.read_text() if fp.exists() else "<h1>BEAST Live Props</h1>"

@app.get("/health")
def health():
    return {"status":"live_props_tracker","sports":["NBA","NFL","MLB","NHL","CFB","WNBA"],"features":["today_filter","live_tracker","live_props_over_under"],"time":datetime.utcnow().isoformat()}

@app.get("/api/v1/live-status")
async def live_status(sport: str = Query("NBA"), time_filter: str = Query("today")):
    r=await orch.run(sport, time_filter)
    return {
        "sport":sport.upper(),
        "time_filter":time_filter,
        "prizepicks_live":r["live_breakdown"]["prizepicks_live"],
        "today_filtered":r["live_breakdown"]["today_filtered"],
        "odds_api_live":r["live_breakdown"]["odds_api_live"],
        "agents":r["agents"],
        "live":True
    }

@app.get("/api/v1/games/live")
async def live_games(sport: str = Query("NBA"), time_filter: str = Query("today")):
    games=await orch.get_live_games_with_props(sport, time_filter)
    total_props=sum(len(g.get("live_props",[])) for g in games)
    hitting_over=len([p for g in games for p in g.get("live_props",[]) if p.get("live_stat") and p["live_stat"]>=p["line"]])
    hitting_under=total_props-hitting_over
    return {
        "sport":sport.upper(),
        "time_filter":time_filter,
        "games":games,
        "total_props":total_props,
        "hitting_over":hitting_over,
        "hitting_under":hitting_under,
        "live_count":len([g for g in games if g["is_live"]]),
        "timestamp":datetime.utcnow().isoformat()
    }

@app.get("/api/v1/games/live-props")
async def live_props(sport: str = Query("NBA"), time_filter: str = Query("today")):
    games=await orch.get_live_games_with_props(sport, time_filter)
    total_props=sum(len(g.get("live_props",[])) for g in games)
    hitting_over=len([p for g in games for p in g.get("live_props",[]) if p.get("live_stat") and p["live_stat"]>=p["line"]])
    return {
        "sport":sport.upper(),
        "time_filter":time_filter,
        "games":games,
        "total_props":total_props,
        "hitting_over":hitting_over,
        "hitting_under":total_props-hitting_over,
        "timestamp":datetime.utcnow().isoformat(),
        "note":"Live stats from balldontlie API - add BALLDONTLIE_API_KEY for real-time player stats"
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
