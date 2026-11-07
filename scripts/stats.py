# Statistiques de réaction des marchés aux surprises macro (2019-2026)
# Pour chaque indicateur et chaque sens de surprise (réel > prévu, < prévu, = prévu),
# probabilité que chaque actif termine la séance en hausse, et variation moyenne.
import json, re, os, datetime as dt, collections
D = os.environ.get("DATA", "data")

px = json.load(open(os.path.join(D, "px.json")))
ASSETS = [a for a in ["^GSPC", "^IXIC", "^GDAXI", "EURUSD=X", "GC=F", "^TNX", "BTC-USD"] if a in px]

# séries : date (UTC) -> clôture, et liste triée des dates de séance
series = {}
for s in ASSETS:
    m = {}
    for t, o, c in px[s]:
        m[dt.datetime.utcfromtimestamp(t).date()] = c
    series[s] = (m, sorted(m))

def num(v):
    v = (v or "").replace("&nbsp;", "").strip()
    if not v or v == "N/A": return None
    neg = v.startswith("(") and v.endswith(")")
    v = re.sub(r"[()$,%\s]", "", v); mul = 1
    if v and v[-1].upper() in "KMBT": mul = {"K": 1e3, "M": 1e6, "B": 1e9, "T": 1e12}[v[-1].upper()]; v = v[:-1]
    try: n = float(v) * mul
    except ValueError: return None
    return -n if neg else n

def reaction(sym, day, t):
    """Variation de la séance qui suit la publication (heure Nasdaq = UTC-5 fixe)."""
    m, dates = series[sym]
    h, mi = map(int, t.split(":"))
    utc = dt.datetime(day.year, day.month, day.day, h, mi) + dt.timedelta(hours=5)
    d = utc.date()
    if sym in ("^GSPC", "^IXIC", "^TNX") and utc.hour >= 21: d += dt.timedelta(days=1)   # après la clôture US
    if sym == "^GDAXI" and utc.hour >= 16: d += dt.timedelta(days=1)                      # après la clôture de Francfort
    import bisect
    i = bisect.bisect_left(dates, d)
    if i >= len(dates) or i == 0: return None
    if (dates[i] - d).days > 4: return None
    c, p = m[dates[i]], m[dates[i - 1]]
    return (c - p) / p if p else None

acc = collections.defaultdict(lambda: {"up": [], "down": [], "inline": []})
names = {}; dev = collections.defaultdict(list); unit = {}
for line in open(os.path.join(D, "hist.jsonl")):
    rec = json.loads(line); day = dt.date.fromisoformat(rec["day"]); occ = collections.Counter()
    for r in rec["rows"]:
        base = r["c"] + "|" + r["n"]; k = base + "|" + str(occ[base]); occ[base] += 1
        a, f = num(r["a"]), num(r["f"])
        if a is None or f is None or ":" not in (r["t"] or ""): continue
        cls = "up" if a > f else "down" if a < f else "inline"
        dev[k].append(abs(a - f)); u = re.sub(r"[-+\d.,()$\s]", "", r["a"].replace("&nbsp;", "")); unit[k] = u
        rx = {s: reaction(s, day, r["t"]) for s in ASSETS}
        acc[k][cls].append(rx); names[k] = (r["c"], r["n"])

out = {}
for k, cl in acc.items():
    tot = sum(len(v) for v in cl.values())
    if tot < 8: continue
    dv = sorted(dev[k]); o = {"n": tot, "cls": {}, "ms": dv[len(dv) // 2] if dv else None, "u": unit.get(k, "")}
    for c, lst in cl.items():
        if len(lst) < 4: continue
        a = {}
        for s in ASSETS:
            v = [x[s] for x in lst if x.get(s) is not None]
            if len(v) >= 4:
                a[s] = [round(sum(1 for x in v if x > 0) / len(v) * 100), round(sum(v) / len(v) * 100, 3), len(v)]
        o["cls"][c] = {"n": len(lst), "a": a}
    if o["cls"]: out[k] = o

# taux de hausse "normal" de chaque actif (toutes les séances depuis 2019), pour juger si un signal est réel
base = {}
for sy in ASSETS:
    m, dates = series[sy]; ds = [d for d in dates if d >= dt.date(2019, 1, 1)]
    ch = [(m[b] - m[a]) / m[a] for a, b in zip(ds, ds[1:]) if m[a]]
    base[sy] = round(sum(1 for x in ch if x > 0) / len(ch) * 100)
print("base", base)
json.dump({"from": "2019-01", "to": dt.date.today().strftime("%Y-%m"), "assets": ASSETS, "base": base, "stats": out}, open(os.path.join(D, "stats.json"), "w"), separators=(",", ":"))
print(len(out), "indicateurs")
for k in ["United States|Nonfarm Payrolls|0", "United States|CPI|0", "United States|Core CPI|0", "United States|Initial Jobless Claims|0", "United States|Retail Sales|0", "United States|ISM Manufacturing PMI|0", "Euro Zone|CPI|0"]:
    if k in out:
        print(k, out[k]["n"], {c: (v["n"], v["a"].get("^GSPC"), v["a"].get("EURUSD=X")) for c, v in out[k]["cls"].items()})
