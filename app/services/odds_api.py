
import os, httpx
async def fetch_live():
    key=os.getenv("ODDS_API_KEY","")
    if not key or key.startswith("your_"): return []
    try:
        async with httpx.AsyncClient(timeout=20) as c:
            url="https://api.the-odds-api.com/v4/sports/basketball_nba/odds"
            r=await c.get(url, params={"apiKey":key,"regions":"us","markets":"player_points,player_rebounds,player_assists,player_threes","oddsFormat":"american"})
            if r.status_code!=200: return []
            books=r.json()
            lines=[]
            for game in books:
                for bm in game.get("bookmakers",[]):
                    for mk in bm.get("markets",[]):
                        for o in mk.get("outcomes",[]):
                            lines.append({"player":o.get("description") or o.get("name"),"market":mk["key"],"line":o.get("point"),"price":o.get("price"),"book":bm["key"],"game":f"{game.get('away_team')} @ {game.get('home_team')}"})
            return lines
    except Exception as e:
        print(f"Odds error {e}")
        return []
