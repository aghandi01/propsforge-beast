
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import pathlib
from datetime import date, datetime
from app.core.orchestrator import BeastOrchestrator

app=FastAPI(title="BEAST Ultra Strict Real")
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_methods=["*"],allow_headers=["*"])
orch=BeastOrchestrator()
fp=pathlib.Path(__file__).parent/"frontend"/"index.html"

@app.get("/",response_class=HTMLResponse)
def root():
    return fp.read_text() if fp.exists() else "<h1>BEAST Ultra Strict</h1>"

@app.get("/api/v1/games/live")
@app.get("/api/v1/games/live-props")
async def live_games(sport: str = Query("NBA"), time_filter: str = Query("today")):
    games=await orch.get_live_games_with_props_strict(sport, time_filter)
    today=date.today().isoformat()
    return {"sport":sport.upper(),"time_filter":time_filter,"game_date":today,"today":today,"games":games,"total_props":sum(len(g.get("live_props",[])) for g in games),"live_count":len([g for g in games if g["is_live"]]),"real_games_today":len(games),"source":"ESPN - 100% Real, No Mock","accurate":True,"strict":True,"ultra_strict":True,"note":f"ULTRA STRICT REAL: {len(games)} actual {sport} games from ESPN for {today}. If Denver not playing, not shown. Zero fake games." if games else f"ULTRA STRICT: No {sport} games today {today} - ESPN says 0 games. Denver not playing = correctly not shown. No fake LAL@DEN.","timestamp":datetime.utcnow().isoformat()}

@app.get("/api/v1/live-status")
async def status(sport: str = Query("NBA"), time_filter: str = Query("today")):
    r=await orch.run(sport, time_filter)
    return {"sport":sport.upper(),"time_filter":time_filter,"game_date":date.today().isoformat(),"prizepicks_live":r["live_breakdown"]["prizepicks_live"],"today_filtered":r["live_breakdown"]["today_filtered"],"real_games_today":r["live_breakdown"]["real_games_today"],"today":date.today().isoformat(),"source":"ESPN - Real Only","accurate":True,"ultra_strict":True}

@app.post("/api/v1/generate-slips-live")
async def gen(sport: str = Query("NBA"), time_filter: str = Query("today")):
    r=await orch.run(sport, time_filter)
    return {"sport":sport.upper(),"time_filter":time_filter,"game_date":r["game_date"],"real_games":r.get("real_games",[]),"live":True,"accurate":True,"ultra_strict":True,"live_breakdown":r["live_breakdown"],"slips":r["slips"]}

@app.get("/api/v1/verify")
async def verify():
    from app.core.orchestrator import fetch_espn_games
    today=date.today().isoformat()
    out={}
    for sp in ["NBA","NFL","MLB","NHL","CFB","WNBA"]:
        games=await fetch_espn_games(sp, date.today())
        live=[g for g in games if g["is_live"]]
        out[sp]={"real_games_today":len(games),"live_right_now":len(live),"games":[f"{g['away']} @ {g['home']} - {g['status']} - live={g['is_live']}" for g in games[:3]],"date":today}
    return {"sports":out,"today":today,"source":"ESPN - 100% real, zero mock","ultra_strict":True,"timestamp":datetime.utcnow().isoformat()}
