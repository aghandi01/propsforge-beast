
import os, httpx
MAP={"NBA":"basketball_nba","NFL":"americanfootball_nfl","MLB":"baseball_mlb","NHL":"icehockey_nhl","CFB":"americanfootball_ncaaf","WNBA":"basketball_wnba"}
async def fetch_live(sport="NBA"):
    key=os.getenv("ODDS_API_KEY","").strip()
    if not key or key.startswith("your_") or len(key)<10:
        print(f"ODDS: No valid key configured (len {len(key) if key else 0})")
        return []
    sport_key=MAP.get(sport.upper(),"basketball_nba")
    try:
        async with httpx.AsyncClient(timeout=20) as c:
            url=f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds"
            r=await c.get(url, params={"apiKey":key,"regions":"us","markets":"player_points,player_rebounds,player_assists,player_threes,player_pass_yds,player_rush_yds,player_receiving_yds","oddsFormat":"american"})
            print(f"ODDS {sport_key} status {r.status_code} remaining {r.headers.get('x-requests-remaining')} used {r.headers.get('x-requests-used')}")
            if r.status_code!=200:
                print(f"ODDS ERROR {r.status_code}: {r.text[:500]}")
                return []
            books=r.json()
            lines=[]
            for game in books:
                for bm in game.get("bookmakers",[]):
                    for mk in bm.get("markets",[]):
                        for o in mk.get("outcomes",[]):
                            lines.append({"player":o.get("description") or o.get("name") or "","market":mk["key"],"line":o.get("point"),"price":o.get("price"),"book":bm["key"],"sport":sport.upper()})
            print(f"ODDS SUCCESS {sport} {len(lines)} lines")
            return lines
    except Exception as e:
        print(f"ODDS exception {sport}: {e}")
        return []
