
import httpx
MAP={"NBA":7,"NFL":82,"MLB":2,"NHL":8,"CFB":12,"WNBA":11}
async def fetch_live(sport="NBA"):
    sport=sport.upper()
    lid=MAP.get(sport,7)
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            r=await c.get("https://api.prizepicks.com/projections",params={"per_page":250,"single_stat":"true","league_id":lid},headers={"User-Agent":"Mozilla/5.0","Referer":"https://app.prizepicks.com/"})
            if r.status_code!=200:
                return []
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
            return out[:200]
    except:
        return []
