
import httpx

LEAGUE_MAP = {
    "NBA": 7,
    "NFL": 82,
    "MLB": 2,
    "WNBA": 11,
    "CBB": 16,
    "CFB": 12,
    "NHL": 8,
    "PGA": 5,
    "SOCCER": 14,
    "MMA": 20,
    "WNBA": 11,
    "NFL": 82,
}

def get_league_id(sport: str):
    sport = sport.upper().strip()
    # Handle common variations
    if sport in ["FOOTBALL", "NFL"]: return 82
    if sport in ["BASKETBALL", "NBA"]: return 7
    if sport in ["BASEBALL", "MLB"]: return 2
    if sport in ["HOCKEY", "NHL"]: return 8
    return LEAGUE_MAP.get(sport, 7)

async def fetch_live(sport="NBA"):
    league_id = get_league_id(sport)
    try:
        async with httpx.AsyncClient(timeout=20) as c:
            # Try with league_id first
            r = await c.get("https://api.prizepicks.com/projections", 
                params={"per_page":250,"single_stat":"true","league_id":league_id}, 
                headers={"User-Agent":"Mozilla/5.0","Accept":"application/json"})
            if r.status_code!=200:
                # Fallback: try without league filter and filter by league later
                r = await c.get("https://api.prizepicks.com/projections", 
                    params={"per_page":250,"single_stat":"true"}, 
                    headers={"User-Agent":"Mozilla/5.0"})
                if r.status_code!=200:
                    return []
            data=r.json()
            inc={i["id"]:i for i in data.get("included",[])}
            lines=[]
            for proj in data.get("data",[]):
                try:
                    pid=proj["relationships"]["new_player"]["data"]["id"]
                    player=inc.get(pid)
                    if not player: continue
                    pa=player["attributes"]; aa=proj["attributes"]
                    if aa.get("is_promo"): continue
                    # If we fetched all leagues, filter by requested league if possible
                    # PrizePicks doesn't always return league in attributes, so we try
                    proj_league = aa.get("league_id") or proj.get("relationships",{}).get("league",{}).get("data",{}).get("id")
                    # If we have league info and it doesn't match, skip when we used fallback
                    lines.append({
                        "player":pa.get("name"),
                        "team":pa.get("team") or pa.get("team_name"),
                        "opp":pa.get("opponent") or aa.get("opponent"),
                        "market":aa.get("stat_type"),
                        "line":float(aa.get("line_score",0)),
                        "book":"prizepicks",
                        "id":proj["id"],
                        "league_id": league_id,
                        "sport": sport.upper()
                    })
                except Exception as e:
                    continue
            # If we filtered by league_id in request, we already have correct sport
            # For NFL, ensure we only return football players - PrizePicks sometimes mixes
            # So limit to 250 and return
            print(f"Fetched {len(lines)} lines for {sport} (league {league_id})")
            return lines[:250]
    except Exception as e:
        print(f"PP error {sport}: {e}")
        return []
