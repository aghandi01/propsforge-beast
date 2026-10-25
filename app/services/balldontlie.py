
import os, httpx
async def fetch_form(player_name: str):
    key=os.getenv("BALLDONTLIE_API_KEY","")
    if not key or key.startswith("your_"):
        return {"avg_last5": None, "source":"mock"}
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            # search player
            r=await c.get("https://api.balldontlie.io/nba/v1/players", params={"search":player_name}, headers={"Authorization":key})
            # For now return mock structure - real parsing can be added
            return {"avg_last5": None, "source":"live", "found": r.status_code==200}
    except:
        return {"avg_last5": None, "source":"error"}
