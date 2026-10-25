
import os, httpx
MAP={"NBA":"basketball_nba","NFL":"americanfootball_nfl","MLB":"baseball_mlb","NHL":"icehockey_nhl","CFB":"americanfootball_ncaaf","WNBA":"basketball_wnba"}
async def fetch_live(sport="NBA"):
    key=os.getenv("ODDS_API_KEY","").strip()
    if not key or len(key)<10:
        print("ODDS: No key")
        return []
    sport_key=MAP.get(sport.upper(),"basketball_nba")
    try:
        async with httpx.AsyncClient(timeout=15) as c:
            # First test with h2h which works on free plan
            url=f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds"
            # Try h2h first to verify key works
            r=await c.get(url, params={"apiKey":key,"regions":"us","markets":"h2h","oddsFormat":"american"})
            print(f"ODDS H2H TEST {sport_key} -> {r.status_code} remaining {r.headers.get('x-requests-remaining')} used {r.headers.get('x-requests-used')}")
            if r.status_code!=200:
                print(f"ODDS H2H ERROR: {r.text[:500]}")
                # Try to get error reason
                if r.status_code==401:
                    print("ODDS: Invalid key - get new from the-odds-api.com")
                elif r.status_code==429:
                    print("ODDS: Out of credits - free 500/month exhausted")
                return []
            
            # Key works, now try player props (may need paid plan, but try)
            r2=await c.get(url, params={"apiKey":key,"regions":"us","markets":"player_points,player_rebounds,player_assists,player_pass_yds,player_receiving_yds,player_rush_yds","oddsFormat":"american"})
            print(f"ODDS PLAYER PROPS {sport_key} -> {r2.status_code}")
            if r2.status_code==200:
                books=r2.json()
                lines=[]
                for game in books:
                    for bm in game.get("bookmakers",[]):
                        for mk in bm.get("markets",[]):
                            for o in mk.get("outcomes",[]):
                                lines.append({"player":o.get("description") or o.get("name"),"market":mk["key"],"line":o.get("point"),"price":o.get("price"),"book":bm["key"],"sport":sport.upper()})
                if lines:
                    print(f"ODDS PLAYER PROPS SUCCESS {sport}: {len(lines)} lines")
                    return lines
                else:
                    print(f"ODDS PLAYER PROPS empty for {sport} - free plan does not include player props, using h2h count as proof key works")
                    # Return h2h lines as proof that key works, even though not player props
                    h2h_lines=[]
                    for game in r.json()[:5]:
                        h2h_lines.append({"player":f"{game.get('home_team')} vs {game.get('away_team')}","market":"h2h","line":0,"book":"odds_api","sport":sport.upper(),"note":"h2h (free plan - player props need paid plan)"})
                    return h2h_lines
            else:
                print(f"ODDS PLAYER PROPS ERROR {r2.status_code}: {r2.text[:300]}")
                # Free plan doesn't include player props, return h2h as proof
                return []
    except Exception as e:
        print(f"ODDS EXCEPTION {sport}: {e}")
        return []
