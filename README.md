# Le Terminal — mises à jour

Ce dépôt public sert uniquement à distribuer l'application **Le Terminal** (Android) et ses données.

| Fichier | Rôle |
|---|---|
| `NewsTerminal.apk` | Dernière version de l'application Android |
| `version.json` | Numéro de version, empreinte SHA-256 de l'APK et des statistiques |
| `newsterminal.zip` | Version Mac (serveur + page web) |
| `data/stats.json` | Statistiques achat / vente des annonces macro, recalculées chaque dimanche |
| `data/hist.jsonl` | Historique des chiffres macro depuis 2019 (Nasdaq) |

## Comment l'appli se met à jour
1. Une fois par jour, l'appli lit `version.json`.
2. Si une version plus récente existe, elle télécharge l'APK et vérifie, avant toute installation :
   - l'empreinte SHA-256 annoncée,
   - le nom de l'application (`com.newsterminal.app`),
   - un numéro de version plus élevé,
   - **la même signature** que l'appli installée.
3. Une notification « 🆕 Le Terminal x.y est prêt » apparaît ; Android demande confirmation.

La clé de signature n'est **jamais** dans ce dépôt : personne d'autre que le propriétaire ne peut publier une version acceptée par l'appli.

## Statistiques automatiques
Le workflow *Statistiques hebdomadaires* (onglet **Actions**) ajoute chaque dimanche les chiffres de la semaine, recalcule `data/stats.json` et met à jour `version.json`. L'appli récupère les nouvelles statistiques sans réinstallation.
