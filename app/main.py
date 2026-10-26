
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import pathlib
from datetime import date, datetime
from app.core.orchestrator import BeastOrchestrator, get_denver_today, fetch_espn_games

app=FastAPI(title="BEAST Denver Timezone Fix")
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_methods=["*"],allow_headers=["*"])
orch=BeastOrchestrator()
fp=pathlib.Path(__file__).parent/"frontend"/"index.html"

@app.get("/",response_class=HTMLResponse)
def root():
    return fp.read_text() if fp.exists() else "<h1>BEAST Denver Fix</h1>"

@app.get("/api/v1/games/live")
@app.get("/api/v1/games/live-props")
async def live_games(sport: str = Query("NBA"), time_filter: str = Query("today")):
    games=await orch.get_live_games_with_props_strict(sport, time_filter)
    denver_today=get_denver_today()
    today=denver_today.isoformat()
    # Also get UTC date for comparison
    utc_today=datetime.utcnow().date().isoformat()
    return {"sport":sport.upper(),"time_filter":time_filter,"game_date":today,"today":today,"denver_date":today,"utc_date":utc_today,"games":games,"total_props":sum(len(g.get("live_props",[])) for g in games),"live_count":len([g for g in games if g["is_live"]]),"real_games_today":len(games),"source":"ESPN - Denver timezone","accurate":True,"timezone_fix":True,"note":f"TIMEZONE FIX: Denver date {today} (UTC date {utc_today}). {len(games)} real games. User in Denver says live games exist - now using Denver date.","timestamp":datetime.utcnow().isoformat()}

@app.get("/api/v1/live-status")
async def status(sport: str = Query("NBA"), time_filter: str = Query("today")):
    r=await orch.run(sport, time_filter)
    denver_today=get_denver_today()
    return {"sport":sport.upper(),"time_filter":time_filter,"game_date":denver_today.isoformat(),"denver_date":denver_today.isoformat(),"utc_date":datetime.utcnow().date().isoformat(),"prizepicks_live":r["live_breakdown"]["prizepicks_live"],"today_filtered":r["live_breakdown"]["today_filtered"],"real_games_today":r["live_breakdown"]["real_games_today"],"today":denver_today.isoformat(),"source":"ESPN - Denver timezone","timezone_fix":True}

@app.post("/api/v1/generate-slips-live")
async def gen(sport: str = Query("NBA"), time_filter: str = Query("today")):
    r=await orch.run(sport, time_filter)
    denver_today=get_denver_today()
    return {"sport":sport.upper(),"time_filter":time_filter,"game_date":denver_today.isoformat(),"denver_date":denver_today.isoformat(),"real_games":r.get("real_games",[]),"live":True,"timezone_fix":True,"live_breakdown":r["live_breakdown"],"slips":r["slips"]}

@app.get("/api/v1/verify")
async def verify():
    denver_today=get_denver_today()
    utc_today=datetime.utcnow().date().isoformat()
    out={}
    for sp in ["NBA","NFL","MLB","NHL","CFB","WNBA"]:
        games=await fetch_espn_games(sp, denver_today)
        live=[g for g in games if g["is_live"]]
        out[sp]={"real_games_today":len(games),"live_right_now":len(live),"games":[f"{g['away']} @ {g['home']} - {g['status']} - live={g['is_live']}" for g in games[:3]],"date":denver_today.isoformat()}
    return {"sports":out,"today":denver_today.isoformat(),"denver_date":denver_today.isoformat(),"utc_date":utc_today,"source":"ESPN - Denver timezone fix","timezone_fix":True,"note":f"Denver today is {denver_today}, UTC today is {utc_today}. User is in Denver, so using Denver date.","timestamp":datetime.utcnow().isoformat()}
