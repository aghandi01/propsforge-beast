
import httpx, random

MAP={"NBA":7,"NFL":82,"MLB":2,"NHL":8,"CFB":12,"WNBA":11}

# Sport-specific mock that matches real players - used as FALLBACK if PrizePicks blocks Railway
MOCK_PLAYERS={
    "NBA":["Nikola Jokic","Luka Doncic","Giannis Antetokounmpo","Jayson Tatum","Stephen Curry","Kevin Durant","Anthony Davis","LeBron James","Joel Embiid","Shai Gilgeous-Alexander","Donovan Mitchell","Devin Booker","Anthony Edwards","Damian Lillard","Ja Morant"],
    "NFL":["Patrick Mahomes","Josh Allen","Jalen Hurts","Justin Jefferson","Tyreek Hill","Christian McCaffrey","Travis Kelce","Justin Herbert","Lamar Jackson","Joe Burrow","Stefon Diggs","Davante Adams","Cooper Kupp","Bijan Robinson","Jamar Chase"],
    "MLB":["Shohei Ohtani","Aaron Judge","Mookie Betts","Ronald Acuna Jr","Mike Trout","Juan Soto","Fernando Tatis Jr","Gunnar Henderson","Corbin Carroll","Yordan Alvarez","Freddie Freeman","Bobby Witt Jr","Julio Rodriguez","Jose Ramirez","Kyle Tucker"],
    "NHL":["Connor McDavid","Nathan MacKinnon","Auston Matthews","Leon Draisaitl","David Pastrnak","Nikita Kucherov","Cale Makar","Sidney Crosby","Artemi Panarin","Connor Bedard","Matthew Tkachuk","Mikko Rantanen","Jack Hughes","Kirill Kaprizov","Igor Shesterkin"],
    "CFB":["Caleb Williams","Marvin Harrison Jr","Drake Maye","Bo Nix","Michael Penix Jr","Jayden Daniels","Malik Nabers","Rome Odunze","Brock Bowers","Quinn Ewers","Carson Beck","Shedeur Sanders","Travis Hunter","Emeka Egbuka","Ollie Gordon"],
    "WNBA":["Aja Wilson","Breanna Stewart","Caitlin Clark","Angel Reese","Sabrina Ionescu","Kelsey Plum","Alyssa Thomas","Napheesa Collier","Jackie Young","Chelsea Gray","Jewell Loyd","Nneka Ogwumike","Aliyah Boston","Kelsey Mitchell","Dearica Hamby"],
}

MOCK_MARKETS={
    "NBA":["Points","Rebounds","Assists","3PT Made","PRA"],
    "NFL":["Pass Yards","Rush Yards","Receiving Yards","Receptions","Pass TDs"],
    "MLB":["Hits","Home Runs","RBIs","Strikeouts","Total Bases"],
    "NHL":["Goals","Assists","Shots on Goal","Points","Saves"],
    "CFB":["Pass Yards","Rush Yards","Receiving Yards","Pass TDs","Receptions"],
    "WNBA":["Points","Rebounds","Assists","3PT Made","PRA"],
}

def get_id(s): return MAP.get(s.upper(),7)

async def fetch_live(sport="NBA"):
    sport=sport.upper()
    lid=get_id(sport)
    headers={
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept":"application/json",
        "Referer":"https://app.prizepicks.com/",
        "Origin":"https://app.prizepicks.com",
    }
    # Try live first
    for url in [
        f"https://api.prizepicks.com/projections?per_page=250&single_stat=true&league_id={lid}",
        "https://api.prizepicks.com/projections?per_page=250&single_stat=true",
    ]:
        try:
            async with httpx.AsyncClient(timeout=15) as c:
                r=await c.get(url, headers=headers)
                print(f"PP LIVE TRY {sport} {url} -> {r.status_code}")
                if r.status_code!=200: continue
                data=r.json()
                inc={i["id"]:i for i in data.get("included",[])}
                out=[]
                for proj in data.get("data",[]):
                    try:
                        pid=proj["relationships"]["new_player"]["data"]["id"]
                        pl=inc.get(pid)
                        if not pl: continue
                        pa=pl["attributes"]; aa=proj["attributes"]
                        if aa.get("is_promo"): continue
                        out.append({"player":pa.get("name"),"team":pa.get("team") or "","opp":pa.get("opponent") or "","market":aa.get("stat_type") or "","line":float(aa.get("line_score",0) or 0),"book":"prizepicks","sport":sport})
                    except: continue
                if out:
                    print(f"PP LIVE SUCCESS {sport}: {len(out)}")
                    return out[:250]
        except Exception as e:
            print(f"PP LIVE FAIL {sport}: {e}")
            continue
    
    # FALLBACK: Sport-specific mock so buttons work even when PrizePicks blocks Railway IP
    print(f"PP FALLBACK MOCK for {sport} - Railway IP blocked, using sport-specific mock")
    players=MOCK_PLAYERS.get(sport, MOCK_PLAYERS["NBA"])
    markets=MOCK_MARKETS.get(sport, MOCK_MARKETS["NBA"])
    out=[]
    for i, p in enumerate(players):
        for m in markets[:2]:
            out.append({
                "player":p,
                "team":["DEN","LAL","GSW","MIA","DAL","KC","BUF","PHI","ATL","LAD"][i%10],
                "opp":["LAL","BOS","MIA","DEN","NYK","SF","BAL","DAL","HOU","CHC"][i%10],
                "market":m,
                "line":round(random.uniform(8.5,28.5),1),
                "book":"prizepicks (mock fallback - PP blocked)",
                "sport":sport,
                "is_mock":True
            })
    return out[:200]
