
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import pathlib
from datetime import date, datetime
from app.core.orchestrator import BeastOrchestrator

app=FastAPI(title="BEAST Strict")
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_methods=["*"],allow_headers=["*"])
orch=BeastOrchestrator()
fp=pathlib.Path(__file__).parent/"frontend"/"index.html"

@app.get("/",response_class=HTMLResponse)
def root(): return fp.read_text() if fp.exists() else "<h1>BEAST</h1>"

@app.get("/api/v1/games/live")
@app.get("/api/v1/games/live-props")
async def live_games(sport: str = Query("NBA"), time_filter: str = Query("today")):
    games=await orch.get_live_games_with_props_strict(sport, time_filter)
    return {"sport":sport.upper(),"time_filter":time_filter,"game_date":date.today().isoformat(),"today":date.today().isoformat(),"games":games,"total_props":sum(len(g.get("live_props",[])) for g in games),"live_count":len([g for g in games if g["is_live"]]),"strict":True,"note":"STRICT: Only today games. Live filter = only live right now. No fake dates.","timestamp":datetime.utcnow().isoformat()}

@app.get("/api/v1/live-status")
async def status(sport: str = Query("NBA"), time_filter: str = Query("today")):
    r=await orch.run(sport, time_filter)
    return {"sport":sport.upper(),"time_filter":time_filter,"game_date":date.today().isoformat(),"prizepicks_live":r["live_breakdown"]["prizepicks_live"],"today_filtered":r["live_breakdown"]["today_filtered"],"today":date.today().isoformat(),"strict":True}

@app.post("/api/v1/generate-slips-live")
async def gen(sport: str = Query("NBA"), time_filter: str = Query("today")):
    r=await orch.run(sport, time_filter)
    return {"sport":sport.upper(),"time_filter":time_filter,"game_date":r["game_date"],"live":True,"strict":True,"live_breakdown":r["live_breakdown"],"slips":r["slips"]}
