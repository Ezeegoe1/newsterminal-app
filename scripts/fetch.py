# Mise à jour hebdomadaire des données : nouveaux chiffres macro (Nasdaq) + cours (Yahoo), puis statistiques.
import json, os, time, urllib.request, urllib.parse, datetime as dt
D = os.environ.get("DATA", "data"); H = os.path.join(D, "hist.jsonl")
KEEP = {"United States", "Euro Zone", "Germany", "United Kingdom", "Japan", "China", "Canada"}
UA = {"User-Agent": "NewsTerminal/1.0", "Accept": "application/json"}
done = {json.loads(l)["day"] for l in open(H)}
end = dt.date.today() - dt.timedelta(days=1); d, new = end - dt.timedelta(days=21), 0   # 3 dernières semaines
with open(H, "a") as f:
    while d <= end:
        if d.isoformat() not in done and d.weekday() != 5:
            for attempt in range(2):
                try:
                    u = f"https://api.nasdaq.com/api/calendar/economicevents?date={(d + dt.timedelta(days=1)).isoformat()}"   # date=J+1 -> jour J
                    rows = json.loads(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=20).read())["data"]["rows"] or []
                    rows = [{"t": x["gmt"], "c": x["country"], "n": x["eventName"], "a": x["actual"], "f": x["consensus"], "p": x["previous"]}
                            for x in rows if x["country"] in KEEP and x["consensus"].replace("&nbsp;", "").strip()]
                    f.write(json.dumps({"day": d.isoformat(), "rows": rows}) + "\n"); new += 1; break
                except Exception as e:
                    print(d, "erreur", e); time.sleep(5 * (attempt + 1))
            time.sleep(1)
        d += dt.timedelta(days=1)
print("jours ajoutés :", new)
px = {}
for s in ["^GSPC", "^IXIC", "EURUSD=X", "GC=F", "^TNX", "^GDAXI", "BTC-USD"]:
    for attempt in range(4):
        try:
            u = "https://query1.finance.yahoo.com/v8/finance/chart/" + urllib.parse.quote(s) + f"?period1=1514764800&period2={int(time.time())}&interval=1d"
            r = json.loads(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "NewsTerminal/1.0"}), timeout=30).read())["chart"]["result"][0]
            q = r["indicators"]["quote"][0]
            px[s] = [[t, o, c] for t, o, c in zip(r["timestamp"], q["open"], q["close"]) if c is not None]; print(s, len(px[s])); break
        except Exception as e:
            print(s, "erreur", e); time.sleep(20 * (attempt + 1))
    time.sleep(3)
if len(px) < 5: raise SystemExit("cours indisponibles : statistiques non recalculées")
json.dump(px, open(os.path.join(D, "px.json"), "w"))
