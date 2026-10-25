
import os, httpx

SPORT_MAP = {
    "NBA": "basketball_nba",
    "NFL": "americanfootball_nfl",
    "MLB": "baseball_mlb",
    "NHL": "icehockey_nhl",
    "CBB": "basketball_ncaab",
    "CFB": "americanfootball_ncaaf",
    "WNBA": "basketball_wnba",
    "SOCCER": "soccer_epl",
}

async def fetch_live(sport="NBA"):
    key=os.getenv("ODDS_API_KEY","")
    if not key or key.startswith("your_"): return []
    sport_key = SPORT_MAP.get(sport.upper(), "basketball_nba")
    try:
        async with httpx.AsyncClient(timeout=20) as c:
            url=f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds"
            r=await c.get(url, params={"apiKey":key,"regions":"us","markets":"player_points,player_rebounds,player_assists,player_threes,player_pass_yds,player_rush_yds","oddsFormat":"american"})
            if r.status_code!=200:
                print(f"Odds {sport_key} {r.status_code}: {r.text[:200]}")
                return []
            books=r.json()
            lines=[]
            for game in books:
                for bm in game.get("bookmakers",[]):
                    for mk in bm.get("markets",[]):
                        for o in mk.get("outcomes",[]):
                            lines.append({"player":o.get("description") or o.get("name"),"market":mk["key"],"line":o.get("point"),"price":o.get("price"),"book":bm["key"],"game":f"{game.get('away_team')} @ {game.get('home_team')}","sport":sport.upper()})
            print(f"Odds {sport} fetched {len(lines)} lines")
            return lines
    except Exception as e:
        print(f"Odds error {sport}: {e}")
        return []
