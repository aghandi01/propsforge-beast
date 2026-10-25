
import httpx, os

MAP={"NBA":7,"NFL":82,"MLB":2,"NHL":8,"CFB":12,"WNBA":11,"CBB":16,"SOCCER":14}
def get_id(s): return MAP.get(s.upper(),7)

async def fetch_live(sport="NBA"):
    lid=get_id(sport)
    headers={
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept":"application/json, text/plain, */*",
        "Accept-Language":"en-US,en;q=0.9",
        "Referer":"https://app.prizepicks.com/",
        "Origin":"https://app.prizepicks.com",
        "Sec-Fetch-Site":"same-site",
        "Sec-Fetch-Mode":"cors",
    }
    urls_to_try=[
        f"https://api.prizepicks.com/projections?per_page=250&single_stat=true&league_id={lid}",
        f"https://api.prizepicks.com/projections?per_page=250&single_stat=true&league_id={lid}&state_code=CO",
        "https://api.prizepicks.com/projections?per_page=250&single_stat=true",
    ]
    for url in urls_to_try:
        try:
            async with httpx.AsyncClient(timeout=25, follow_redirects=True) as c:
                r=await c.get(url, headers=headers)
                print(f"PP try {url} -> {r.status_code} len {len(r.text)}")
                if r.status_code!=200:
                    continue
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
                        # Filter by league if we got all leagues
                        if "league_id" not in url:
                            # Try to keep only requested sport by checking player league if available
                            # For now accept all but add sport tag
                            pass
                        out.append({
                            "player":pa.get("name") or pa.get("display_name"),
                            "team":pa.get("team") or pa.get("team_name") or "",
                            "opp":pa.get("opponent") or aa.get("opponent") or "",
                            "market":aa.get("stat_type") or aa.get("stat_display_name") or "",
                            "line":float(aa.get("line_score",0) or 0),
                            "book":"prizepicks",
                            "id":proj["id"],
                            "sport":sport.upper()
                        })
                    except Exception as e:
                        continue
                if len(out)>0:
                    print(f"PP SUCCESS {sport} {lid}: {len(out)} lines from {url}")
                    return out[:250]
        except Exception as e:
            print(f"PP error {sport} url {url}: {e}")
            continue
    print(f"PP FAILED all urls for {sport}")
    return []
