# Met à jour version.json avec l'empreinte du nouveau fichier de statistiques.
import hashlib, json, datetime as dt
v = json.load(open("version.json"))
v["stats_sha256"] = hashlib.sha256(open("data/stats.json", "rb").read()).hexdigest()
v["stats_date"] = dt.date.today().strftime("%d/%m/%Y")
json.dump(v, open("version.json", "w"), ensure_ascii=False, indent=1)
