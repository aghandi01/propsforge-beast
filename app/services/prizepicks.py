
import httpx
async def fetch_live():
    try:
        async with httpx.AsyncClient(timeout=20) as c:
            r = await c.get("https://api.prizepicks.com/projections", params={"per_page":250,"single_stat":"true","league_id":7}, headers={"User-Agent":"Mozilla/5.0"})
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
                    lines.append({"player":pa.get("name"),"team":pa.get("team"),"opp":pa.get("opponent") or aa.get("opponent"),"market":aa.get("stat_type"),"line":float(aa.get("line_score",0)),"book":"prizepicks","id":proj["id"]})
                except: continue
            return lines
    except Exception as e:
        print(f"PP error {e}")
        return []
