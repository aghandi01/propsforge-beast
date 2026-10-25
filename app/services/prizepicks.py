
import httpx
MAP={"NBA":7,"NFL":82,"MLB":2,"NHL":8,"CFB":12,"WNBA":11,"CBB":16}
def get_id(s): return MAP.get(s.upper(),7)
async def fetch_live(sport="NBA"):
    lid=get_id(sport)
    try:
        async with httpx.AsyncClient(timeout=20) as c:
            r=await c.get("https://api.prizepicks.com/projections",params={"per_page":250,"single_stat":"true","league_id":lid},headers={"User-Agent":"Mozilla/5.0"})
            if r.status_code!=200:
                r=await c.get("https://api.prizepicks.com/projections",params={"per_page":250,"single_stat":"true"},headers={"User-Agent":"Mozilla/5.0"})
                if r.status_code!=200: return []
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
                    out.append({"player":pa.get("name"),"team":pa.get("team") or "","opp":pa.get("opponent") or aa.get("opponent") or "","market":aa.get("stat_type") or "","line":float(aa.get("line_score",0)),"book":"prizepicks","id":proj["id"],"sport":sport.upper()})
                except: continue
            print(f"PP {sport} {lid}: {len(out)}")
            return out
    except Exception as e:
        print(f"PP err {sport} {e}")
        return []
