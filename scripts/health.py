# Contrôle hebdomadaire des sources : une source qui ne répond pas 3 semaines de suite est écartée par l'appli.
import json, hashlib, urllib.request, urllib.parse, concurrent.futures as cf
F = json.load(open("data/feeds.json"))["feeds"]
try: H = json.load(open("data/feeds_health.json"))
except Exception: H = {}
def ok(f):
    try:
        r = urllib.request.urlopen(urllib.request.Request(urllib.parse.quote(f["url"], safe=":/?&=+%,;@!$*()'~#"), headers={"User-Agent": "NewsTerminal/1.0"}), timeout=25)
        b = r.read(400000).decode("utf-8", "ignore")
        return r.status == 200 and ("<item" in b or "<entry" in b or '"feed"' in b)
    except Exception: return False
with cf.ThreadPoolExecutor(8) as ex: res = dict(zip([f["name"] for f in F], ex.map(ok, F)))
H = {n: (0 if good else H.get(n, 0) + 1) for n, good in res.items()}
json.dump(H, open("data/feeds_health.json", "w"), ensure_ascii=False, indent=1, sort_keys=True)
v = json.load(open("version.json")); h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
v["health_sha256"] = h("data/feeds_health.json"); v["feeds_sha256"] = h("data/feeds.json")
json.dump(v, open("version.json", "w"), ensure_ascii=False, indent=1)
bad = [n for n, k in H.items() if k]; print(len(F), "sources ;", len(bad), "en panne cette semaine :", ", ".join(f"{n} ({H[n]} sem.)" for n in bad))
