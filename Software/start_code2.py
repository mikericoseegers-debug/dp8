from pathlib import Path
import json
from datetime import date
import urllib.request
from database_wrapper import Database

# -------------------------------
# Parameters voor connectie met de database
# -------------------------------
db = Database(
    host="localhost",
    gebruiker="root",
    wachtwoord="200708s",
    database="attractiepark"
)

# -------------------------------
# Input medewerker
# -------------------------------
personeelsl_id = input("Voer het id van het personeelslid in: ")

# -------------------------------
# Haal personeelslid op
# -------------------------------
db.connect()
select_query = f"SELECT * FROM personeelslid WHERE id = {personeelsl_id}"
personeelslid = db.execute_query(select_query)
db.close()

if not personeelslid:
    print("Geen personeelslid gevonden met dit ID.")
    exit()

personeelslid = personeelslid[0]  # eerste record
print("Naam:", personeelslid["naam"])

# -------------------------------
# Bereken maximale fysieke belasting
# -------------------------------
leeftijd = personeelslid["leeftijd"]

if leeftijd <= 24:
    verlaagde_fysieke_belasting = 25
elif leeftijd <= 50:
    verlaagde_fysieke_belasting = 50
else:
    verlaagde_fysieke_belasting = 20

print("Maximale fysieke belasting:", verlaagde_fysieke_belasting)

# -------------------------------
# Haal onderhoudstaken op
# -------------------------------
db.connect()
select_query = (
    f"SELECT * FROM onderhoudstaak "
    f"WHERE beroepstype = '{personeelslid['beroepstype']}' "
    f"AND bevoegdheid = '{personeelslid['bevoegdheid']}' "
    f"AND afgerond = 0 "
    f"AND fysieke_belasting <= {verlaagde_fysieke_belasting}"
)
onderhoudstaken = db.execute_query(select_query)
db.close()

print(f"{len(onderhoudstaken)} onderhoudstaken gevonden.")

# -------------------------------
# FR8 - Sorteer taken op prioriteit (hoog naar laag)
# -------------------------------
prioriteit_volgorde = {"hoog": 3, "middel": 2, "laag": 1}
onderhoudstaken.sort(key=lambda t: prioriteit_volgorde.get(t["prioriteit"], 0), reverse=True)

# -------------------------------
# FR5 - Totale werktijd niet overschrijden (max. 8 uur)
# -------------------------------
MAX_WERKTIJD = 480  # minuten (8 uur)
dagtaken = []
totaal_tijd = 0

for taak in onderhoudstaken:
    if totaal_tijd + taak["duur"] <= MAX_WERKTIJD:
        dagtaken.append(taak)
        totaal_tijd += taak["duur"]
    else:
        break  # stop als 8 uur bereikt is

# -------------------------------
# FR11 - Pauze toevoegen (30 minuten halverwege)
# -------------------------------
pauze = {"taak": "Pauze", "duur": 30, "prioriteit": "laag"}
halverwege = len(dagtaken) // 2
dagtaken.insert(halverwege, pauze)
totaal_tijd += 30

# -------------------------------
# FR9 - Afsluiten met een lage prioriteitstaak
# -------------------------------
lage_prioriteit_taken = [t for t in onderhoudstaken if t["prioriteit"] == "laag"]
if lage_prioriteit_taken:
    dagtaken.append(lage_prioriteit_taken[0])
    totaal_tijd += lage_prioriteit_taken[0]["duur"]

# -------------------------------
# FR14 - Temperatuur ophalen via Open-Meteo API
# -------------------------------
url = "https://weerlive.nl/api/weerlive_api_v2.php?key=demo&locatie=Amsterdam"

with urllib.request.urlopen(url) as url_data:
    json_string = url_data.read().decode() 
    gegevens = json.loads(json_string)

print(gegevens["liveweer"])
temperatuur = (gegevens["wk_verw"][0]["max_temp"])
print(temperatuur)

print(gegevens["liveweer"])
neerslag = (gegevens["wk_verw"][0]["neersl_perc_dag"])
print(neerslag)

 
if float(temperatuur) > 30:
    dagtaken.append({"taak": "Extra pauze (warm weer)", "duur": 15, "prioriteit": "laag"})
    totaal_tijd += 15
    print("Extra pauze van 15 minuten toegevoegd wegens hitte.")

# -------------------------------
# Bouw dagtakenlijst JSON (enige JSON die we opslaan)
# -------------------------------
dagtakenlijst = {
    "personeelsgegevens": {
        "naam": personeelslid["naam"],
        "leeftijd": personeelslid["leeftijd"],
        "beroepstype": personeelslid["beroepstype"],
        "bevoegdheid": personeelslid["bevoegdheid"],
        "fysieke_belasting": verlaagde_fysieke_belasting
    },
    "weergegevens": {
        "datum": str(date.today()),
        "temperatuur": f"{temperatuur} °C",
        "neerslag": f"{neerslag} mm"
    },
    "dagtaken": dagtaken,
    "totale_duur": totaal_tijd
}

# -------------------------------
# Schrijf JSON-bestand weg (enkel deze)
# -------------------------------
bestandspad = Path(f"dagtakenlijst_personeelslid_{personeelsl_id}.json")
with open(bestandspad, "w", encoding="utf-8") as f:
    json.dump(dagtakenlijst, f, indent=4, ensure_ascii=False)
